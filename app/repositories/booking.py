from sqlalchemy.orm import Session
from app.models.booking import Booking
from app.schemas.booking import CreateBooking


class BookingRepo:
    def create(db: Session, payload: CreateBooking, user_id: int):
        booking = Booking(
            at_before=payload.at_before,
            booking_no=payload.booking_no,
            date=payload.date,
            cut_off_vgm=payload.cut_off_vgm,
            cut_off_si=payload.cut_off_si,
            booking_name=payload.booking_name,
            etd=payload.etd,
            fob_at_quantities=payload.fob_at_quantities,
            consignee=payload.consignee,
            return_date=payload.return_date,
            cy_date=payload.cy_date,
            cy_at=payload.cy_at,
            carrier=payload.carrier,
            closing_date=payload.closing_date,
            port_of_disch=payload.port_of_disch,
            shipper=payload.shipper,
            port_of_del=payload.port_of_del,
            return_yard=payload.return_yard,
            port_of_loading=payload.port_of_loading,
            eta_date=payload.eta_date,
            feeder=payload.feeder,
            place_of_rec=payload.place_of_rec,
            paperless_code=payload.paperless_code,
            user_id=user_id,
            lc_id=payload.lc_id,
            transaction_id=payload.transaction_id,
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking
