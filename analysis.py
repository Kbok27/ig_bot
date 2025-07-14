# %%  
# Cell 1: Imports and configuration  
import sqlite3  
import pandas as pd  
import matplotlib.pyplot as plt  
# Path to your SQLite database  
DB_PATH = 'centralized/results/test_master_summary.db'  

# %%  
# Cell 2: Load data  
conn = sqlite3.connect(DB_PATH)  
summary_df = pd.read_sql_query('SELECT * FROM trades', conn)  
conn.close()  
print(summary_df.head())

# %%  
# Cell 3: Compute performance by symbol  
stats = summary_df.groupby('symbol').agg(  
    total_trades=('return','count'),  
    winning_trades=('return',lambda x:(x>0).sum()),  
    win_rate=('return',lambda x:(x>0).mean()),  
    total_return=('return','sum'),  
    avg_return=('return','mean'),  
    max_drawdown=('drawdown','max')  
).reset_index()  
print(stats)

# %%  
# Cell 4: Plot total return  
plt.figure(figsize=(8,4))  
plt.bar(stats['symbol'], stats['total_return'])  
plt.title('Total Return by Symbol')  
plt.ylabel('Total Return')  
plt.xlabel('Symbol')  
plt.xticks(rotation=45)  
plt.show()

# %%  
# Cell 5: Equity curve for one symbol  
symbol = stats['symbol'].iloc[0]  
conn = sqlite3.connect(DB_PATH)  
df = pd.read_sql_query('SELECT time,balance FROM trades WHERE symbol=? ORDER BY time',  
                       conn, params=(symbol,))  
conn.close()  
df['time'] = pd.to_datetime(df['time'])  
df.set_index('time', inplace=True)  
plt.figure(figsize=(8,4))  
plt.plot(df.index, df['balance'], marker='o')  
plt.title(f'Equity Curve: {symbol}')  
plt.ylabel('Balance')  
plt.xlabel('Time')  
plt.xticks(rotation=45)  
plt.show()
