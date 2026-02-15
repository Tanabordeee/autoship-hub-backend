from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.bencer import BencerGenerate, CreateBencer
from app.services.bencer import generate_bencer, confirm_bencer
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/generate-bencer")
def generate_bencer_endpoint(
    payload: BencerGenerate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = generate_bencer(db, payload, current_user.id)
        if result and "output_path" in result:
            output_path = result["output_path"]
            filename = output_path.split("\\")[-1]
            return FileResponse(
                output_path,
                media_type="application/pdf",
                filename=filename,
            )
        return {"error": "Failed to generate bencer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/confirm_bencer")
def confirm_bencer_endpoint(
    payload: CreateBencer,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = confirm_bencer(db, payload, current_user.id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
