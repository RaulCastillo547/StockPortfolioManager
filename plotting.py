from matplotlib import pyplot as plt
import pandas as pd

def graph():
    overview_df = pd.read_csv('Stock Market\Overview.csv', index_col='Stock')
    fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(10, 10))
    
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
    ax4 = fig.add_subplot(4, 1, (4, 5))
    bar_chart = ax4.bar(overview_df.index, overview_df['Current Profit/Loss'])
    
    ax4.set_title('Money Made Across Stocks')
    ax4.axes.get_yaxis().set_visible(False)
    ax4.bar_label(bar_chart, fmt = '$%0.2f')
    plt.show()

graph()