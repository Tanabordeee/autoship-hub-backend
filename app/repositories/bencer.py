from sqlalchemy.orm import Session
from app.schemas.bencer import CreateBencer
from app.models.bencer import Bencer


class BencerRepo:
    def create(db: Session, payload: CreateBencer, user_id: int):
        bencer = Bencer(
            date=payload.date,
            director=payload.director,
            user_id=user_id,
        )
        db.add(bencer)
        db.commit()
        db.refresh(bencer)
        return bencer

    def get_by_id(db: Session, id: int):
        return db.query(Bencer).filter(Bencer.id == id).first()
