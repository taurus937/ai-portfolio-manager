from pprint import pprint

from config.settings import settings
from services.backtest import Backtester
from services.data_loader import DataLoader


if __name__ == "__main__":
    loader = DataLoader(settings.data_path)
    prices = loader.pivot_close_prices()
    backtester = Backtester(benchmark=settings.benchmark)
    results = backtester.run(prices)
    pprint({k: v for k, v in results.items() if k != "history"})
