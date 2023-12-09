from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd

from PortfolioMaster import PortfolioMaster

def graph(portfolio):
    overview_df = portfolio.overview_table()
    plt.style.use('seaborn-v0_8')
    fig = plt.figure(tight_layout=True)
    gs = gridspec.GridSpec(2,3)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[0, 2])
    ax4 = fig.add_subplot(gs[1, :])

    # 1 Quantity
    def quantity_format(pct, allvals):
        value = allvals*(pct/100)
        output = '{:n}'.format(value)
        return output
    ax1.pie(x=overview_df['Quantity'], labels=overview_df.index, autopct=lambda pct: quantity_format(pct, overview_df['Quantity'].sum()))
    ax1.set_title('Quantity of Stocks Owned')

    # 2 Invested
    def currency_format(pct, allvals):
        value = allvals*(pct/100)
        output = '${:0.2f}'.format(value)
        return output
    ax2.pie(x=overview_df['Amount Invested'], labels=overview_df.index, autopct=lambda pct: currency_format(pct, overview_df['Amount Invested'].sum()))
    ax2.set_title('Amount Invested Across Stocks')

    # 3 Current Worth
    ax3.pie(x=overview_df['Current Worth'], labels=overview_df.index, autopct=lambda pct: currency_format(pct, overview_df['Current Worth'].sum()))
    ax3.set_title('Current Value of Stocks')

    # 4 Revenue Accross Stocks
    
    colors = ['g' if value > 0 else 'r' for value in overview_df['Current Profit/Loss']]
    bar_chart = ax4.bar(overview_df.index, overview_df['Current Profit/Loss'], color = colors)
    
    ax4.set_title('Money Made Across Stocks')
    ax4.axes.get_yaxis().set_visible(False)
    ax4.bar_label(bar_chart, fmt = '$%0.2f')

    plt.show()