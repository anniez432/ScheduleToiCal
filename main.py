from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import tempfile
from datetime import date

from ocr_utils import preprocess_img
from parser import parse_schedule
from ics_builder import build_ics

app = FastAPI()

@app.post("/upload")

async def upload(file: UploadFile = File(...)):
    # save temp file
    with tempfile.NamedTemporaryFile(delete = False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

        # ocr -> parse 
        text = preprocess_img(tmp_path)
        parsed = parse_schedule(text)

        term_start = date(2025, 9, 3)
        term_end = date(2025, 12, 18)

        ics_bytes = build_ics(parsed, term_start, term_end)

        out_path = tmp_path + ".ics"
        with open(out_path, "wb") as f:
            f.write(ics_bytes)

        return FileResponse(out_path, media_type="text/calendar", filename="schedule.ics")