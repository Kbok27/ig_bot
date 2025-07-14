# File: backtester.py

import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime
from typing import List, Optional, Tuple
from strategies.strategy_sma_stoch_rr_v2 import run_strategy

def backtest(
    symbol: str,
    timeframe: int,
    bars: int,
    oversold_threshold: int,
    sweep_thresholds: Optional[List[int]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Run a vanilla backtest and optional threshold sweep all in-process.

    Args:
        symbol: MT5 instrument (e.g. "NAS100.a").
        timeframe: minutes (1,5,15,30,60,240,1440).
        bars: number of bars to fetch.
        oversold_threshold: percent for vanilla backtest.
        sweep_thresholds: list of thresholds to sweep (None to skip).

    Returns:
        equity_df, trades_df, sweep_summary_df
    """
    # Initialize MT5 and fetch data
    if not mt5.initialize():
        raise RuntimeError(f"MT5 init failed: {mt5.last_error()}")

    # Map timeframe (240m is H4)
    tf_attr = f"TIMEFRAME_M{timeframe}" if timeframe != 240 else "TIMEFRAME_H4"
    tf = getattr(mt5, tf_attr, mt5.TIMEFRAME_M5)
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, bars)
    mt5.shutdown()

    # Build DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    df.rename(columns={'high': 'High', 'low': 'Low', 'close': 'Close'}, inplace=True)

    # Base strategy parameters
    common = dict(
        fast_sma=10,
        slow_sma=50,
        stoch_k=14,
        stoch_d=3,
        atr_period=14,
        atr_multiplier=1.5,
        reward_ratio=2.0,
        risk_per_trade=0.01,
        starting_balance=100_000,
        pip_size=1.0
    )

    # Vanilla backtest
    eq_df, tr_df = run_strategy(
        df,
        **common,
        stoch_oversold_threshold=oversold_threshold,
        sweep_thresholds=None
    )

    # Threshold sweep if requested
    if sweep_thresholds is not None:
        _, _, sweep_df = run_strategy(
            df,
            **common,
            stoch_oversold_threshold=oversold_threshold,
            sweep_thresholds=sweep_thresholds
        )
    else:
        sweep_df = pd.DataFrame()

    return eq_df, tr_df, sweep_df
