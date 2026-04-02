from fastapi import FastAPI
from dotenv import load_dotenv
import os
import alpaca_trade_api as tradeapi

load_dotenv(".env", override=True)

app = FastAPI()


def send_telegram(msg):
    import os, requests
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": msg}, timeout=10)
    except:
        pass


def send_telegram(msg):
    import os, requests
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": msg}, timeout=10)
    except:
        pass



TICKERS = ["SPY","QQQ","XLF","XLV","XLI"]
DEFENSIVE = ["TLT","GLD"]
TOP_N = 3
MAX_PER_TRADE = 5000
DRY_RUN = True

# runtime toggle
RUNTIME_DRY_RUN = {"value": True}

def get_api():
    return tradeapi.REST(
        os.getenv("ALPACA_API_KEY"),
        os.getenv("ALPACA_SECRET_KEY"),
        os.getenv("ALPACA_BASE_URL"),
    )

@app.get("/health")
def health():
    return {"status": "ok"}

def momentum(api, ticker):
    bars = api.get_bars(ticker, "1Day", limit=60).df
    if len(bars) == 0:
        return 0
    start = bars["close"].iloc[0]
    end = bars["close"].iloc[-1]
    return (end - start) / start

@app.post("/alpaca/strategy-trade")
def strategy_trade():
    try:
        send_telegram("Strategy executed from dashboard")
        return {
            "status": "strategy_executed",
            "mode": "manual",
            "orders": []
        }
    except Exception as e:
        return {"error": str(e)}


