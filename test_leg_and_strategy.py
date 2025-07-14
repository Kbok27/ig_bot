# strategies/strategy_trend_legs.py

import pandas as pd

def identify_trend_legs(df, min_leg_move=0.3, max_leg_gap=10):
    df = df.copy()
    df["SMA20"] = df["Close"].rolling(window=20).mean()
    df["SMA50"] = df["Close"].rolling(window=50).mean()

    legs = []
    current_leg = None

    for i in range(1, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i - 1]

        # Determine trend direction
        if row["SMA20"] > row["SMA50"]:
            direction = "up"
        elif row["SMA20"] < row["SMA50"]:
            direction = "down"
        else:
            continue

        # Start a new leg if direction changed
        if current_leg is None or current_leg["direction"] != direction:
            if current_leg is not None:
                current_leg["end_index"] = i - 1
                current_leg["end_time"] = df.index[i - 1]
                current_leg["length"] = current_leg["end_index"] - current_leg["start_index"]
                current_leg["magnitude"] = abs(df["Close"].iloc[current_leg["end_index"]] - df["Close"].iloc[current_leg["start_index"]])
                if current_leg["magnitude"] >= min_leg_move:
                    legs.append(current_leg)

            current_leg = {
                "direction": direction,
                "start_index": i,
                "start_time": df.index[i]
            }

        # Check leg gap
        if current_leg is not None:
            gap = i - current_leg["start_index"]
            if gap > max_leg_gap:
                current_leg["end_index"] = i - 1
                current_leg["end_time"] = df.index[i - 1]
                current_leg["length"] = current_leg["end_index"] - current_leg["start_index"]
                current_leg["magnitude"] = abs(df["Close"].iloc[current_leg["end_index"]] - df["Close"].iloc[current_leg["start_index"]])
                if current_leg["magnitude"] >= min_leg_move:
                    legs.append(current_leg)
                current_leg = None

    # Final leg
    if current_leg is not None and "end_index" not in current_leg:
        current_leg["end_index"] = len(df) - 1
        current_leg["end_time"] = df.index[-1]
        current_leg["length"] = current_leg["end_index"] - current_leg["start_index"]
        current_leg["magnitude"] = abs(df["Close"].iloc[current_leg["end_index"]] - df["Close"].iloc[current_leg["start_index"]])
        if current_leg["magnitude"] >= min_leg_move:
            legs.append(current_leg)

    return legs
