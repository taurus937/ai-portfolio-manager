from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import pandas as pd


@dataclass
class PaperBrokerConfig:
    state_path: str
    initial_cash: float = 100000.0


class PaperBroker:
    def __init__(self, config: PaperBrokerConfig):
        self.config = config
        self.state_path = Path(config.state_path)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.state_path.exists():
            self.reset_account()

    def _default_state(self) -> Dict:
        return {
            "cash": float(self.config.initial_cash),
            "positions": {},
            "order_history": [],
            "last_updated": None,
        }

    def load_state(self) -> Dict:
        if not self.state_path.exists():
            return self._default_state()
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def save_state(self, state: Dict) -> None:
        state["last_updated"] = datetime.now(timezone.utc).isoformat()
        self.state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def reset_account(self) -> Dict:
        state = self._default_state()
        self.save_state(state)
        return state

    @staticmethod
    def latest_prices(prices: pd.DataFrame) -> Dict[str, float]:
        latest = prices.iloc[-1].dropna()
        return {str(k): float(v) for k, v in latest.items()}

    def account_value(self, state: Dict, latest_prices: Dict[str, float]) -> float:
        position_value = 0.0
        for ticker, qty in state["positions"].items():
            price = latest_prices.get(ticker, 0.0)
            position_value += float(qty) * price
        return float(state["cash"]) + position_value

    def build_target_orders(
        self,
        target_weights: Dict[str, float],
        state: Dict,
        latest_prices: Dict[str, float],
    ) -> List[Dict]:
        total_value = self.account_value(state, latest_prices)
        current_positions = state["positions"]

        current_values = {
            ticker: float(qty) * latest_prices.get(ticker, 0.0)
            for ticker, qty in current_positions.items()
        }

        target_values = {
            ticker: total_value * float(weight)
            for ticker, weight in target_weights.items()
        }

        universe = sorted(set(current_values.keys()) | set(target_values.keys()))
        orders: List[Dict] = []

        for ticker in universe:
            price = latest_prices.get(ticker)
            if price is None or price <= 0:
                continue

            current_value = current_values.get(ticker, 0.0)
            target_value = target_values.get(ticker, 0.0)
            delta_value = target_value - current_value

            if abs(delta_value) < 1e-6:
                continue

            qty = delta_value / price
            if abs(qty) < 1e-6:
                continue

            orders.append(
                {
                    "ticker": ticker,
                    "side": "buy" if qty > 0 else "sell",
                    "quantity": round(abs(qty), 6),
                    "price": round(float(price), 6),
                    "notional": round(abs(delta_value), 2),
                }
            )
        return orders

    def execute_orders(self, state: Dict, orders: List[Dict]) -> Dict:
        positions = dict(state["positions"])
        cash = float(state["cash"])
        order_history = list(state["order_history"])

        for order in orders:
            ticker = order["ticker"]
            qty = float(order["quantity"])
            price = float(order["price"])
            side = order["side"]
            signed_qty = qty if side == "buy" else -qty
            cash_change = -(qty * price) if side == "buy" else (qty * price)

            positions[ticker] = round(float(positions.get(ticker, 0.0)) + signed_qty, 6)
            if abs(positions[ticker]) < 1e-8:
                positions.pop(ticker, None)

            cash = round(cash + cash_change, 6)

            order_history.append(
                {
                    **order,
                    "executed_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        new_state = {
            "cash": cash,
            "positions": positions,
            "order_history": order_history[-500:],
            "last_updated": state.get("last_updated"),
        }
        self.save_state(new_state)
        return new_state
