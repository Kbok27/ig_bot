# File: visualize_trades.py

import argparse
import os

import pandas as pd
import matplotlib.pyplot as plt

from utils.data_utils import get_data

def plot_trades_for_config(df, trades_df, symbol, config_idx):
    """
    Overlay each trade on the price chart:
      • entry markers (▲)
      • horizontal lines for SL and TP
    """
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Close')

    # Which columns hold our trade data?
    time_col  = 'entry_time'
    price_col = 'entry_price'
    sl_col    = 'stop_loss'
    tp_col    = 'take_profit'

    sl_plotted = False
    tp_plotted = False

    for i, trade in trades_df.iterrows():
        et = pd.to_datetime(trade[time_col])
        ep = trade[price_col]
        sl = trade[sl_col]
        tp = trade[tp_col]

        # entry arrow
        plt.scatter(et, ep, marker='^', s=100, label='Entry' if i == 0 else "")

        # stop-loss line
        if not sl_plotted:
            plt.hlines(sl, df.index[0], df.index[-1], linestyles='dashed', label='Stop Loss')
            sl_plotted = True
        else:
            plt.hlines(sl, df.index[0], df.index[-1], linestyles='dashed')

        # take-profit line
        if not tp_plotted:
            plt.hlines(tp, df.index[0], df.index[-1], linestyles='dotted', label='Take Profit')
            tp_plotted = True
        else:
            plt.hlines(tp, df.index[0], df.index[-1], linestyles='dotted')

    plt.title(f"{symbol} – Trades (Config #{config_idx})")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.tight_layout()

    outpath = f"plots/{symbol}_config_{config_idx}.png"
    os.makedirs("plots", exist_ok=True)
    plt.savefig(outpath)
    plt.close()
    print(f"✅ Saved trade-overlay chart to {outpath}")

def main():
    parser = argparse.ArgumentParser(
        description="Visualize your trade logs on price charts"
    )
    parser.add_argument(
        "--symbols", nargs="+",
        default=["BTCUSD.a"],
        help="List of MT5 symbols you ran"
    )
    parser.add_argument(
        "--configs", type=int, nargs="+",
        default=[1, 2],
        help="Which config indices to plot (e.g. 1 2)"
    )
    parser.add_argument(
        "--timeframe", type=int, default=2,
        help="Bar timeframe in minutes"
    )
    parser.add_argument(
        "--bars", type=int, default=1000,
        help="Number of bars you fetched"
    )
    parser.add_argument(
        "--results-dir", type=str, default="results",
        help="Directory where your *_result_*.csv files live"
    )
    args = parser.parse_args()

    for symbol in args.symbols:
        # reload price data for this symbol
        df = get_data(symbol=symbol, timeframe=args.timeframe, bars=args.bars)
        for idx in args.configs:
            csv_path = os.path.join(args.results_dir, f"{symbol}_result_{idx}.csv")
            if not os.path.isfile(csv_path):
                print(f"⚠️  Missing {csv_path}, skipping…")
                continue

            trades_df = pd.read_csv(csv_path)
            plot_trades_for_config(df, trades_df, symbol, idx)

if __name__ == "__main__":
    main()
