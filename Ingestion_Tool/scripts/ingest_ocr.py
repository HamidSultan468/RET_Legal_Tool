"""
ingest_ocr.py

Standalone batch OCR script: reads every PDF/JPG/PNG in
Ingestion_Tool/inputs/, runs the same preprocessing + OCR pipeline used by
the live Document Ingestion Tool (tools/ocr_preprocessing.py), and writes
one combined CSV of extracted lines to Ingestion_Tool/outputs/ocr_results.csv.

Run from the repo root:
    python Ingestion_Tool/scripts/ingest_ocr.py
"""

import csv
import gc
import sys
from pathlib import Path

from pdf2image import convert_from_path, pdfinfo_from_path
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
INGESTION_TOOL_DIR = SCRIPT_DIR.parent
REPO_ROOT = INGESTION_TOOL_DIR.parent
INPUTS_DIR = INGESTION_TOOL_DIR / "inputs"
OUTPUTS_DIR = INGESTION_TOOL_DIR / "outputs"
OUTPUT_CSV = OUTPUTS_DIR / "ocr_results.csv"

# Reuse the exact same preprocessing/config as the Streamlit tool.
sys.path.insert(0, str(REPO_ROOT))
from tools.ocr_preprocessing import PDF_DPI, preprocess_image, run_ocr  # noqa: E402

CONFIDENCE_THRESHOLD = 60
SUPPORTED_SUFFIXES = {".pdf", ".jpg", ".jpeg", ".png"}


def _ocr_lines(img, source_name, page_num):
    """Preprocess and run OCR on a single page image, returning extracted line rows."""
    processed = preprocess_image(img)
    ocr_data = run_ocr(processed, img)

    n_boxes = len(ocr_data["text"])
    line_text = ""
    line_confidences = []
    rows = []

    def flush():
        nonlocal line_text, line_confidences
        if line_text:
            avg_conf = sum(line_confidences) / len(line_confidences) if line_confidences else 0
            rows.append({
                "Source File": source_name,
                "Page": page_num,
                "Text": line_text.strip(),
                "Confidence": round(avg_conf, 1),
                "Low Confidence": "YES" if avg_conf < CONFIDENCE_THRESHOLD else "",
            })
            line_text = ""
            line_confidences = []

    for i in range(n_boxes):
        word = ocr_data["text"][i].strip()
        conf = int(ocr_data["conf"][i]) if ocr_data["conf"][i] != "-1" else -1

        if word == "":
            flush()
            continue

        line_text += word + " "
        if conf >= 0:
            line_confidences.append(conf)

    flush()
    return rows


def process_file(file_path: Path):
    print(f"Processing: {file_path.name}")
    all_rows = []

    if file_path.suffix.lower() == ".pdf":
        try:
            page_count = pdfinfo_from_path(str(file_path))["Pages"]
        except Exception as e:
            print(f"  Error reading PDF: {e}")
            return all_rows

        for page_num in range(1, page_count + 1):
            page_images = convert_from_path(
                str(file_path), dpi=PDF_DPI, first_page=page_num, last_page=page_num
            )
            img = page_images[0]
            all_rows.extend(_ocr_lines(img, file_path.name, page_num))
            img.close()
            del img, page_images
            gc.collect()
    else:
        img = Image.open(file_path)
        all_rows.extend(_ocr_lines(img, file_path.name, 1))
        img.close()
        del img
        gc.collect()

    return all_rows


def main():
    if not INPUTS_DIR.exists():
        print(f"Inputs folder not found: {INPUTS_DIR}")
        return

    files = sorted(
        f for f in INPUTS_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_SUFFIXES
    )
    if not files:
        print(f"No PDF/JPG/PNG files found in {INPUTS_DIR}")
        return

    all_rows = []
    for file_path in files:
        all_rows.extend(process_file(file_path))

    if not all_rows:
        print("No text extracted.")
        return

    OUTPUTS_DIR.mkdir(exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)

    low_conf_count = sum(1 for r in all_rows if r["Low Confidence"] == "YES")
    print(f"OCR complete. {len(all_rows)} lines extracted -> {OUTPUT_CSV}")
    print(f"{low_conf_count} lines flagged as low confidence (below {CONFIDENCE_THRESHOLD}%).")


if __name__ == "__main__":
    main()
