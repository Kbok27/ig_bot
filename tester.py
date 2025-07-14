import pandas as pd
from strategies import sma_stochastic_v3 as strategy

def run_mock_test(file_path):
    df = pd.read_csv(file_path, parse_dates=['Date'], index_col='Date')
    df['sma_short'] = df['Close'].rolling(window=3).mean()
    df['sma_long'] = df['Close'].rolling(window=7).mean()
    low_14 = df['Low'].rolling(window=14).min()
    high_14 = df['High'].rolling(window=14).max()
    df['%K'] = 100 * ((df['Close'] - low_14) / (high_14 - low_14))

    result_df = strategy.run_strategy(df.copy(), initial_equity=1000)
    return result_df

if __name__ == "__main__":
    result_df = run_mock_test("data/mock/mock_sma_stochastic_test.csv")
