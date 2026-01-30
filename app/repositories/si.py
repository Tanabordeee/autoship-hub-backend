from sqlalchemy.orm import Session
from app.models.si import SI
from app.schemas.si import SICreate


class SI_Repository:
    def create_si(db: Session, payload: SICreate):
        si = SI(
            gross_weight=payload.gross_weight,
            measurement=payload.measurement,
            port_of_loading=payload.port_of_loading,
            port_of_discharge=payload.port_of_discharge,
            number_of_original_bs=payload.number_of_original_bs,
            no_of_packages=payload.no_of_packages,
            seal_no=payload.seal_no,
            user_id=payload.user_id,
        )
        db.add(si)
        db.commit()
        db.refresh(si)
        return si

    def get_by_id(db: Session, id: int):
        return db.query(SI).filter(SI.id == id).first()
