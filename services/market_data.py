from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests
import yfinance as yf


@dataclass
class MarketDataConfig:
    source: str
    tickers: list[str]
    lookback_period: str = "2y"
    alphavantage_api_key: str = ""


class MarketDataProvider:
    def __init__(self, config: MarketDataConfig):
        self.config = config

    def fetch(self) -> pd.DataFrame:
        source = self.config.source.lower()
        if source == "yfinance":
            return self._fetch_yfinance()
        if source == "alphavantage":
            return self._fetch_alphavantage()
        raise ValueError(f"Unsupported market data source: {self.config.source}")

    def _fetch_yfinance(self) -> pd.DataFrame:
        df = yf.download(
            tickers=self.config.tickers,
            period=self.config.lookback_period,
            auto_adjust=True,
            progress=False,
            group_by="ticker",
            threads=True,
        )

        if df.empty:
            raise ValueError("No data returned from yfinance.")

        frames = []
        if isinstance(df.columns, pd.MultiIndex):
            for ticker in self.config.tickers:
                if ticker not in df.columns.get_level_values(0):
                    continue
                ticker_df = df[ticker].copy()
                if "Close" not in ticker_df.columns:
                    continue
                temp = ticker_df[["Close"]].reset_index()
                temp.columns = ["date", "close"]
                temp["ticker"] = ticker
                frames.append(temp[["date", "ticker", "close"]])
        else:
            if "Close" not in df.columns:
                raise ValueError("Expected Close column in yfinance response.")
            temp = df[["Close"]].reset_index()
            temp.columns = ["date", "close"]
            temp["ticker"] = self.config.tickers[0]
            frames.append(temp[["date", "ticker", "close"]])

        if not frames:
            raise ValueError("Could not parse yfinance response into price records.")

        out = pd.concat(frames, ignore_index=True)
        out["date"] = pd.to_datetime(out["date"]).dt.tz_localize(None)
        out = out.dropna(subset=["close"]).sort_values(["ticker", "date"])
        return out

    def _fetch_alphavantage(self) -> pd.DataFrame:
        if not self.config.alphavantage_api_key:
            raise ValueError("ALPHAVANTAGE_API_KEY is required for Alpha Vantage.")

        frames = []
        for ticker in self.config.tickers:
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_DAILY_ADJUSTED",
                "symbol": ticker,
                "outputsize": "full",
                "apikey": self.config.alphavantage_api_key,
            }
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            payload = resp.json()

            series = payload.get("Time Series (Daily)")
            if not series:
                note = payload.get("Note") or payload.get("Information") or payload
                raise ValueError(f"Alpha Vantage returned no time series for {ticker}: {note}")

            rows = []
            for dt, values in series.items():
                rows.append(
                    {
                        "date": pd.to_datetime(dt),
                        "ticker": ticker,
                        "close": float(values["5. adjusted close"]),
                    }
                )
            frames.append(pd.DataFrame(rows))

        out = pd.concat(frames, ignore_index=True)
        out = out.sort_values(["ticker", "date"])
        return out

    @staticmethod
    def save(df: pd.DataFrame, path: str | Path) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        return output_path
