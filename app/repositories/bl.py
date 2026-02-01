from app.models.bl import BL
from sqlalchemy.orm import Session
from app.schemas.bl import BLCreate


class BLRepository:
    @staticmethod
    def create(db: Session, bl: BLCreate) -> BL:
        db_bl = BL(
            version_bl=bl.version_bl,
            bl_number=bl.bl_number,
            jo_number=bl.jo_number,
            shipper=bl.shipper,
            consignee=bl.consignee,
            notify_party=bl.notify_party,
            place_of_receipt=bl.place_of_receipt,
            port_of_loading=bl.port_of_loading,
            port_of_discharge=bl.port_of_discharge,
            ocean_vessel=bl.ocean_vessel,
            place_of_delivery=bl.place_of_delivery,
            freight_payable_at=bl.freight_payable_at,
            number_of_original_bs=bl.number_of_original_bs,
            gross_weight=bl.gross_weight,
            measurement=bl.measurement,
            cy_cf=bl.cy_cf,
            description_of_good=bl.description_of_good,
            container=bl.container,
            seal_no=bl.seal_no,
            user_id=bl.user_id,
            size_no=bl.size_no,
        )
        db.add(db_bl)
        db.commit()
        db.refresh(db_bl)
        return db_bl

    @staticmethod
    def get_latest_version_by_bl_no(db: Session, bl_number: str) -> BL:
        return (
            db.query(BL)
            .filter(BL.bl_number == bl_number)
            .order_by(BL.version_bl.desc())
            .first()
        )
