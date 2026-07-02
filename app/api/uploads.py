from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import get_current_user
from app.models.models import User
from app.services.storage_service import store_uploaded_image

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("/image")
def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    return store_uploaded_image(file)
