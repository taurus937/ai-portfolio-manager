from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os

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


@app.get("/health")
def health():
    send_telegram("Strategy executed")

    return {"status": "ok"}

@app.post("/alpaca/strategy-trade")
def strategy_trade():
    return {
        "status": "strategy_executed",
        "mode": "manual",
        "orders": []
    }

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
    <!doctype html>
    <html>
    <head>
      <title>AI Portfolio Dashboard</title>
      <style>
        body { font-family: Arial, sans-serif; background:#0f172a; color:white; margin:0; padding:40px; }
        .wrap { max-width:900px; margin:0 auto; }
        .card { background:#111827; border:1px solid #334155; border-radius:16px; padding:20px; margin-bottom:20px; }
        button { background:white; color:black; border:none; padding:12px 18px; border-radius:10px; cursor:pointer; font-weight:600; }
        pre { background:#020617; padding:16px; border-radius:12px; overflow:auto; }
        h1,h2 { margin-top:0; }
      </style>
    </head>
    <body>
      <div class="wrap">
        <h1>AI Portfolio Dashboard</h1><div class="card"><h2>Account</h2><button onclick="loadAccount()">Load Account</button><pre id="accountBox">Click to load account.</pre></div>

        <div class="card">
          <h2>Run Strategy</h2>
        </div>

        <div class="card">
          <h2>Positions</h2>
        </div>

        <div class="card">
          <h2>P&L</h2>
        </div>

        <div class="card">
          <h2>Trade History</h2>
          <button onclick="loadTrades()">Load Trades</button>
          <pre id="tradesBox">Click to load trades.</pre>
        </div>

        <div class="card">
        </div>

        <div class="card">
          <h2>Trade History</h2>
          <button onclick="loadTrades()">Load Trades</button>
          <pre id="tradesBox">Click to load trades.</pre>
        </div>

        <div class="card">
          <button onclick="loadPnL()">Load P&L</button>
          <pre id="pnlBox">Click to load P&L.</pre>
        </div>

        <div class="card">
          <button onclick="loadPositions()">Load Positions</button>
          <pre id="positionsBox">Click to load positions.</pre>
        </div>

        <div class="card">
          <button onclick="runStrategy()">Execute Strategy Trade</button>
          <pre id="strategyBox">Click the button to run the strategy.</pre>
        </div>
      </div>

      <script>
        async function loadAccount() {
          const res = await fetch("/alpaca/account");
          const data = await res.json();
          document.getElementById("accountBox").textContent = JSON.stringify(data, null, 2);
        }

        async function loadTrades() {
          const res = await fetch("/alpaca/trades");
          const data = await res.json();
          document.getElementById("tradesBox").textContent = JSON.stringify(data, null, 2);
        }

        async function loadTrades() {
          const res = await fetch("/alpaca/trades");
          const data = await res.json();
          document.getElementById("tradesBox").textContent = JSON.stringify(data, null, 2);
        }

        async function loadPnL() {
          const res = await fetch("/alpaca/pnl");
          const data = await res.json();
          document.getElementById("pnlBox").textContent = JSON.stringify(data, null, 2);
        }

        async function loadPositions() {
          const res = await fetch("/alpaca/positions");
          const data = await res.json();
          document.getElementById("positionsBox").textContent = JSON.stringify(data, null, 2);
        }

        async function runStrategy() {
          const res = await fetch("/alpaca/strategy-trade", { method: "POST" });
          const data = await res.json();
          document.getElementById("strategyBox").textContent = JSON.stringify(data, null, 2);
        }
      </script>
    </body>
    </html>
    """


@app.get("/alpaca/account")
def alpaca_account():
    import os, requests
    url = os.getenv("ALPACA_BASE_URL") + "/v2/account"
    r = requests.get(
        url,
        headers={
            "APCA-API-KEY-ID": os.getenv("ALPACA_API_KEY"),
            "APCA-API-SECRET-KEY": os.getenv("ALPACA_SECRET_KEY"),
        },
        timeout=20,
    )
    data = r.json()
    return {
        "status": data.get("status"),
        "cash": data.get("cash"),
        "portfolio_value": data.get("portfolio_value"),
        "buying_power": data.get("buying_power"),
    }




@app.get("/alpaca/positions")
def alpaca_positions():
    import os, requests
    url = os.getenv("ALPACA_BASE_URL") + "/v2/positions"
    r = requests.get(
        url,
        headers={
            "APCA-API-KEY-ID": os.getenv("ALPACA_API_KEY"),
            "APCA-API-SECRET-KEY": os.getenv("ALPACA_SECRET_KEY"),
        },
        timeout=20,
    )
    return r.json()


@app.get("/alpaca/pnl")
def alpaca_pnl():
    import os, requests

    headers = {
        "APCA-API-KEY-ID": os.getenv("ALPACA_API_KEY"),
        "APCA-API-SECRET-KEY": os.getenv("ALPACA_SECRET_KEY"),
    }

    base = os.getenv("ALPACA_BASE_URL")

    acc = requests.get(base + "/v2/account", headers=headers, timeout=20).json()
    pos = requests.get(base + "/v2/positions", headers=headers, timeout=20).json()

    total_market_value = sum(float(p["market_value"]) for p in pos) if pos else 0

    return {
        "portfolio_value": acc.get("portfolio_value"),
        "cash": acc.get("cash"),
        "positions_market_value": round(total_market_value, 2),
        "positions": pos
    }


@app.get("/alpaca/trades")
def alpaca_trades():
    import os, requests

    headers = {
        "APCA-API-KEY-ID": os.getenv("ALPACA_API_KEY"),
        "APCA-API-SECRET-KEY": os.getenv("ALPACA_SECRET_KEY"),
    }

    base = os.getenv("ALPACA_BASE_URL")
    r = requests.get(base + "/v2/orders?status=all&limit=20", headers=headers, timeout=20)
    data = r.json()

    return [
        {
            "symbol": o.get("symbol"),
            "side": o.get("side"),
            "qty": o.get("qty"),
            "status": o.get("status"),
            "filled_avg_price": o.get("filled_avg_price"),
            "created_at": o.get("created_at"),
        }
        for o in data
    ]
