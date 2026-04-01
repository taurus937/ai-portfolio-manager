from typing import Dict, List, Optional
from pydantic import BaseModel


class AssetSignal(BaseModel):
    ticker: str
    expected_return: float
    volatility: float
    score: float


class PortfolioWeights(BaseModel):
    weights: Dict[str, float]


class BacktestResult(BaseModel):
    cumulative_return: float
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    max_drawdown: float
    history: List[Dict]


class PaperOrder(BaseModel):
    ticker: str
    side: str
    quantity: float
    price: float
    notional: float


class PaperAccount(BaseModel):
    cash: float
    positions: Dict[str, float]
    order_history: List[Dict]
    last_updated: Optional[str] = None
