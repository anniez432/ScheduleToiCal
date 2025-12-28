from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import tempfile
from pprint import pprint
from datetime import date

from ocr_utils import preprocess_img
from parser import parse_schedule
from ics_builder import build_ics

import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "https://scheduletoical.onrender.com",
                   "https://uwmadison-schedule-to-ical.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")

async def upload(file: UploadFile = File(...)):
    # save temp file
    with tempfile.NamedTemporaryFile(delete = False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

        # ocr -> parse 
        text = preprocess_img(tmp_path)
        parsed = parse_schedule(text)

        pprint(parsed)

        term_start = date(2026, 1, 20)
        term_end = date(2026, 5, 4)

        ics_bytes = build_ics(parsed, term_start, term_end)

        """
        out_path = tmp_path + ".ics"
        with open(out_path, "wb") as f:
            f.write(ics_bytes)

        return FileResponse(out_path, media_type="text/calendar", filename="schedule.ics")
        """
        ics_base64 = base64.b64encode(ics_bytes).decode("utf-8")

        return JSONResponse({
            "classes": parsed.get("classes", []),
            "exams": parsed.get("exams", []),
            "ics_base64": ics_base64
        })

    
@app.get("/download/{filename}")
def download_ics(filename: str):
    return FileResponse(f"/tmp/{filename}", media_type="text/calendar", filename="schedule.ics")