from sqlalchemy.orm import Session
from app.repositories.audit_log_repo import audit_log_repo


class AuditLogService:
    @staticmethod
    def log_action(
        db: Session,
        action_type: str,
        entity_type: str,
        user_id: int,
        transaction_id: int,
    ):
        return audit_log_repo.create(
            db, action_type, entity_type, user_id, transaction_id
        )

    @staticmethod
    def get_transaction_logs(db: Session, transaction_id: int):
        return audit_log_repo.get_by_transaction(db, transaction_id)

    @staticmethod
    def list_logs(db: Session):
        return audit_log_repo.get_all(db)


audit_log_service = AuditLogService()
