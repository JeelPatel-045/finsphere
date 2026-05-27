from fastapi import APIRouter, UploadFile
import shutil

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/")
def upload_document(file: UploadFile):
    save_path = f"uploads/{file.filename}"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "File uploaded successfully",
        "filename": file.filename
    }