from fastapi import APIRouter , Depends 
from sqlalchemy.orm import Session
from app.schemas.auth import Login 
from app.api.deps import get_db
from app.services.auth_service import login as login_service
router = APIRouter()

@router.post("/login")
def login(user:Login, db: Session = Depends(get_db)):
    return login_service(user.email, user.password, db)
    