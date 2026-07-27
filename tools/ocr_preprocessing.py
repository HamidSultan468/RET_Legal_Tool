"""
Shared image preprocessing + Tesseract configuration for the OCR tools.

Used by both the live Streamlit tool (tools/document_ingestion.py) and the
standalone batch script (Ingestion_Tool/scripts/ingest_ocr.py) so the two
never drift out of sync.
"""

import numpy as np
import pytesseract
from PIL import Image, ImageFilter

# Tesseract's own docs recommend 300-400 DPI for reliable recognition, with
# diminishing/negative returns above that (over-smoothed strokes, larger
# artifacts). Pages are rendered and OCR'd one at a time (see
# document_ingestion.py), so peak memory is bounded by a single page's size,
# not the document's page count -- a single page at 400 DPI is still well
# under 100MB, comfortably inside a 1GB budget.
PDF_DPI = 400

# oem 3: LSTM + legacy engine combined (Tesseract's most accurate mode).
# psm 6: assume a single uniform block of text. After deskewing, a scanned
# document page is exactly that; the default psm 3 (fully automatic layout
# detection) tends to over- or under-segment noisy scans into spurious
# blocks and drop text at block boundaries.
PSM_PRIMARY = 6
# psm 4: single column of text of variable sizes. Used only as a fallback
# (see run_ocr) for the pages primary segmentation handles badly -- multi-
# paragraph or ragged-margin scans where psm 6's "one block" assumption
# merges lines that should stay separate.
PSM_FALLBACK = 4
# psm 3: fully automatic layout detection, Tesseract's own default. Used as
# a safety-net candidate against the untouched raw page image (see
# run_ocr) -- on pages where preprocessing hurts more than it helps, or
# where the page mixes regions (e.g. a UI chrome strip above a table)
# that psm 6/4's block assumptions don't fit, this recovers the result
# a completely unprocessed pipeline would have gotten.
PSM_AUTO = 3
TESSERACT_CONFIG = f"--oem 3 --psm {PSM_PRIMARY}"

# Below this average word confidence, a page is considered mis-segmented
# rather than genuinely low-quality, and is worth retrying under psm 4.
RETRY_CONFIDENCE_THRESHOLD = 55

# Tesseract's LSTM model is trained on text with a ~30-33px cap height,
# which corresponds to roughly 300 DPI on a standard page. Below this
# width a page's characters are too small for reliable recognition, so
# it's upscaled before OCR.
MIN_OCR_WIDTH_PX = 2000


def _otsu_threshold(gray_array: np.ndarray) -> int:
    """Otsu's method: pick the threshold that best separates ink from
    background by maximizing between-class variance."""
    hist, _ = np.histogram(gray_array, bins=256, range=(0, 256))
    total = gray_array.size
    sum_total = np.dot(np.arange(256), hist)

    sum_bg = 0.0
    weight_bg = 0.0
    best_thresh = 128
    best_variance = -1.0

    for t in range(256):
        weight_bg += hist[t]
        if weight_bg == 0:
            continue
        weight_fg = total - weight_bg
        if weight_fg == 0:
            break
        sum_bg += t * hist[t]
        mean_bg = sum_bg / weight_bg
        mean_fg = (sum_total - sum_bg) / weight_fg
        between_variance = weight_bg * weight_fg * (mean_bg - mean_fg) ** 2
        if between_variance > best_variance:
            best_variance = between_variance
            best_thresh = t

    return best_thresh


def _estimate_skew_angle(gray_image: Image.Image) -> float:
    """Estimate skew in degrees via a projection-profile search: on a
    correctly-rotated page, horizontal text lines line up into sharp
    peaks/valleys in the row-wise ink count, so the right angle is the one
    that maximizes the variance of that profile. Runs on a small thumbnail
    (skew angle is scale-invariant) so the search stays fast.
    """
    thumb = gray_image.copy()
    thumb.thumbnail((1000, 1000))
    arr = np.asarray(thumb, dtype=np.uint8)
    thresh = _otsu_threshold(arr)
    binary_img = Image.fromarray(((arr < thresh) * 255).astype(np.uint8))

    def profile_variance(angle: float) -> float:
        rotated = binary_img.rotate(
            angle, resample=Image.BILINEAR, expand=False, fillcolor=0
        )
        row_sums = np.asarray(rotated, dtype=np.float64).sum(axis=1)
        return float(row_sums.var())

    best_angle = 0.0
    best_score = profile_variance(0.0)

    # Coarse pass across a wide range, then refine around the best hit.
    for angle in np.arange(-10.0, 10.5, 1.0):
        if angle == 0.0:
            continue
        score = profile_variance(angle)
        if score > best_score:
            best_score, best_angle = score, angle

    for angle in np.arange(best_angle - 1.0, best_angle + 1.05, 0.1):
        score = profile_variance(angle)
        if score > best_score:
            best_score, best_angle = score, angle

    return best_angle


def _upscale_if_small(gray: Image.Image) -> Image.Image:
    """Scan/photo sources are often below Tesseract's effective working
    resolution (low-res phone camera, small scan setting). Upscaling before
    OCR -- rather than letting Tesseract work on undersized glyphs -- makes
    a measurable difference on these pages; sharp/high-res inputs pass
    through unchanged.
    """
    if gray.width >= MIN_OCR_WIDTH_PX:
        return gray
    scale = MIN_OCR_WIDTH_PX / gray.width
    new_size = (MIN_OCR_WIDTH_PX, round(gray.height * scale))
    return gray.resize(new_size, resample=Image.Resampling.LANCZOS)


def preprocess_image(img: Image.Image) -> Image.Image:
    """Grayscale -> denoise -> upscale -> illumination-normalize -> sharpen
    -> deskew.

    Tuned for phone/scanner captures (uneven lighting, slight rotation,
    sensor noise), which is the dominant source of documents fed into this
    tool (see the CamScanner sample in Ingestion_Tool/inputs).

    Deliberately stops short of hard binarization. A single page-wide
    black/white threshold cannot tell a genuine faint artifact (a scan
    line, a light table gridline, a shadow band) from real background --
    on a real sample in this repo it turned a faint horizontal artifact
    into a solid black bar through "2026-04-04", corrupting the date.
    Tesseract's LSTM engine (oem 3) is trained on antialiased glyphs and
    does its own adaptive thresholding internally, so it's handed enhanced
    grayscale instead. See run_ocr(), which also OCRs the untouched raw
    page and keeps whichever result scores higher confidence -- so this
    preprocessing can only help, never hurt, a given page.
    """
    gray = img.convert("L")

    # Median filter knocks out isolated sensor/JPEG-artifact noise pixels
    # before anything else runs, so later steps (skew detection, Otsu) see
    # a cleaner signal instead of fitting to noise.
    gray = gray.filter(ImageFilter.MedianFilter(size=3))
    gray = _upscale_if_small(gray)

    # Flatten uneven lighting (shadows, vignetting from phone scans) by
    # dividing out a heavily blurred version of the page as an estimate of
    # the local background, before thresholding. Plain global Otsu alone
    # loses text in shadowed corners on camera scans.
    background = gray.filter(ImageFilter.GaussianBlur(radius=25))
    gray_arr = np.asarray(gray, dtype=np.float32)
    bg_arr = np.asarray(background, dtype=np.float32)
    normalized_arr = np.clip((gray_arr / np.maximum(bg_arr, 1.0)) * 255, 0, 255)
    normalized = Image.fromarray(normalized_arr.astype(np.uint8))

    # Unsharp mask re-crisps character stroke edges that illumination
    # normalization and any upscaling soften, giving Otsu a sharper
    # ink/background boundary to threshold against.
    normalized = normalized.filter(
        ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)
    )

    angle = _estimate_skew_angle(normalized)
    if abs(angle) >= 0.1:
        normalized = normalized.rotate(
            angle, resample=Image.BICUBIC, expand=True, fillcolor=255
        )

    return normalized


def _average_confidence(ocr_data: dict) -> float:
    confs = [int(c) for c in ocr_data["conf"] if c not in ("-1", -1)]
    return sum(confs) / len(confs) if confs else 0.0


def run_ocr(img: Image.Image, raw_img: Image.Image) -> dict:
    """Run Tesseract against both the preprocessed page and the untouched
    raw page, and keep whichever result scores highest confidence.

    Pages that segment cleanly under the default psm 6 (the common case
    after preprocessing) OCR once against the preprocessed image. Pages
    that come back low-confidence are retried under psm 4, recovering
    pages where the "single block" assumption behind psm 6 mis-splits
    columns or paragraphs.

    The winner of that pair is then compared against the raw page OCR'd
    under psm 3 (Tesseract's own auto-layout default). This is the
    guardrail against preprocessing making a page worse: a real sample in
    this repo (a clean digital screenshot, not a noisy paper scan) scored
    80.6 average confidence completely untouched vs. 66.4 through the full
    preprocessing pipeline, because denoising/normalizing/sharpening a
    page that wasn't degraded in the first place just adds artifacts.
    Comparing against the raw pass means preprocessing can only win or
    tie, never lose, regardless of which failure mode a given page hits.
    """
    primary = pytesseract.image_to_data(
        img, config=f"--oem 3 --psm {PSM_PRIMARY}", output_type=pytesseract.Output.DICT
    )
    best = primary
    if _average_confidence(primary) < RETRY_CONFIDENCE_THRESHOLD:
        fallback = pytesseract.image_to_data(
            img, config=f"--oem 3 --psm {PSM_FALLBACK}", output_type=pytesseract.Output.DICT
        )
        if _average_confidence(fallback) > _average_confidence(best):
            best = fallback

    raw_result = pytesseract.image_to_data(
        raw_img.convert("L"), config=f"--oem 3 --psm {PSM_AUTO}", output_type=pytesseract.Output.DICT
    )
    if _average_confidence(raw_result) > _average_confidence(best):
        best = raw_result

    return best
