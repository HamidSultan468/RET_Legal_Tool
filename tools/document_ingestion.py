import streamlit as st
import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path
from PIL import Image
import pandas as pd
import gc
import os
import uuid


def _ocr_lines(img, source_name, page_num, confidence_threshold):
    """Run OCR on a single page image and return extracted line rows."""
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    n_boxes = len(ocr_data['text'])
    line_text = ""
    line_confidences = []
    rows = []

    for i in range(n_boxes):
        word = ocr_data['text'][i].strip()
        conf = int(ocr_data['conf'][i]) if ocr_data['conf'][i] != '-1' else -1

        if word == "":
            if line_text:
                avg_conf = sum(line_confidences) / len(line_confidences) if line_confidences else 0
                rows.append({
                    "Source File": source_name,
                    "Page": page_num,
                    "Text": line_text.strip(),
                    "Confidence": round(avg_conf, 1),
                    "Low Confidence": "YES" if avg_conf < confidence_threshold else ""
                })
                line_text = ""
                line_confidences = []
            continue

        line_text += word + " "
        if conf >= 0:
            line_confidences.append(conf)

    if line_text:
        avg_conf = sum(line_confidences) / len(line_confidences) if line_confidences else 0
        rows.append({
            "Source File": source_name,
            "Page": page_num,
            "Text": line_text.strip(),
            "Confidence": round(avg_conf, 1),
            "Low Confidence": "YES" if avg_conf < confidence_threshold else ""
        })

    return rows


def run():
    st.markdown(
        '<div class="app-header"><h1>📄 Document Ingestion Tool</h1>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.write("Upload scanned client documents (PDF or images) to extract text with OCR.")

    CONFIDENCE_THRESHOLD = 60
    # 150 DPI keeps OCR accuracy usable while staying well under the 1GB
    # RAM limit on Streamlit Community Cloud's free tier.
    PDF_DPI = 150

    with st.container(border=True):
        uploaded_files = st.file_uploader(
            "Upload files (PDF, JPG, PNG)",
            type=["pdf", "jpg", "jpeg", "png"],
            accept_multiple_files=True
        )

    if uploaded_files:
        all_rows = []

        for uploaded_file in uploaded_files:
            st.subheader(f"Processing: {uploaded_file.name}")
            file_bytes = uploaded_file.read()

            # Use a unique temp filename so multiple files never collide
            temp_path = f"temp_{uuid.uuid4().hex}_{uploaded_file.name}"

            try:
                with open(temp_path, "wb") as f:
                    f.write(file_bytes)

                if uploaded_file.name.lower().endswith(".pdf"):
                    try:
                        page_count = pdfinfo_from_path(temp_path)["Pages"]
                    except Exception as e:
                        st.error(f"Error reading PDF: {e}")
                        page_count = 0

                    # Render and OCR one page at a time so memory usage stays
                    # flat regardless of document length (see PDF_DPI note above).
                    for page_num in range(1, page_count + 1):
                        page_images = convert_from_path(
                            temp_path, dpi=PDF_DPI, first_page=page_num, last_page=page_num
                        )
                        img = page_images[0]
                        all_rows.extend(_ocr_lines(img, uploaded_file.name, page_num, CONFIDENCE_THRESHOLD))
                        img.close()
                        del img, page_images
                        gc.collect()
                else:
                    img = Image.open(temp_path)
                    all_rows.extend(_ocr_lines(img, uploaded_file.name, 1, CONFIDENCE_THRESHOLD))
                    img.close()
                    del img
                    gc.collect()

            finally:
                # Always clean up the temp file, even if an error occurred above
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        if all_rows:
            df = pd.DataFrame(all_rows)
            st.success(f"OCR complete. {len(df)} lines extracted.")

            low_conf_count = (df["Low Confidence"] == "YES").sum()
            st.warning(f"{low_conf_count} lines flagged as low confidence (below {CONFIDENCE_THRESHOLD}%).")

            show_only_low_conf = st.checkbox("Show only low-confidence lines (need manual review)")
            display_df = df[df["Low Confidence"] == "YES"] if show_only_low_conf else df

            st.dataframe(display_df, use_container_width=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download Results as CSV",
                data=csv,
                file_name="ocr_results.csv",
                mime="text/csv",
                type="primary",
            )
    else:
        st.info("Please upload one or more files to begin.")
