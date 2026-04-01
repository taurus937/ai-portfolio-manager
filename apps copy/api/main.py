from fastapi import FastAPI, HTTPException

from config.settings import settings
from services.backtest import Backtester
from services.data_loader import DataLoader
from services.market_data import MarketDataConfig, MarketDataProvider
from services.paper_broker import PaperBroker, PaperBrokerConfig
from services.portfolio import PortfolioManager
from services.trading import TradingService

app = FastAPI(title=settings.app_name)


def get_broker() -> PaperBroker:
    return PaperBroker(
        PaperBrokerConfig(
            state_path=settings.paper_state_path,
            initial_cash=settings.paper_initial_cash,
        )
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}


@app.post("/market-data/refresh")
def refresh_market_data() -> dict:
    try:
        config = MarketDataConfig(
            source=settings.market_data_source,
            tickers=settings.live_ticker_list,
            lookback_period=settings.live_lookback_period,
            alphavantage_api_key=settings.alphavantage_api_key,
        )
        provider = MarketDataProvider(config)
        df = provider.fetch()
        output_path = provider.save(df, settings.data_path)
        return {"rows_saved": len(df), "path": str(output_path), "source": settings.market_data_source}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/portfolio/rebalance")
def portfolio_rebalance() -> dict:
    try:
        loader = DataLoader(settings.data_path)
        prices = loader.pivot_close_prices()
        manager = PortfolioManager(
            benchmark=settings.benchmark,
            max_position_weight=settings.max_position_weight,
        )
        weights = manager.rebalance(prices)
        return {"benchmark": settings.benchmark, "weights": weights}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/backtest")
def run_backtest() -> dict:
    try:
        loader = DataLoader(settings.data_path)
        prices = loader.pivot_close_prices()
        backtester = Backtester(benchmark=settings.benchmark)
        return backtester.run(prices)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/paper/account")
def paper_account() -> dict:
    try:
        loader = DataLoader(settings.data_path)
        prices = loader.pivot_close_prices()
        broker = get_broker()
        state = broker.load_state()
        latest_prices = broker.latest_prices(prices)
        equity_value = broker.account_value(state, latest_prices)
        return {
            "cash": state["cash"],
            "positions": state["positions"],
            "equity_value": round(equity_value, 2),
            "last_updated": state.get("last_updated"),
            "orders_count": len(state.get("order_history", [])),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/paper/orders")
def paper_orders() -> dict:
    try:
        broker = get_broker()
        state = broker.load_state()
        return {"order_history": state.get("order_history", [])}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/paper/reset")
def paper_reset() -> dict:
    try:
        broker = get_broker()
        state = broker.reset_account()
        return state
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/paper/rebalance-and-trade")
def paper_rebalance_and_trade() -> dict:
    try:
        loader = DataLoader(settings.data_path)
        prices = loader.pivot_close_prices()

        manager = PortfolioManager(
            benchmark=settings.benchmark,
            max_position_weight=settings.max_position_weight,
        )
        target_weights = manager.rebalance(prices)

        broker = get_broker()
        trading_service = TradingService(broker)
        result = trading_service.rebalance_to_target(prices, target_weights)

        return {
            "benchmark": settings.benchmark,
            **result,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
