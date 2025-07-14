# File: state_manager.py

import json
import os

STATE_FILE = 'bot_state.json'

def load_state() -> dict:
    """Load the persistent state (or return defaults if missing)."""
    if not os.path.isfile(STATE_FILE):
        return {
            "last_equity": None,
            "last_timestamp": None,
            "optimized_params": {}
        }
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_state(state: dict):
    """Write the state back to disk."""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, default=str)
