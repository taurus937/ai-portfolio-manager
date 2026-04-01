import pandas as pd


class RegimeDetector:
    """
    Simple MVP regime model:
    - risk_on if benchmark > 200d moving average
    - risk_off otherwise
    """

    def classify(self, benchmark_prices: pd.Series) -> str:
        ma_200 = benchmark_prices.rolling(200).mean()
        if len(benchmark_prices.dropna()) < 200:
            return "neutral"
        return "risk_on" if benchmark_prices.iloc[-1] > ma_200.iloc[-1] else "risk_off"
