"""
Document Ingestion Tool.

Two-stage extraction. A PDF that already carries a text layer (anything
produced digitally -- e-filed documents, exported affidavits, Word/InDesign
output) is read straight from that layer: exact characters, instant, and no
system dependencies. Only pages with no usable text layer -- true scans and
photographs -- are rendered to images and pushed through Tesseract, which is
slow, lossy, and needs Tesseract + Poppler installed.

Running the text-layer pass first matters in practice: the previous build
OCR'd every page unconditionally, which meant a 17-page e-filed PDF took
minutes and came back with OCR errors in text that could have been read
perfectly for free.
"""

import gc
import io

import pandas as pd
import streamlit as st
from PIL import Image

from tools import ui

# Below this many characters, a page's "text layer" is almost certainly
# incidental -- a header stamp, a page number, or the scanner's own watermark
# on an otherwise image-only page -- so the page is sent to OCR instead.
MIN_TEXT_LAYER_CHARS = 40

CONFIDENCE_THRESHOLD = 60


def _ocr_status():
    """Report whether the OCR path can actually run on this machine.

    Checked up front so the tool can say so plainly instead of failing
    halfway through a document with a raw TesseractNotFoundError.
    """
    try:
        import pytesseract

        pytesseract.get_tesseract_version()
    except Exception:
        return False, "Tesseract OCR is not installed or not on this machine's PATH."

    try:
        import pdf2image  # noqa: F401
    except Exception:
        return False, "The pdf2image package is not installed."

    return True, ""


def _rows_from_text_layer(text, source_name, page_num):
    """Split a page's embedded text layer into one row per line.

    Confidence is left empty rather than set to 100: these characters are read
    directly out of the file, so there is no recognition step to be confident
    about, and filling in a fake score would make OCR rows harder to trust.
    """
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            rows.append(
                {
                    "Source File": source_name,
                    "Page": page_num,
                    "Text": line,
                    "Method": "Text layer",
                    "Confidence": None,
                    "Low Confidence": "",
                }
            )
    return rows


def _rows_from_ocr(img, source_name, page_num):
    """Preprocess and OCR a single page image, returning one row per line."""
    from tools.ocr_preprocessing import preprocess_image, run_ocr

    processed = preprocess_image(img)
    ocr_data = run_ocr(processed, img)

    rows = []
    line_text = ""
    line_confidences = []

    def flush():
        if not line_text:
            return
        avg = sum(line_confidences) / len(line_confidences) if line_confidences else 0
        rows.append(
            {
                "Source File": source_name,
                "Page": page_num,
                "Text": line_text.strip(),
                "Method": "OCR",
                "Confidence": round(avg, 1),
                "Low Confidence": "YES" if avg < CONFIDENCE_THRESHOLD else "",
            }
        )

    for i in range(len(ocr_data["text"])):
        word = ocr_data["text"][i].strip()
        raw_conf = ocr_data["conf"][i]
        conf = int(raw_conf) if str(raw_conf) != "-1" else -1

        if word == "":
            flush()
            line_text = ""
            line_confidences = []
            continue

        line_text += word + " "
        if conf >= 0:
            line_confidences.append(conf)

    flush()
    return rows


def _process_pdf(file_bytes, source_name, ocr_ready, progress_cb):
    """Text layer first, OCR only for the pages that need it."""
    import pypdf

    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    page_texts = []
    for page in reader.pages:
        try:
            page_texts.append(page.extract_text() or "")
        except Exception:
            page_texts.append("")

    total = len(page_texts)
    scanned_pages = [
        i + 1 for i, t in enumerate(page_texts) if len(t.strip()) < MIN_TEXT_LAYER_CHARS
    ]

    rows = []
    for i, text in enumerate(page_texts):
        page_num = i + 1
        if page_num not in scanned_pages:
            rows.extend(_rows_from_text_layer(text, source_name, page_num))
            progress_cb(page_num, total)

    skipped = []
    if scanned_pages and ocr_ready:
        from pdf2image import convert_from_bytes

        for page_num in scanned_pages:
            try:
                images = convert_from_bytes(
                    file_bytes,
                    dpi=_pdf_dpi(),
                    first_page=page_num,
                    last_page=page_num,
                )
            except Exception as e:
                skipped.append((page_num, str(e)))
                progress_cb(page_num, total)
                continue

            img = images[0]
            rows.extend(_rows_from_ocr(img, source_name, page_num))
            img.close()
            del img, images
            gc.collect()
            progress_cb(page_num, total)
    elif scanned_pages:
        skipped = [(p, "OCR unavailable") for p in scanned_pages]

    return rows, total, scanned_pages, skipped


def _pdf_dpi():
    from tools.ocr_preprocessing import PDF_DPI

    return PDF_DPI


def run():
    ui.page_head(
        "Tool 01",
        "Document Ingestion",
        "Upload scanned bundles, affidavits or exhibits to extract their text. "
        "Digital pages are read directly from the file; scanned pages are put "
        "through OCR with a per-line confidence score.",
    )

    ocr_ready, ocr_reason = _ocr_status()

    if not ocr_ready:
        ui.banner(
            "warn",
            f"<b>OCR is unavailable.</b> {ocr_reason} Digital PDFs will still "
            "extract perfectly — only scanned or photographed pages need OCR, "
            "and those will be listed as skipped.",
        )

    with st.container(border=True):
        st.markdown('<div class="card-title">Upload</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "PDF, JPG or PNG — multiple files allowed",
            type=["pdf", "jpg", "jpeg", "png"],
            accept_multiple_files=True,
        )

    if not uploaded_files:
        ui.hint(
            "Nothing uploaded yet. Text-based PDFs process in seconds; scanned "
            "pages take roughly 2–5 seconds each because every page is "
            "deskewed and OCR'd individually."
        )
        return

    total_files = len(uploaded_files)
    ui.banner(
        "ok",
        f"<b>{total_files} file{'s' if total_files > 1 else ''} ready.</b> "
        "Review the list above, then run the extraction.",
    )

    if not st.button("Extract text", type="primary"):
        return

    all_rows = []
    all_scanned = []
    all_skipped = []
    page_total = 0

    progress = st.progress(0.0, text="Starting…")

    for idx, uploaded_file in enumerate(uploaded_files):
        name = uploaded_file.name
        file_bytes = uploaded_file.read()

        def progress_cb(page, total, _idx=idx, _name=name):
            done = (_idx + (page / max(total, 1))) / total_files
            progress.progress(
                min(done, 1.0), text=f"{_name} — page {page} of {total}"
            )

        try:
            if name.lower().endswith(".pdf"):
                rows, pages, scanned, skipped = _process_pdf(
                    file_bytes, name, ocr_ready, progress_cb
                )
                all_rows.extend(rows)
                page_total += pages
                all_scanned.extend((name, p) for p in scanned)
                all_skipped.extend((name, p, r) for p, r in skipped)
            else:
                page_total += 1
                if ocr_ready:
                    img = Image.open(io.BytesIO(file_bytes))
                    all_rows.extend(_rows_from_ocr(img, name, 1))
                    img.close()
                    gc.collect()
                    all_scanned.append((name, 1))
                else:
                    all_skipped.append((name, 1, "OCR unavailable"))
                progress_cb(1, 1)
        except Exception as e:
            ui.banner("err", f"<b>{name}</b> could not be processed: {e}")

    progress.empty()

    if not all_rows:
        ui.banner(
            "err",
            "<b>No text extracted.</b> These pages carry no text layer, and OCR "
            "could not run on them. See the note above.",
        )
        _render_skipped(all_skipped)
        return

    df = pd.DataFrame(all_rows)
    ocr_rows = df[df["Method"] == "OCR"]
    low_conf = int((df["Low Confidence"] == "YES").sum())

    st.markdown("### Results")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        ui.stat("Files", total_files)
    with c2:
        ui.stat("Pages", page_total)
    with c3:
        ui.stat("Lines extracted", f"{len(df):,}")
    with c4:
        ui.stat(
            "Need review",
            low_conf,
            tone="warn" if low_conf else "ok",
        )

    st.write("")

    if len(ocr_rows) == 0:
        ui.banner(
            "ok",
            "<b>Every page had a text layer.</b> All text was read directly "
            "from the files, so it is character-exact — no OCR was needed.",
        )
    else:
        avg_conf = ocr_rows["Confidence"].mean()
        ui.banner(
            "info",
            f"<b>{len(ocr_rows):,} lines came from OCR</b> across "
            f"{len({s for s in all_scanned})} scanned page(s), averaging "
            f"{avg_conf:.1f}% confidence. "
            f"{low_conf} line(s) fell below {CONFIDENCE_THRESHOLD}% and are "
            "flagged for manual review.",
        )

    _render_skipped(all_skipped)

    tab_table, tab_text = st.tabs(["Table", "Full text"])

    with tab_table:
        only_low = st.checkbox("Show only lines flagged for review")
        view = df[df["Low Confidence"] == "YES"] if only_low else df
        if view.empty:
            ui.hint("No lines are flagged for review.")
        else:
            st.dataframe(view, width="stretch", hide_index=True)

    with tab_text:
        joined = _as_plain_text(df)
        st.text_area(
            "Extracted text",
            joined,
            height=420,
            label_visibility="collapsed",
        )

    st.write("")
    d1, d2, _ = st.columns([1, 1, 2])
    with d1:
        st.download_button(
            "Download CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="ret_extraction.csv",
            mime="text/csv",
            type="primary",
        )
    with d2:
        st.download_button(
            "Download text",
            _as_plain_text(df).encode("utf-8"),
            file_name="ret_extraction.txt",
            mime="text/plain",
        )


def _render_skipped(skipped):
    if not skipped:
        return
    unavailable = [s for s in skipped if s[2] == "OCR unavailable"]
    errored = [s for s in skipped if s[2] != "OCR unavailable"]

    if unavailable:
        listing = ", ".join(f"{n} p.{p}" for n, p, _ in unavailable[:12])
        more = f" and {len(unavailable) - 12} more" if len(unavailable) > 12 else ""
        ui.banner(
            "warn",
            f"<b>{len(unavailable)} page(s) skipped — no text layer and OCR is "
            f"unavailable:</b> {listing}{more}.",
        )
    for name, page, reason in errored:
        ui.banner("err", f"<b>{name} p.{page}</b> failed: {reason}")


def _as_plain_text(df):
    out = []
    for (source, page), group in df.groupby(["Source File", "Page"], sort=True):
        out.append(f"===== {source} — page {page} =====")
        out.extend(group["Text"].tolist())
        out.append("")
    return "\n".join(out)
