from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, RoleChecker
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import AnalyticsResponse
from app.models.user import User

router = APIRouter()


@router.get(
    "/analytics",
    response_model=AnalyticsResponse,
    dependencies=[Depends(RoleChecker(["admin"]))],
)
def get_analytics_endpoint(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return AnalyticsService.get_analytics(db)
