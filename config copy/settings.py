from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="AI Portfolio Manager MVP", alias="APP_NAME")
    risk_free_rate: float = Field(default=0.04, alias="RISK_FREE_RATE")
    target_vol: float = Field(default=0.15, alias="TARGET_VOL")
    max_position_weight: float = Field(default=0.15, alias="MAX_POSITION_WEIGHT")
    max_turnover: float = Field(default=0.25, alias="MAX_TURNOVER")
    benchmark: str = Field(default="SPY", alias="BENCHMARK")

    market_data_source: str = Field(default="yfinance", alias="MARKET_DATA_SOURCE")
    live_tickers: str = Field(default="SPY,QQQ,XLF,XLV,XLI,TLT,GLD", alias="LIVE_TICKERS")
    live_lookback_period: str = Field(default="2y", alias="LIVE_LOOKBACK_PERIOD")
    data_path: str = Field(default="data/live_prices.csv", alias="DATA_PATH")
    alphavantage_api_key: str = Field(default="", alias="ALPHAVANTAGE_API_KEY")

    paper_initial_cash: float = Field(default=100000.0, alias="PAPER_INITIAL_CASH")
    paper_state_path: str = Field(default="data/paper_account.json", alias="PAPER_STATE_PATH")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def live_ticker_list(self) -> list[str]:
        return [ticker.strip().upper() for ticker in self.live_tickers.split(",") if ticker.strip()]


settings = Settings()
