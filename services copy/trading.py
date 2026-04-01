from __future__ import annotations

from typing import Dict

import pandas as pd

from services.paper_broker import PaperBroker


class TradingService:
    def __init__(self, broker: PaperBroker):
        self.broker = broker

    def rebalance_to_target(self, prices: pd.DataFrame, target_weights: Dict[str, float]) -> Dict:
        state = self.broker.load_state()
        latest_prices = self.broker.latest_prices(prices)
        before_value = self.broker.account_value(state, latest_prices)
        orders = self.broker.build_target_orders(target_weights, state, latest_prices)
        new_state = self.broker.execute_orders(state, orders)
        after_value = self.broker.account_value(new_state, latest_prices)

        return {
            "target_weights": target_weights,
            "orders": orders,
            "account_before": {
                "cash": state["cash"],
                "positions": state["positions"],
                "equity_value": round(before_value, 2),
            },
            "account_after": {
                "cash": new_state["cash"],
                "positions": new_state["positions"],
                "equity_value": round(after_value, 2),
            },
        }
