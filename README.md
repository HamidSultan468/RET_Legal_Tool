# RET Legal Tools

Internal Streamlit web app for RET Legal, bundling two tools behind one sidebar:

1. **Document Ingestion Tool** – upload scanned PDFs/images and run OCR to extract text (with a low-confidence flag for lines that need manual review).
2. **CanLII Research Tool** – search Canadian court case law via the [CanLII API](https://www.canlii.org/en/info/api.html).

---

## 1. Project Structure

```
RET_Legal_Tool/
├── main.py                     # App entry point — run this with Streamlit
├── requirements.txt            # Python dependencies
├── packages.txt                # System packages needed on Streamlit Cloud (tesseract, poppler)
├── .env.example                # Template for environment variables (copy to .env)
├── .env                        # Your real secrets — NEVER commit or share this file
├── .streamlit/
│   └── config.toml             # Theme/colors for the app
├── tools/                      # Code actually used by main.py
│   ├── document_ingestion.py   # OCR tool logic (this is the live/active version)
│   └── canlii_research.py      # CanLII search tool logic (this is the live/active version)
├── CanLII_Tool/                # OLDER/legacy prototype of the CanLII tool (not imported by main.py)
│   ├── canlii_client.py
│   └── canlii_page.py
└── Ingestion_Tool/             # OLDER/legacy scratch folder for OCR experiments (not used by main.py)
    ├── inputs/                 # Sample test files
    ├── outputs/                # (empty)
    └── scripts/ingest_ocr.py   # Empty file, unused
```

**Important:** Only `main.py` + the `tools/` folder are actually run by the app. `CanLII_Tool/` and `Ingestion_Tool/` are old/leftover work — safe to ignore unless you're specifically asked to look at them. If something behaves unexpectedly, check `tools/document_ingestion.py` and `tools/canlii_research.py` first.

---

## 2. Requirements

- **Python 3.10+**
- **Tesseract OCR** (needed by the Document Ingestion Tool)
- **Poppler** (needed by `pdf2image` to convert PDF pages to images)

### Installing system dependencies

**Windows:**
- Tesseract: download installer from https://github.com/UB-Mannheim/tesseract/wiki, install it, then add the install folder (e.g. `C:\Program Files\Tesseract-OCR`) to your PATH.
- Poppler: download from https://github.com/oschwartz10612/poppler-windows/releases, unzip it, and add its `bin` folder to your PATH.

**macOS:**
```bash
brew install tesseract poppler
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

(`packages.txt` lists these same two packages — that file is only used by Streamlit Community Cloud to auto-install them there.)

---

## 3. Setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd RET_Legal_Tool

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env         # macOS/Linux
copy .env.example .env       # Windows
```

Then open `.env` and add your CanLII API key:

```
CANLII_API_KEY=your_actual_api_key_here
```

Get a key by registering at https://www.canlii.org/en/info/api.html. If you don't have a key yet, the CanLII Research Tool will still load — it will just ask you to paste a key into a sidebar box instead.

**Do not commit `.env` or share it with anyone.** It's already listed in `.gitignore`, but double-check before zipping up the project to send to someone.

---

## 4. Running the App

```bash
streamlit run main.py
```

This opens the app in your browser, usually at `http://localhost:8501`. Use the sidebar to switch between "Document Ingestion Tool" and "CanLII Research Tool".

---

## 5. How Each Tool Works

### Document Ingestion Tool (`tools/document_ingestion.py`)
1. Upload one or more PDF/JPG/PNG files.
2. Each PDF page is rendered to an image at 150 DPI (kept low intentionally to fit memory limits on free hosting tiers) and OCR'd one page at a time with Tesseract.
3. Results are shown as a table (Source File, Page, Text, Confidence, Low Confidence flag) and can be downloaded as CSV.
4. Lines with average OCR confidence below 60% are flagged `"YES"` under "Low Confidence" — check the "Show only low-confidence lines" box to review just those.

### CanLII Research Tool (`tools/canlii_research.py`)
1. Reads `CANLII_API_KEY` from `.env` (or asks for it in the sidebar if missing).
2. Pick a court/database from the dropdown and a result count, then click Search.
3. Results are pulled from `GET /caseBrowse/en/{database}/`; clicking "View Full Details" on a case calls `GET /caseBrowse/en/{database}/{caseId}/` for extra metadata (date, docket number).
4. Each result links out to the case's public page on canlii.org.

---

## 6. Debugging Guide

### App won't start / `ModuleNotFoundError`
- You probably haven't activated the virtual environment or installed dependencies. Run:
  ```bash
  pip install -r requirements.txt
  ```

### `TesseractNotFoundError` or OCR silently fails
- Tesseract isn't installed or isn't on your PATH. Verify with:
  ```bash
  tesseract --version
  ```
  If that fails, reinstall Tesseract and make sure its folder is on PATH (Windows) or reinstall via brew/apt.
- If Tesseract is installed somewhere Python can't find, add this near the top of `tools/document_ingestion.py`:
  ```python
  pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
  ```

### PDF upload fails / `PDFInfoNotInstalledError` / `Unable to get page count`
- Poppler isn't installed or isn't on PATH. Verify with:
  ```bash
  pdftoppm -v
  ```
  If this command isn't found, install/reinstall Poppler and check PATH (see Section 2).

### CanLII search returns `API Error: 401` or `403`
- Your API key is missing, wrong, or expired. Check `.env` has `CANLII_API_KEY=...` with no quotes and no extra spaces, then restart the app (env vars are only read once at startup via `load_dotenv()`).

### CanLII search returns `API Error: 429`
- You've hit CanLII's rate limit. Wait a bit and lower "Number of Results", or reduce how often you're calling the API while testing.

### "No response received from the API" / network errors
- Check your internet connection, and confirm `https://api.canlii.org` isn't blocked by a firewall/VPN. Requests time out after 10 seconds (`tools/canlii_research.py`) — a slow network will show as a failure, not a hang.

### App runs but styling looks broken / sidebar colors missing
- Custom CSS is injected in `main.py` — check the browser console for errors, and confirm you're running `main.py` directly (not one of the files inside `tools/`, `CanLII_Tool/`, or `Ingestion_Tool/`).

### Large PDFs are slow or the app crashes/restarts (especially on free hosting)
- OCR processes one page at a time by design to control memory use. If it's still too slow/heavy, lower `PDF_DPI` in `tools/document_ingestion.py` (currently `150`) — lower DPI = faster and lighter, but less accurate OCR.

### General debugging tips
- Run `streamlit run main.py` from a terminal (not double-clicking a file) so you can see the full error traceback.
- Streamlit auto-reloads on file save — if changes don't seem to apply, check the terminal for a Python syntax/import error, or manually refresh the browser tab.
- To reset local state (e.g. weird cached CanLII sidebar API key issues), stop the app (`Ctrl+C`) and restart it.

---

## 7. Notes for Whoever Is Debugging This

- The two folders `CanLII_Tool/` and `Ingestion_Tool/` at the project root are earlier drafts/experiments and are **not wired into the running app** — `main.py` only ever imports from the `tools/` package. Don't spend time debugging those unless told to.
- `Ingestion_Tool/scripts/ingest_ocr.py` is an empty file (0 bytes) — it's a stub that was never finished.
- If you're given this project as a zip/folder instead of a git clone, double check whether a real `.env` file (with a live API key inside) got included by mistake, and ask the sender for a fresh key if so.
