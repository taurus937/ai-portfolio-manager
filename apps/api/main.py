from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os

load_dotenv(".env", override=True)

app = FastAPI()

@app.get("/health")
def health():
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
