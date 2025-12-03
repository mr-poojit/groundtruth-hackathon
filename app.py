from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
from insight_engine import process_and_generate
import os

app = FastAPI()

@app.post("/generate-report")
async def generate_report(files: list[UploadFile] = File(...)):
    saved_paths = []
    os.makedirs("data", exist_ok=True)

    uploaded_names = []

    for f in files:
        path = f"data/{f.filename}"
        with open(path, "wb") as out:
            shutil.copyfileobj(f.file, out)
        saved_paths.append(path)
        uploaded_names.append(os.path.splitext(f.filename)[0])  

    # join filenames for final output
    base_name = "_".join(uploaded_names)

    zip_path = process_and_generate(saved_paths, base_name)
    return FileResponse(zip_path, filename=os.path.basename(zip_path), media_type="application/zip")

