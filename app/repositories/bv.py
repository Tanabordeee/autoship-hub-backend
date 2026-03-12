from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.bv import BV
from app.schemas.bv import BVCreate


class BVRepository:
    @staticmethod
    def create(db: Session, payload: BVCreate):
        bv = BV(
            type_of_vehicle=payload.type_of_vehicle,
            make=payload.make,
            model=payload.model,
            seat=payload.seat,
            commonly_called=payload.commonly_called,
            manufacture_grade=payload.manufacture_grade,
            body_colour=payload.body_colour,
            fuel_type=payload.fuel_type,
            year_of_manufacture=payload.year_of_manufacture,
            inspection_mileage=payload.inspection_mileage,
            engine_capacity=payload.engine_capacity,
            engine_no=payload.engine_no,
            driving_system=payload.driving_system,
            marks_of_accident_on_chassis=payload.marks_of_accident_on_chassis,
            condition_of_chassis=payload.condition_of_chassis,
            country_of_origin=payload.country_of_origin,
            year_month_of_first_registration=payload.year_month_of_first_registration,
            code_no=payload.code_no,
            version_bv=payload.version_bv,
            date=payload.date,
            bv_ref_no=payload.bv_ref_no,
            lc_no=payload.lc_no,
            user_id=payload.user_id,
            lc_id=payload.lc_id,
            chassis_no=payload.chassis_no,
        )
        db.add(bv)
        db.commit()
        db.refresh(bv)
        return bv

    @staticmethod
    def get_latest_version_by_bv_ref_no(db: Session, bv_ref_no: str):
        return (
            db.query(BV)
            .filter(
                func.lower(func.trim(BV.bv_ref_no)) == func.lower(func.trim(bv_ref_no))
            )
            .order_by(BV.version_bv.desc())
            .first()
        )

    @staticmethod
    def get_by_id(db: Session, id: int):
        return db.query(BV).filter(BV.id == id).first()

    @staticmethod
    def get_all_versions_by_id(db: Session, id: int):
        """Get all versions of an LC by the lc_no of the given id, sorted by versions descending"""
        bv = db.query(BV).filter(BV.id == id).first()
        if not bv:
            return []

        # หา LC ทั้งหมดที่มี lc_no เดียวกัน
        return (
            db.query(BV)
            .filter(BV.bv_ref_no == bv.bv_ref_no)
            .order_by(BV.version_bv.desc())  # sort จากมากไปน้อย
            .all()
        )
