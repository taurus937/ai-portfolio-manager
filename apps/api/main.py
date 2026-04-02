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

        async function runStrategy() {
          const res = await fetch("/alpaca/strategy-trade", { method: "POST" });
          const data = await res.json();
          document.getElementById("strategyBox").textContent = JSON.stringify(data, null, 2);
        }
      </script>
    </body>
    </html>
    """
