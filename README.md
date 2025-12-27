**ScheduleToiCal**

- **Purpose:** Convert a photographed or scanned course schedule into an `.ics` calendar file (iCal) using OCR and simple schedule parsing.

**Features**
- **OCR-based:** Uses Tesseract (via `pytesseract`) to extract text from schedule images.
- **Parser:** Extracts course types (lectures, labs, discussions) and exams from the schedule text.
- **ICS export:** Builds recurring calendar events (with alarms) and returns a downloadable `.ics` file.

**Requirements**
- **Python:** Tested with Python 3.11+ (works on macOS with homebrew/pyenv-installed Python).
- **System deps:** `tesseract` binary must be installed and accessible in PATH.
- **Python packages:** Listed in `requirements.txt` (`fastapi`, `uvicorn`, `pytesseract`, `opencv-python`, `icalendar`, `python-multipart`, etc.).

**Quick Install**
1. Create and activate a virtual environment:

```
python3 -m venv .venv
source .venv/bin/activate
```

2. Install Python requirements:

```
pip install -r requirements.txt
```

3. Install Tesseract (macOS example):

```
brew install tesseract
```

**Usage (development / local)**
- Start the FastAPI server (serves an upload endpoint at `/upload`):

```
uvicorn main:app --reload --port 8000
```

- Upload a schedule image via Swagger UI:

Open browser and navigate to:

```
http://localhost:8000/docs
```
Locate the POST `/upload` endpoint, click Try it out, choose a schedule image file, and click execute.

- Upload via `curl`:

```
curl -X POST "http://localhost:8000/upload" -F "file=@/path/to/schedule.jpg" -o schedule.ics
```

The server will:
- run OCR on the uploaded image (`ocr_utils.preprocess_img`)
- parse meetings and exams (`parser.parse_schedule`)
- build an `.ics` file with recurring events (`ics_builder.build_ics`)

The returned file `schedule.ics` can be imported into Calendar apps (Apple Calendar, Google Calendar, etc.).

**Configuration / Notes**
- `main.py` currently sets `term_start` and `term_end` dates in code (example uses Jan–May 2026). Modify these values to match the academic term you are creating events for.
- The parser expects schedule text similar to the University of Wisconsin-Madison style (days like `MWF`, `TR`, times like `8:00 AM - 9:15 AM`, and building names followed by `Room` + room number). See `parser.py` for the parsing regex and `day_map`.
- Building names are mapped to addresses in `ics_builder.py` via `building_address_map` and will be used as the `LOCATION` in the `.ics` events. Add or update entries if needed.

**Project structure**
- `main.py`: FastAPI app with `/upload` endpoint that orchestrates OCR → parse → ICS build.
- `ocr_utils.py`: Image preprocessing and Tesseract text extraction.
- `parser.py`: Parsing logic that extracts classes and exams from OCR text.
- `ics_builder.py`: Creates iCalendar (`.ics`) bytes from parsed data.
- `requirements.txt`: Python dependencies.

**Development**
- To tweak parsing behavior, edit `parser.py` (regex patterns, `normalize_course_name`, `expand_days`).
- To change calendar details (alarms, timezone, travel time), edit `ics_builder.py`.

**Troubleshooting**
- If OCR quality is poor, try improving image contrast/lighting, or adjust preprocessing in `ocr_utils.preprocess_img`.
- Ensure `tesseract` binary is installed and accessible; confirm with `tesseract --version`.

