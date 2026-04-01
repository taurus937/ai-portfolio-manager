import pandas as pd


class SignalModel:
    def score_assets(self, features: pd.DataFrame, regime: str) -> pd.DataFrame:
        df = features.copy()

        df["score"] = (
            0.45 * df["mom_20"]
            + 0.45 * df["mom_60"]
            - 0.10 * df["vol_20"]
        )

        if regime == "risk_off":
            df["score"] = df["score"] - 0.05 * df["vol_20"]

        df["expected_return"] = df["score"].clip(lower=-0.20, upper=0.20)
        df["volatility"] = df["vol_20"]
        return df.sort_values("score", ascending=False)
