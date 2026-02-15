from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.proforma_invoice import ProformaInvoice, PiItem
from app.models.transaction import Transaction
from app.models.bv import BV
from datetime import datetime, timedelta


class AnalyticsRepo:
    @staticmethod
    def get_stats(db: Session):
        now = datetime.now()
        first_day_current = now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        first_day_prev = (first_day_current - timedelta(days=1)).replace(day=1)

        # Total Sales (Overall)
        total_sales_overall = (
            db.query(func.sum(ProformaInvoice.total_price)).scalar() or 0
        )

        # --- Revenue ---
        current_rev = (
            db.query(func.sum(ProformaInvoice.total_price))
            .filter(ProformaInvoice.created_at >= first_day_current)
            .scalar()
            or 0
        )
        prev_rev = (
            db.query(func.sum(ProformaInvoice.total_price))
            .filter(
                ProformaInvoice.created_at >= first_day_prev,
                ProformaInvoice.created_at < first_day_current,
            )
            .scalar()
            or 0
        )

        # --- Units Sold (Chassis Items) ---
        current_units = (
            db.query(func.count(PiItem.id))
            .join(ProformaInvoice, PiItem.pi_id == ProformaInvoice.id)
            .filter(
                PiItem.item_type == "CHASSIS",
                ProformaInvoice.created_at >= first_day_current,
            )
            .scalar()
            or 0
        )
        prev_units = (
            db.query(func.count(PiItem.id))
            .join(ProformaInvoice, PiItem.pi_id == ProformaInvoice.id)
            .filter(
                PiItem.item_type == "CHASSIS",
                ProformaInvoice.created_at >= first_day_prev,
                ProformaInvoice.created_at < first_day_current,
            )
            .scalar()
            or 0
        )

        # --- Avg Transaction (Price per Chassis) ---
        current_avg = (
            db.query(func.avg(ProformaInvoice.total_price))
            .filter(ProformaInvoice.created_at >= first_day_current)
            .scalar()
            or 0
        )
        prev_avg = (
            db.query(func.avg(ProformaInvoice.total_price))
            .filter(
                ProformaInvoice.created_at >= first_day_prev,
                ProformaInvoice.created_at < first_day_current,
            )
            .scalar()
            or 0
        )

        # --- Active Deals (Current snapshot vs previous month same time?) ---
        # For simplicity, we compare total active now vs total active on last day of prev month
        active_deals = (
            db.query(func.count(Transaction.id))
            .filter(Transaction.status != "completed")
            .scalar()
            or 0
        )
        # Note: Historical active deals would require a history table.
        # We'll stick to revenue/units for now as they are the primary metrics.

        def calc_change(curr, prev):
            if not prev or prev == 0:
                return 0
            return ((float(curr) - float(prev)) / float(prev)) * 100

        return {
            "total_sales": float(total_sales_overall),
            "revenue": {
                "current": float(current_rev),
                "change": calc_change(current_rev, prev_rev),
            },
            "units": {
                "current": int(current_units),
                "change": calc_change(current_units, prev_units),
            },
            "avg_transaction": {
                "current": float(current_avg),
                "change": calc_change(current_avg, prev_avg),
            },
            "active_deals": {
                "current": int(active_deals),
                "change": 0,
            },  # Placeholder or zero if no history
        }

    @staticmethod
    def get_sales_trend(db: Session):
        # Last 6 months
        trend_data = (
            db.query(
                func.to_char(ProformaInvoice.created_at, "Mon").label("month"),
                func.count(PiItem.id).label("count"),
            )
            .join(PiItem, PiItem.pi_id == ProformaInvoice.id)
            .filter(PiItem.item_type == "CHASSIS")
            .group_by(func.to_char(ProformaInvoice.created_at, "Mon"))
            .order_by(func.min(ProformaInvoice.created_at))
            .limit(6)
            .all()
        )
        return trend_data
