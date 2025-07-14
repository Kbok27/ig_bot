import os
import json
import time
import pandas as pd
from utils.data_utils import get_data

STATE_FILE      = "bot_state.json"
DEFAULT_BALANCE = 100_000.0

class BarFeed:
    """
    Stateful bar feed supporting both historical replay and real-time streaming.

    Modes:
    - 'replay': iterate once through historical bars up to full_bars.
    - 'live':  warm up with initial_window bars then poll for new bars.

    State persistence (bot_state.json) tracks:
      - last_ts:  ISO timestamp of the last processed bar
      - balance: current account balance
    """
    def __init__(self,
                 symbol: str,
                 timeframe: int = 5,
                 full_bars: int = 5000,
                 initial_window: int = 1000,
                 mode: str = 'replay',
                 delay: int = 5,
                 state_file: str = STATE_FILE):
        self.symbol         = symbol
        self.timeframe      = timeframe
        self.full_bars      = full_bars
        self.initial_window = initial_window
        self.mode           = mode
        self.delay          = delay
        self.state_file     = state_file

        # load or init state
        self.state = self._load_state()

        if self.mode == 'replay':
            # load full history once
            self.df_all  = get_data(symbol=symbol,
                                    timeframe=timeframe,
                                    bars=full_bars)
            # determine start index
            if self.state['last_ts']:
                last_dt = pd.to_datetime(self.state['last_ts'])
                self.next_idx = self.df_all.index.searchsorted(last_dt, side='right')
            else:
                self.next_idx = initial_window

        elif self.mode == 'live':
            # warm-up: load initial history
            self.df_hist = get_data(symbol=symbol,
                                    timeframe=timeframe,
                                    bars=initial_window)
            # update last_ts from history tail if not set
            if not self.state['last_ts'] and not self.df_hist.empty:
                self.state['last_ts'] = self.df_hist.index[-1].isoformat()
                self._save_state()
        else:
            raise ValueError(f"Unknown mode: {self.mode}")

    def _load_state(self) -> dict:
        if os.path.exists(self.state_file):
            raw = json.load(open(self.state_file))
            return {
                'last_ts': raw.get('last_ts', None),
                'balance': raw.get('balance', DEFAULT_BALANCE)
            }
        return {'last_ts': None, 'balance': DEFAULT_BALANCE}

    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def get_next_bar(self):
        """
        Returns the next bar as a pandas.Series, blocking until available in live mode,
        or None if replay is complete.
        """
        if self.mode == 'replay':
            if self.next_idx >= len(self.df_all):
                return None
            bar = self.df_all.iloc[self.next_idx]
            # update state
            ts = bar.name
            self.state['last_ts'] = ts.isoformat()
            self._save_state()
            self.next_idx += 1
            return bar

        # live mode: poll until a new bar appears
        while True:
            df = get_data(symbol=self.symbol,
                          timeframe=self.timeframe,
                          bars=self.full_bars)
            last_ts = pd.to_datetime(self.state['last_ts']) if self.state['last_ts'] else None
            new_bars = df[df.index > last_ts] if last_ts is not None else df
            if not new_bars.empty:
                bar = new_bars.iloc[0]
                ts = bar.name
                self.state['last_ts'] = ts.isoformat()
                self._save_state()
                return bar
            time.sleep(self.delay)

    def get_balance(self) -> float:
        """Return the current balance."""
        return self.state['balance']

    def update_balance(self, new_balance: float):
        """Persist a new balance value."""
        self.state['balance'] = new_balance
        self._save_state()
