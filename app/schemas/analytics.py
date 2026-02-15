from pydantic import BaseModel
from typing import List, Optional


class StatItem(BaseModel):
    title: str
    value: str
    change: str
    icon: Optional[str] = None


class TrendDataset(BaseModel):
    label: str
    data: List[float]
    borderColor: str = "#9c9c9cff"
    tension: float = 0.4


class TrendData(BaseModel):
    labels: List[str]
    datasets: List[TrendDataset]


class AnalyticsResponse(BaseModel):
    stats: List[StatItem]
    sales_trend: TrendData
