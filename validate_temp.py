# utils/validate.py

def validate_csv_columns(df, required_columns, filename="(unknown file)"):
    """
    Validates that the DataFrame has all required columns.
    Raises a ValueError with details if any are missing.
    """
    actual_cols = list(df.columns)
    missing_cols = [col for col in required_columns if col not in actual_cols]

    print(f"[DEBUG] Columns in '{filename}': {actual_cols}")

    if missing_cols:
        raise ValueError(
            f"[❌] Missing required columns in '{filename}': {missing_cols}\n"
            f"[💡] Found columns: {actual_cols}"
        )


def validate_ohlc_v2(df, filename="(unknown file)"):
    """
    Ensures that OHLC values are sane (High >= Open/Close >= Low).
    """
    if df.empty:
        raise ValueError(f"[❌] No data in {filename}")

    bad_rows = df[
        (df["High"] < df["Open"]) |
        (df["High"] < df["Close"]) |
        (df["Low"] > df["Open"]) |
        (df["Low"] > df["Close"]) |
        (df["Low"] > df["High"])
    ]

    if not bad_rows.empty:
        raise ValueError(
            f"[❌] Found {len(bad_rows)} malformed OHLC bars in {filename}"
        )
