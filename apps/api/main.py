from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os
import requests

load_dotenv(".env", override=True)

app = FastAPI()

RUNTIME_DRY_RUN = {"value": True}


def alpaca_headers():
    return {
        "APCA-API-KEY-ID": os.getenv("ALPACA_API_KEY"),
        "APCA-API-SECRET-KEY": os.getenv("ALPACA_SECRET_KEY"),
    }


def alpaca_base():
    return os.getenv("ALPACA_BASE_URL")


def send_telegram(msg):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": msg},
            timeout=10,
        )
    except Exception:
        pass


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/alpaca/account")
def alpaca_account():
    r = requests.get(
        alpaca_base() + "/v2/account",
        headers=alpaca_headers(),
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
    r = requests.get(
        alpaca_base() + "/v2/positions",
        headers=alpaca_headers(),
        timeout=20,
    )
    return r.json()


@app.get("/alpaca/pnl")
def alpaca_pnl():
    acc = requests.get(
        alpaca_base() + "/v2/account",
        headers=alpaca_headers(),
        timeout=20,
    ).json()
    pos = requests.get(
        alpaca_base() + "/v2/positions",
        headers=alpaca_headers(),
        timeout=20,
    ).json()

    total_market_value = sum(float(p["market_value"]) for p in pos) if pos else 0

    return {
        "portfolio_value": acc.get("portfolio_value"),
        "cash": acc.get("cash"),
        "positions_market_value": round(total_market_value, 2),
        "positions": pos,
    }


@app.get("/alpaca/trades")
def alpaca_trades():
    r = requests.get(
        alpaca_base() + "/v2/orders?status=all&limit=20",
        headers=alpaca_headers(),
        timeout=20,
    )
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


@app.get("/toggle")
def get_toggle():
    return {"dry_run": RUNTIME_DRY_RUN["value"]}


@app.post("/toggle/on")
def toggle_on():
    RUNTIME_DRY_RUN["value"] = True
    send_telegram("Dry Run turned ON")
    return {"dry_run": RUNTIME_DRY_RUN["value"]}


@app.post("/toggle/off")
def toggle_off():
    RUNTIME_DRY_RUN["value"] = False
    send_telegram("Dry Run turned OFF")
    return {"dry_run": RUNTIME_DRY_RUN["value"]}


@app.post("/alpaca/strategy-trade")
def strategy_trade():
    send_telegram(f"Strategy executed | dry_run={RUNTIME_DRY_RUN['value']}")
    return {
        "status": "strategy_executed",
        "mode": "manual",
        "orders": [],
        "dry_run": RUNTIME_DRY_RUN["value"],
    }


@app.get("/debug/telegram")
def debug_telegram():
    return {
        "has_token": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
        "has_chat_id": bool(os.getenv("TELEGRAM_CHAT_ID")),
        "token_len": len(os.getenv("TELEGRAM_BOT_TOKEN") or ""),
        "chat_id": os.getenv("TELEGRAM_CHAT_ID"),
    }


@app.get("/debug/test-telegram")
def test_telegram():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    r = requests.post(url, json={"chat_id": chat_id, "text": "Test message from Render app"}, timeout=10)
    return {"status_code": r.status_code, "text": r.text[:1000]}


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
        button { background:white; color:black; border:none; padding:12px 18px; border-radius:10px; cursor:pointer; font-weight:600; margin-right:10px; margin-bottom:10px; }
        pre { background:#020617; padding:16px; border-radius:12px; overflow:auto; white-space:pre-wrap; }
        h1,h2 { margin-top:0; }
      </style>
    </head>
    <body>
      <div class="wrap">
        <h1>AI Portfolio Dashboard</h1>
        <div id="modeBanner" style="margin:20px 0;padding:15px;border-radius:12px;font-weight:bold;">Loading mode...</div>

        <div class="card">
          <h2>Account</h2>
          <button onclick="loadAccount()">Load Account</button>
          <pre id="accountBox">Click to load account.</pre>
        </div>

        <div class="card">
          <h2>Positions</h2>
          <button onclick="loadPositions()">Load Positions</button>
          <pre id="positionsBox">Click to load positions.</pre>
        </div>

        <div class="card">
          <h2>P&L</h2>
          <button onclick="loadPnL()">Load P&L</button>
          <pre id="pnlBox">Click to load P&L.</pre>
        </div>

        <div class="card">
          <h2>Trade History</h2>
          <button onclick="loadTrades()">Load Trades</button>
          <pre id="tradesBox">Click to load trades.</pre>
        </div>

        <div class="card">
          <h2>Dry Run Toggle</h2>
          <button onclick="showToggle()">Show Mode</button>
          <button onclick="toggleOn()">Dry Run ON</button>
          <button onclick="toggleOff()">Dry Run OFF</button>
          <pre id="toggleBox">Click to view or change mode.</pre>
        </div>

        <div class="card">
          <h2>Run Strategy</h2>
          <button onclick="runStrategy()"><span id="runBtnText">Execute Strategy Trade</span></button>
          <pre id="strategyBox">Click the button to run the strategy.</pre>
        </div>
      </div>

      <script>
        async function loadAccount() {
          const res = await fetch("/alpaca/account");
          const data = await res.json();
          document.getElementById("accountBox").textContent = JSON.stringify(data, null, 2);
        }

        async function loadPositions() {
          const res = await fetch("/alpaca/positions");
          const data = await res.json();
          document.getElementById("positionsBox").textContent = JSON.stringify(data, null, 2);
        }

        async function loadPnL() {
          const res = await fetch("/alpaca/pnl");
          const data = await res.json();
          document.getElementById("pnlBox").textContent = JSON.stringify(data, null, 2);
        }

        async function loadTrades() {
          const res = await fetch("/alpaca/trades");
          const data = await res.json();
          document.getElementById("tradesBox").textContent = JSON.stringify(data, null, 2);
        }

        async function showToggle() {
          const btn = document.getElementById("runBtnText");
          const res = await fetch("/toggle");
          const data = await res.json();
          document.getElementById("toggleBox").textContent = JSON.stringify(data, null, 2);
          const banner = document.getElementById("modeBanner");
          if (data.dry_run) {
            banner.textContent = "SAFE MODE: DRY RUN ON";
            banner.style.background = "#14532d";
            banner.style.color = "#dcfce7";
            btn.textContent = "Preview Strategy Trade";
          } else {
            banner.textContent = "LIVE PAPER TRADING: DRY RUN OFF";
            banner.style.background = "#7f1d1d";
            banner.style.color = "#fee2e2";
            btn.textContent = "Execute LIVE Paper Trade";
          }
        }

        async function toggleOn() {
          const res = await fetch("/toggle/on", { method: "POST" });
          const data = await res.json();
          document.getElementById("toggleBox").textContent = JSON.stringify(data, null, 2);
          await showToggle();
        }

        async function toggleOff() {
          const res = await fetch("/toggle/off", { method: "POST" });
          const data = await res.json();
          document.getElementById("toggleBox").textContent = JSON.stringify(data, null, 2);
          await showToggle();
        }

        async function runStrategy() {
          const res = await fetch("/alpaca/strategy-trade", { method: "POST" });
          const data = await res.json();
          document.getElementById("strategyBox").textContent = JSON.stringify(data, null, 2);
        }

        showToggle();
      </script>
    </body>
    </html>
    """
