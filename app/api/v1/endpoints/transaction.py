from fastapi import APIRouter
from app.api.deps import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.services.transaction import get_all_transactions

router = APIRouter()


@router.get("/transactions")
def get_all_transactions_endpoint(db: Session = Depends(get_db)):
    return get_all_transactions(db)
