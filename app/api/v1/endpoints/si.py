from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.si import SICreate, ConfirmSi
from app.services.si import create_si, confirm_si
from app.api.deps import get_current_user
from app.models.user import User
from fastapi import Body

router = APIRouter()


@router.post("/si")
def create_si_endpoint(
    db: Session = Depends(get_db),
    payload: SICreate = Body(...),
    current_user: User = Depends(get_current_user),
):
    result = create_si(db, payload)
    if result:
        filename = result["output_path"].split("\\")[-1]
        return FileResponse(
            result["output_path"],
            media_type="application/pdf",
            filename=filename,
            headers={"X-SI-ID": str(result["si_id"])},
        )
    return {"error": "Failed to generate SI"}


@router.post("/confirm_si")
def confirm_si_endpoint(
    payload: ConfirmSi,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return confirm_si(db, payload.transaction_id, payload.si_id)
