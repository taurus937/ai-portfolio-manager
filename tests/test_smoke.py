from pathlib import Path

from services.backtest import Backtester
from services.data_loader import DataLoader
from services.paper_broker import PaperBroker, PaperBrokerConfig
from services.portfolio import PortfolioManager
from services.trading import TradingService


def test_rebalance_runs():
    csv_path = Path("data/sample_prices.csv")
    loader = DataLoader(str(csv_path))
    prices = loader.pivot_close_prices()
    manager = PortfolioManager(benchmark="SPY")
    weights = manager.rebalance(prices)
    assert isinstance(weights, dict)


def test_backtest_runs():
    csv_path = Path("data/sample_prices.csv")
    loader = DataLoader(str(csv_path))
    prices = loader.pivot_close_prices()
    backtester = Backtester(benchmark="SPY")
    results = backtester.run(prices)
    assert "cumulative_return" in results
    assert "history" in results


def test_paper_broker_executes_orders(tmp_path):
    csv_path = Path("data/sample_prices.csv")
    loader = DataLoader(str(csv_path))
    prices = loader.pivot_close_prices()

    broker = PaperBroker(
        PaperBrokerConfig(
            state_path=str(tmp_path / "paper_account.json"),
            initial_cash=100000,
        )
    )
    trading = TradingService(broker)
    target_weights = {"QQQ": 0.5, "XLF": 0.5}
    result = trading.rebalance_to_target(prices, target_weights)

    assert "orders" in result
    assert "account_after" in result
    assert result["account_after"]["positions"]
