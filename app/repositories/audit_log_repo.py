from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


from app.models.user import User


class AuditLogRepository:
    def create(
        self,
        db: Session,
        action_type: str,
        entity_type: str,
        user_id: int,
        transaction_id: int,
    ):
        log = AuditLog(
            action_type=action_type,
            entity_type=entity_type,
            user_id=user_id,
            transaction_id=transaction_id,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    def get_by_transaction(self, db: Session, transaction_id: int):
        return (
            db.query(
                AuditLog.id,
                AuditLog.create_at,
                AuditLog.action_type,
                AuditLog.entity_type,
                AuditLog.user_id,
                User.name.label("user_name"),
                AuditLog.transaction_id,
            )
            .outerjoin(User, AuditLog.user_id == User.id)
            .filter(AuditLog.transaction_id == transaction_id)
            .order_by(AuditLog.create_at.desc())
            .all()
        )

    def get_all(self, db: Session):
        return (
            db.query(
                AuditLog.id,
                AuditLog.create_at,
                AuditLog.action_type,
                AuditLog.entity_type,
                AuditLog.user_id,
                User.name.label("user_name"),
                AuditLog.transaction_id,
            )
            .outerjoin(User, AuditLog.user_id == User.id)
            .order_by(AuditLog.create_at.desc())
            .all()
        )


audit_log_repo = AuditLogRepository()
