from typing import Dict
import pandas as pd


class Optimizer:
    """
    MVP optimizer:
    - rank by score
    - keep top N
    - assign score-proportional long-only weights
    """

    def __init__(self, top_n: int = 5):
        self.top_n = top_n

    def optimize(self, scored_assets: pd.DataFrame) -> Dict[str, float]:
        top = scored_assets.head(self.top_n).copy()
        top = top[top["score"] > 0]

        if top.empty:
            return {}

        raw = top["score"] / top["score"].sum()
        return raw.to_dict()
