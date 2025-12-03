# app.py
import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from insight_engine import process_and_generate

app = FastAPI(title="Automated Insight Engine")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

@app.post("/generate-report")
async def generate_report(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="Upload at least one file.")

    saved_paths = []
    uploaded_names = []

    # Save each uploaded file into /data preserving filename
    for f in files:
        safe_name = f.filename
        target = os.path.join(DATA_DIR, safe_name)
        with open(target, "wb") as out_file:
            shutil.copyfileobj(f.file, out_file)
        saved_paths.append(target)
        uploaded_names.append(os.path.splitext(safe_name)[0])

    # Build base_name from uploaded names (limit length)
    base_name = "_".join(uploaded_names)
    if len(base_name) > 80:
        base_name = base_name[:75]

    # process_and_generate returns path to ZIP
    zip_path = process_and_generate(saved_paths, base_name)
    return FileResponse(zip_path, filename=os.path.basename(zip_path), media_type="application/zip")
