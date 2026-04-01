from config.settings import settings
from services.market_data import MarketDataConfig, MarketDataProvider


if __name__ == "__main__":
    config = MarketDataConfig(
        source=settings.market_data_source,
        tickers=settings.live_ticker_list,
        lookback_period=settings.live_lookback_period,
        alphavantage_api_key=settings.alphavantage_api_key,
    )
    provider = MarketDataProvider(config)
    df = provider.fetch()
    output_path = provider.save(df, settings.data_path)
    print(f"Saved {len(df)} rows to {output_path}")
