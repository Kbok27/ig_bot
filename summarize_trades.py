# summarize_trades.py
import sys
import pandas as pd
from utils.db_utils import get_all_symbols_summary, get_overall_summary

def main(db_file):
    # Fetch overall summary
    overall = get_overall_summary(db_file)
    # Fetch per-symbol breakdown
    df_by_symbol = get_all_symbols_summary(db_file)

    # Format floats nicely
    pd.set_option('display.float_format', lambda x: f"{x:,.2f}")

    # Print overall metrics
    print("\n=== Overall Performance ===\n")
    if overall.empty:
        print("No trades found in database.")
    else:
        # Turn Series into a one-row DataFrame for prettier printing
        print(overall.to_frame().T.to_string(index=False))

    # Print per-symbol table
    print("\n=== Trade Performance by Symbol ===\n")
    if df_by_symbol.empty:
        print("No symbol-level trades found.")
        sys.exit(1)
    print(df_by_symbol.to_string(index=False))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python summarize_trades.py <path/to/trades.db>")
        sys.exit(1)
    main(sys.argv[1])
