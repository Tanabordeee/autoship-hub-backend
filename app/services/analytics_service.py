from sqlalchemy.orm import Session
from app.repositories.analytics_repo import AnalyticsRepo
from app.schemas.analytics import (
    AnalyticsResponse,
    StatItem,
    TrendData,
    TrendDataset,
)


class AnalyticsService:
    @staticmethod
    def get_analytics(db: Session) -> AnalyticsResponse:
        stats_raw = AnalyticsRepo.get_stats(db)
        trend_raw = AnalyticsRepo.get_sales_trend(db)

        # Format Stats using math-based changes from repo
        stats = [
            StatItem(
                title="Total Sales",
                value=f"${stats_raw['total_sales'] / 1000000:.1f}M",
                change=f"{stats_raw['revenue']['change']:+.1f}%",
            ),
            StatItem(
                title="Vehicles Sold",
                value=str(stats_raw["units"]["current"]),
                change=f"{stats_raw['units']['change']:+.1f}%",
            ),
            StatItem(
                title="Avg. Transaction",
                value=f"${stats_raw['avg_transaction']['current'] / 1000:.1f}K",
                change=f"{stats_raw['avg_transaction']['change']:+.1f}%",
            ),
            StatItem(
                title="Active Deals",
                value=str(stats_raw["active_deals"]["current"]),
                change=f"{stats_raw['active_deals']['change']:+.1f}%",
            ),
        ]

        # Format Trend
        labels = [r.month for r in trend_raw]
        data = [float(r.count) for r in trend_raw]

        # Ensure we have data even if empty
        if not labels:
            labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
            data = [0, 0, 0, 0, 0, 0]

        sales_trend = TrendData(
            labels=labels, datasets=[TrendDataset(label="Vehicles Sold", data=data)]
        )
        return AnalyticsResponse(stats=stats, sales_trend=sales_trend)
