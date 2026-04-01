from typing import Dict
import pandas as pd


class RiskManager:
    def __init__(self, max_position_weight: float = 0.15):
        self.max_position_weight = max_position_weight

    def apply_weight_caps(self, weights: Dict[str, float]) -> Dict[str, float]:
        capped = {k: min(v, self.max_position_weight) for k, v in weights.items()}
        total = sum(capped.values())
        if total == 0:
            return capped
        return {k: v / total for k, v in capped.items()}

    def estimate_portfolio_vol(self, weights: Dict[str, float], returns: pd.DataFrame) -> float:
        if returns.empty:
            return 0.0
        w = pd.Series(weights).reindex(returns.columns).fillna(0.0).values
        cov = returns.cov().values * 252
        return float((w.T @ cov @ w) ** 0.5)
