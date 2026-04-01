from typing import Dict

import pandas as pd

from services.features import FeatureEngineer
from services.regime import RegimeDetector
from services.signals import SignalModel
from services.optimizer import Optimizer
from services.risk import RiskManager


class PortfolioManager:
    def __init__(self, benchmark: str, max_position_weight: float = 0.15):
        self.benchmark = benchmark
        self.feature_engineer = FeatureEngineer()
        self.regime_detector = RegimeDetector()
        self.signal_model = SignalModel()
        self.optimizer = Optimizer(top_n=5)
        self.risk_manager = RiskManager(max_position_weight=max_position_weight)

    def rebalance(self, prices: pd.DataFrame) -> Dict[str, float]:
        if self.benchmark not in prices.columns:
            raise ValueError(f"Benchmark {self.benchmark} not found in price data.")

        features = self.feature_engineer.latest_feature_snapshot(prices)
        benchmark_prices = prices[self.benchmark]
        regime = self.regime_detector.classify(benchmark_prices)
        scored = self.signal_model.score_assets(features, regime)

        if self.benchmark in scored.index:
            scored = scored.drop(index=self.benchmark)

        raw_weights = self.optimizer.optimize(scored)
        final_weights = self.risk_manager.apply_weight_caps(raw_weights)
        return final_weights
