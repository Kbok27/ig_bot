import matplotlib.pyplot as plt
import numpy as np

def plot_equity_and_drawdown_together(equity_curve, symbol="Symbol"):
    equity_curve = np.array(equity_curve)
    peak = np.maximum.accumulate(equity_curve)
    drawdown = peak - equity_curve

    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(equity_curve, color='blue', label='Equity Curve')
    ax1.set_xlabel('Trade Number')
    ax1.set_ylabel('Equity', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    ax2 = ax1.twinx()
    ax2.plot(drawdown, color='red', label='Drawdown')
    ax2.set_ylabel('Drawdown', color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    fig.suptitle(f'{symbol} - Equity Curve and Drawdown')

    # Combine legends of both axes
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left')

    plt.tight_layout()
    plt.show()
