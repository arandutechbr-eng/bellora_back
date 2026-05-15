from fastapi import APIRouter, UploadFile, File
import shutil
from pathlib import Path
from uuid import uuid4

router = APIRouter(prefix="/uploads", tags=["Uploads"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/image")
def upload_image(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix
    filename = f"{uuid4()}{ext}"
    file_path = UPLOAD_DIR / filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": filename,
        "url": f"http://127.0.0.1:8000/media/{filename}"
    }