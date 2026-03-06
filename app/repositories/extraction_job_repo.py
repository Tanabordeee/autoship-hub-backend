from sqlalchemy.orm import Session
from app.models.extraction_job import ExtractionJob
from app.schemas.extraction_job import ExtractionJobCreate, ExtractionJobUpdate
from typing import Optional


class ExtractionJobRepo:
    @staticmethod
    def create(db: Session, payload: ExtractionJobCreate) -> ExtractionJob:
        db_obj = ExtractionJob(
            id=payload.id,
            transaction_id=payload.transaction_id,
            user_id=payload.user_id,
            status=payload.status,
            result=payload.result,
            error_message=payload.error_message,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get(db: Session, id: str) -> Optional[ExtractionJob]:
        return db.query(ExtractionJob).filter(ExtractionJob.id == id).first()

    @staticmethod
    def update(
        db: Session, id: str, payload: ExtractionJobUpdate
    ) -> Optional[ExtractionJob]:
        db_obj = db.query(ExtractionJob).filter(ExtractionJob.id == id).first()
        if not db_obj:
            return None

        if payload.status is not None:
            db_obj.status = payload.status
        if payload.result is not None:
            db_obj.result = payload.result
        if payload.error_message is not None:
            db_obj.error_message = payload.error_message

        db.commit()
        db.refresh(db_obj)
        return db_obj
