from pathlib import Path
import pandas as pd


class DataLoader:
    def __init__(self, data_path: str = "data/live_prices.csv"):
        self.data_path = Path(data_path)

    def load_prices(self) -> pd.DataFrame:
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Price file not found: {self.data_path}. Run fetch_market_data.py first "
                "or point DATA_PATH to an existing CSV."
            )
        df = pd.read_csv(self.data_path, parse_dates=["date"])
        df = df.sort_values(["ticker", "date"])
        return df

    def pivot_close_prices(self) -> pd.DataFrame:
        df = self.load_prices()
        prices = df.pivot(index="date", columns="ticker", values="close").sort_index()
        return prices
