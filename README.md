# AI Portfolio Manager MVP

A simple MVP for an AI-assisted portfolio manager with:
- real market data support
- paper trading support
- data loading
- feature engineering
- regime classification
- signal ranking
- risk controls
- constrained portfolio construction
- backtesting
- API exposure

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Fetch market data

```bash
python fetch_market_data.py
```

## Run API

```bash
uvicorn apps.api.main:app --reload
```

## Paper trading flow

1. Refresh market data
2. Rebalance portfolio
3. Submit paper orders
4. View positions and order history

Example:

```bash
curl -X POST http://127.0.0.1:8000/market-data/refresh
curl http://127.0.0.1:8000/portfolio/rebalance
curl -X POST http://127.0.0.1:8000/paper/rebalance-and-trade
curl http://127.0.0.1:8000/paper/account
```

## Notes
This is an MVP scaffold, not production investment software.
Add proper brokerage integration, compliance checks, live market data validation,
monitoring, retries, audit controls, and extensive testing before any real deployment.
