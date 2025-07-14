# dashboard_app.py
"""
A simple Flask web dashboard to view overall and per-symbol trade statistics.
"""
from flask import Flask, render_template_string, abort
from utils.db_utils import get_all_symbols_summary, get_overall_summary, get_symbol_trades

app = Flask(__name__)

# HTML template for the main dashboard
template_index = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Trade Dashboard</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 40px; }
      table { border-collapse: collapse; width: 100%; margin-bottom: 40px; }
      th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
      th { background-color: #f2f2f2; }
      a { color: #007bff; text-decoration: none; }
      a:hover { text-decoration: underline; }
    </style>
  </head>
  <body>
    <h1>Overall Performance</h1>
    {% if overall.empty %}
      <p>No trades found.</p>
    {% else %}
      <table>
        <tr>
          {% for col in overall.index %}
            <th>{{ col.replace('_', ' ').title() }}</th>
          {% endfor %}
        </tr>
        <tr>
          {% for val in overall.values %}
            <td>{{ '%.2f'|format(val) }}</td>
          {% endfor %}
        </tr>
      </table>
    {% endif %}

    <h1>Symbol Breakdown</h1>
    {% if not summary_rows %}
      <p>No symbol-level trades found.</p>
    {% else %}
      <table>
        <tr>
          {% for col in summary_cols %}
            <th>{{ col.replace('_', ' ').title() }}</th>
          {% endfor %}
        </tr>
        {% for row in summary_rows %}
        <tr>
          <td><a href="/symbol/{{ row['symbol'] }}">{{ row['symbol'] }}</a></td>
          {% for key in summary_cols[1:] %}
            <td>{{ '%.2f'|format(row[key]) if key not in ['total_trades','winning_trades'] else row[key] }}</td>
          {% endfor %}
        </tr>
        {% endfor %}
      </table>
    {% endif %}
  </body>
</html>
'''

# HTML template for symbol detail
template_detail = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Detail for {{ symbol }}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
    th { background-color: #f2f2f2; }
  </style>
</head>
<body>
  <h1>Trades for {{ symbol }}</h1>
  <table>
    <tr><th>Time</th><th>Balance</th><th>Return</th><th>Drawdown</th></tr>
    {% for r in rows %}
      <tr>
        <td>{{ r.time }}</td>
        <td>{{ '%.2f'|format(r.balance) }}</td>
        <td>{{ '%.2f'|format(r.return) }}</td>
        <td>{{ '%.2f'|format(r.drawdown) }}</td>
      </tr>
    {% endfor %}
  </table>
  <p><a href="/">Back to Dashboard</a></p>
</body>
</html>
'''

@app.route('/')
def index():
    db_path = 'centralized/results/test_master_summary.db'
    overall = get_overall_summary(db_path)
    summary_df = get_all_symbols_summary(db_path)
    summary_rows = summary_df.to_dict(orient='records')
    summary_cols = summary_df.columns.tolist()
    return render_template_string(
        template_index,
        overall=overall,
        summary_rows=summary_rows,
        summary_cols=summary_cols
    )

@app.route('/symbol/<symbol>')
def symbol_detail(symbol):
    db_path = 'centralized/results/test_master_summary.db'
    df = get_symbol_trades(db_path, symbol)
    if df.empty:
        abort(404)
    rows = df.reset_index().to_dict(orient='records')
    return render_template_string(
        template_detail,
        symbol=symbol,
        rows=rows
    )

if __name__ == '__main__':
    app.run(debug=True)
