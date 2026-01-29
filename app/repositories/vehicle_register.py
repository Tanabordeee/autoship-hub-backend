from sqlalchemy.orm import Session
from app.models.vehicle_register import VehicleRegister
from app.schemas.vehicle_register import VehicleRegisterCreate


class VehicleRegisterRepo:
    def create(
        db: Session, payload: VehicleRegisterCreate, user_id: int, transaction_id: int
    ):
        vehicle_register = VehicleRegister(
            model_year=payload.model_year,
            seat=payload.seat,
            characteristics=payload.characteristics,
            car_engine=payload.car_engine,
            chassis_no=payload.chassis_no,
            colour=payload.colour,
            total_weight=payload.total_weight,
            vehicle_weight=payload.vehicle_weight,
            date_of_registration=payload.date_of_registration,
            type_car=payload.type_car,
            registration_no=payload.registration_no,
            engine_no=payload.engine_no,
            vehicle_make=payload.vehicle_make,
            province=payload.province,
            model=payload.model,
            fuel_type=payload.fuel_type,
            lc_id=payload.lc_id,
            user_id=user_id,
            transaction_id=transaction_id,
        )
        db.add(vehicle_register)
        db.commit()
        db.refresh(vehicle_register)
        return vehicle_register

    def get_by_id(db: Session, id: int):
        return db.query(VehicleRegister).filter(VehicleRegister.id == id).first()
