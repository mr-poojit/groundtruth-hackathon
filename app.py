from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import shutil
from insight_engine import process_and_generate

app = FastAPI()

@app.post("/generate-report")
async def generate_report(files: list[UploadFile] = File(...)):
    saved = []

    for f in files:
        path = f"data/{f.filename}"
        with open(path, "wb") as out:
            shutil.copyfileobj(f.file, out)
        saved.append(path)

    zip_path = process_and_generate(saved)

    return FileResponse(zip_path, filename=os.path.basename(zip_path), media_type="application/zip")
