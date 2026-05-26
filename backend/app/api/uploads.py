from fastapi import APIRouter, File, UploadFile
import shutil
from pathlib import Path
from uuid import uuid4

from app.core.config import settings

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

    base_url = settings.PUBLIC_API_BASE_URL.rstrip("/")
    return {
        "filename": filename,
        "url": f"{base_url}/media/{filename}",
    }