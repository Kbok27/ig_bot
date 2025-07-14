# File: live_dashboard.py
from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
from pathlib import Path

from utils import get_data
from strategies.strategy_sma_stoch_rr_v2 import backtest

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# Directories
RESULTS_DIR   = Path("results")
DASHBOARD_DIR = Path("static/dashboards")
THUMB_DIR     = Path("static/thumbnails")

@app.route("/")
def index():
    # Render the main dashboard page
    return render_template("index.html")

@app.route("/api/gallery")
def api_gallery():
    """
    Return JSON list of dashboard items with core stats:
      - symbol
      - trade_count
      - bars (number of candles)
      - total_pnl
      - avg_win
      - avg_loss
      - dashboard_url
      - thumbnail_url
    """
    min_trades = int(request.args.get("min_trades", 0))
    records = []

    # Iterate through all summary JSON files
    for summary_file in RESULTS_DIR.glob("*_summary.json"):
        symbol      = summary_file.stem.replace("_summary", "")
        trades_file = RESULTS_DIR / f"{symbol}_trades.csv"

        # Initialize stats
        trade_count = 0
        total_pnl   = 0.0
        avg_win     = 0.0
        avg_loss    = 0.0
        bars        = None

        # Load trades if file exists
        if trades_file.exists():
            df_trades   = pd.read_csv(trades_file)
            trade_count = len(df_trades)

            # Compute pnl column if missing
            if (
                'pnl' not in df_trades.columns
                and 'entry_price' in df_trades.columns
                and 'exit_price' in df_trades.columns
            ):
                df_trades['pnl'] = df_trades['exit_price'] - df_trades['entry_price']

            # Aggregate PnL, wins, losses
            if 'pnl' in df_trades.columns:
                total_pnl = df_trades['pnl'].sum()
                wins      = df_trades[df_trades['pnl'] > 0]['pnl']
                losses    = df_trades[df_trades['pnl'] <= 0]['pnl']
                avg_win   = wins.mean()  if not wins.empty   else 0.0
                avg_loss  = losses.mean() if not losses.empty else 0.0

        # Load summary JSON and normalize
        raw = json.loads(summary_file.read_text())
        if isinstance(raw, list):
            summary_data = raw[0] if raw else {}
        else:
            summary_data = raw
        bars = summary_data.get('bars', bars)

        # Skip entries without a valid bars count
        if bars is None:
            continue

        # Only include items meeting the min_trades threshold
        if trade_count >= min_trades:
            records.append({
                'symbol':        symbol,
                'trade_count':   trade_count,
                'bars':          bars,
                'total_pnl':     total_pnl,
                'avg_win':       avg_win,
                'avg_loss':      avg_loss,
                'dashboard_url': f"/static/dashboards/{symbol}_dashboard.html",
                'thumbnail_url': f"/static/thumbnails/{symbol}.png"
            })

    return jsonify(records)

@app.route("/api/run_job", methods=["POST"])
def api_run_job():
    """
    Run a single backtest via the UI and save its results.
    Expects JSON body:
      - symbol
      - timeframe
      - bars
      - strategy_kwargs (dict)
    Returns: { 'symbol': symbol }
    """
    job    = request.get_json()
    symbol = job['symbol']
    tf     = job['timeframe']
    bars   = job['bars']
    params = job.get('strategy_kwargs', {})

    df      = get_data(symbol, tf, bars)
    summary, trades = backtest(df, **params)

    RESULTS_DIR.mkdir(exist_ok=True)

    trades_file = RESULTS_DIR / f"{symbol}_trades.csv"
    pd.DataFrame(trades).to_csv(trades_file, index=False)

    summary_file = RESULTS_DIR / f"{symbol}_summary.json"
    out_summary  = {**summary, 'bars': bars}
    summary_file.write_text(json.dumps(out_summary, indent=2))

    return jsonify({"symbol": symbol})

if __name__ == "__main__":
    RESULTS_DIR.mkdir(exist_ok=True)
    app.run(debug=True)
