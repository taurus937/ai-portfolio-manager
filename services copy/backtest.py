from typing import Dict, List

import numpy as np
import pandas as pd

from services.portfolio import PortfolioManager


class Backtester:
    def __init__(self, benchmark: str = "SPY", rebalance_every: int = 20):
        self.benchmark = benchmark
        self.rebalance_every = rebalance_every
        self.manager = PortfolioManager(benchmark=benchmark)

    @staticmethod
    def max_drawdown(equity_curve: pd.Series) -> float:
        running_max = equity_curve.cummax()
        drawdown = equity_curve / running_max - 1.0
        return float(drawdown.min())

    def run(self, prices: pd.DataFrame) -> Dict:
        returns = prices.pct_change().fillna(0.0)
        weights = {}
        portfolio_returns: List[float] = []
        history: List[Dict] = []

        start_idx = min(200, max(1, len(prices) - 2))

        for i in range(start_idx, len(prices) - 1):
            window_prices = prices.iloc[: i + 1]

            if (i - start_idx) % self.rebalance_every == 0:
                weights = self.manager.rebalance(window_prices)

            next_day_returns = returns.iloc[i + 1]
            port_ret = 0.0
            for ticker, weight in weights.items():
                if ticker in next_day_returns.index:
                    port_ret += weight * float(next_day_returns[ticker])

            portfolio_returns.append(port_ret)
            history.append(
                {
                    "date": str(prices.index[i + 1].date()),
                    "return": port_ret,
                    "weights": weights.copy(),
                }
            )

        if not portfolio_returns:
            return {
                "cumulative_return": 0.0,
                "annualized_return": 0.0,
                "annualized_volatility": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "history": history,
            }

        series = pd.Series(portfolio_returns)
        equity_curve = (1 + series).cumprod()

        ann_return = float((equity_curve.iloc[-1] ** (252 / len(series))) - 1)
        ann_vol = float(series.std() * np.sqrt(252)) if len(series) > 1 else 0.0
        sharpe = float(ann_return / ann_vol) if ann_vol > 0 else 0.0
        mdd = self.max_drawdown(equity_curve)

        return {
            "cumulative_return": float(equity_curve.iloc[-1] - 1),
            "annualized_return": ann_return,
            "annualized_volatility": ann_vol,
            "sharpe_ratio": sharpe,
            "max_drawdown": mdd,
            "history": history,
        }
