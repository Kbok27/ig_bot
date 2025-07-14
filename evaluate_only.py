import pandas as pd
import numpy as np

def evaluate_trades(trades, initial_equity=1000):
    if not trades:
        return {
            "win_rate": 0,
            "avg_return": 0,
            "sharpe_ratio": 0,
            "final_equity": initial_equity,
        }

    df = pd.DataFrame(trades)
    df["pnl"] = df["profit"]

    equity = initial_equity + df["pnl"].cumsum()
    returns = df["pnl"] / initial_equity

    win_rate = (df["pnl"] > 0).mean()
    avg_return = returns.mean()

    sharpe = returns.mean() / (returns.std() + 1e-9) * np.sqrt(252) if len(returns) > 1 else 0

    return {
        "win_rate": win_rate,
        "avg_return": avg_return,
        "sharpe_ratio": sharpe,
        "final_equity": equity.iloc[-1],
    }
