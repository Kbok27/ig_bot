import sys
import json
import traceback
from datetime import datetime

import MetaTrader5 as mt5
import pandas as pd

from alerts import slack_alert, email_alert

# Load optimized parameters
with open('best_params.json', 'r') as f:
    params = json.load(f)

SYMBOL        = params['symbol']
TP            = params['take_profit_pips']
ATR_STOP_MULT = params['atr_stop_multiplier']
PIP_FACTORS   = params['pip_factors']
BARS          = params.get('bars', 10000)
LOT_SIZE      = params.get('lot_size', 1.0)

# Circuit breaker settings
daily_pnl      = 0.0
DAILY_MAX_LOSS = params.get('daily_max_loss', -100.0)

# Live trade log filename
LIVE_LOG_FILE = 'live_trade_log.csv'


def get_data(symbol, timeframe, bars):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    if rates is None or len(rates) == 0:
        raise RuntimeError("No data returned from MT5")
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','tick_volume':'Volume'}, inplace=True)
    return df


def main():
    global daily_pnl

    # dynamic import to avoid circular issues
    from strategies.strategy_sma_stoch_rr_v2 import run_strategy

    # 1) Initialize MT5
    if not mt5.initialize():
        print(f"[❌] MT5 init failed: {mt5.last_error()}")
        sys.exit(1)
    print("[✅] MT5 initialized")

    try:
        # 2) Fetch data
        print(f"[INFO] Fetching {BARS} bars for {SYMBOL} @ M5…")
        df = get_data(SYMBOL, mt5.TIMEFRAME_M5, BARS)
        print(f"[✅] Got {len(df)} rows")

        # 3) Run strategy (live orders inside)
        results = run_strategy(
            df,
            take_profit_pips=TP,
            stop_loss_pips=int(TP * ATR_STOP_MULT),
            pip_factor=PIP_FACTORS[SYMBOL],
            use_atr_stop=True,
            atr_stop_multiplier=ATR_STOP_MULT,
            atr_period=params.get('atr_period',10),
            atr_multiplier=params.get('atr_multiplier',1.0),
            sma50_distance_pips=params.get('sma50_distance_pips',30),
            min_candle_size_pips=params.get('min_candle_size_pips',0.5),
            min_leg_move=params.get('min_leg_move',0.3),
            max_leg_gap=params.get('max_leg_gap',10),
            initial_equity=params.get('initial_equity',1000.0),
            symbol=SYMBOL,
            lot_size=LOT_SIZE
        )

        # 4) Circuit breaker: sum PnL of all closed trades
        trades = results['trade_log']
        daily_pnl += trades.loc[trades['status']=='closed','profit'].sum()
        if daily_pnl <= DAILY_MAX_LOSS:
            msg = f"Daily PnL {daily_pnl:.2f} <= limit {DAILY_MAX_LOSS}, halting trading."
            slack_alert(msg)
            email_alert("Circuit Breaker Triggered", msg)
            sys.exit(0)

        # 5) Print performance summary
        wins   = results['wins']
        losses = results['losses']
        total  = wins + losses
        win_rate = wins / total if total else 0

        avg_win  = trades.loc[trades['profit']>0,'profit'].mean()  or 0
        avg_loss = trades.loc[trades['profit']<=0,'profit'].mean() or 0
        pf       = trades.loc[trades['profit']>0,'profit'].sum() / abs(trades.loc[trades['profit']<=0,'profit'].sum() or 1)
        expct    = win_rate * avg_win + (1 - win_rate) * avg_loss
        achieved_rr = (avg_win / abs(avg_loss)) if avg_loss else float('inf')
        target_rr   = TP / (TP * ATR_STOP_MULT)

        print(f"[SUMMARY] Trades: {total}  Wins: {wins}  Losses: {losses}  Win Rate: {win_rate:.2%}")
        print(f"[STATS] Avg Win: {avg_win:.4f}  Avg Loss: {avg_loss:.4f}")
        print(f"[METRICS] PF: {pf:.2f}  Expectancy: {expct:.4f}  R:R {achieved_rr:.2f}:1 (Target {target_rr:.2f}:1)")

        # 6) Save the live trade log for dashboarding
        if not trades.empty:
            trades.to_csv(LIVE_LOG_FILE, index=False)
            print(f"[ℹ️] Live trade log saved to {LIVE_LOG_FILE}")
        else:
            print(f"[⚠️] No trades executed; {LIVE_LOG_FILE} not updated.")

    except Exception:
        tb = traceback.format_exc()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[❌] Crash during run:\n{tb}")
        with open('crash.log', 'a') as f:
            f.write(f"--- Crash @ {ts} ---\n{tb}\n")
        sys.exit(1)

    finally:
        mt5.shutdown()
        print("[ℹ️] MT5 shutdown complete")

if __name__ == '__main__':
    main()
