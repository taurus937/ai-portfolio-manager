import numpy as np
import pandas as pd


class FeatureEngineer:
    @staticmethod
    def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
        return prices.pct_change().fillna(0.0)

    @staticmethod
    def compute_momentum(prices: pd.DataFrame, lookback: int = 20) -> pd.DataFrame:
        return prices / prices.shift(lookback) - 1.0

    @staticmethod
    def compute_volatility(returns: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        return returns.rolling(window).std() * np.sqrt(252)

    @staticmethod
    def latest_feature_snapshot(prices: pd.DataFrame) -> pd.DataFrame:
        returns = FeatureEngineer.compute_returns(prices)
        mom_20 = FeatureEngineer.compute_momentum(prices, lookback=20)
        mom_60 = FeatureEngineer.compute_momentum(prices, lookback=60)
        vol_20 = FeatureEngineer.compute_volatility(returns, window=20)

        snapshot = pd.DataFrame(
            {
                "mom_20": mom_20.iloc[-1],
                "mom_60": mom_60.iloc[-1],
                "vol_20": vol_20.iloc[-1],
                "last_price": prices.iloc[-1],
            }
        ).dropna()

        return snapshot
