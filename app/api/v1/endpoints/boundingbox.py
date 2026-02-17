from fastapi import APIRouter, UploadFile, File
from app.services.boundingbox import boundingbox

router = APIRouter()


@router.post("/boundingbox")
async def boundingbox_endpoint(file: UploadFile = File(...)):
    # Using async as it's best practice for FastAPI IO-bound operations
    # though the OCR itself is CPU-bound
    return await boundingbox(file)
