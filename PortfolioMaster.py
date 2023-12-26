from datetime import datetime as dt
from datetime import timedelta
import math
import os
import sqlite3

from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import requests

class PortfolioMaster():
    # Creates database with tables if the database or tables do not already exist;
    # Also collects API key from environmental variable
    def __init__(self, database_name, API_KEY):
        # Collect API key & database name
        self.api_key = os.environ.get(API_KEY)
        self.database_name = database_name

        # Create cursor
        con = sqlite3.connect(self.database_name + ".db")
        cur = con.cursor()

        # Add missing tables: Meta, Orders, Receipts, Overview
        tables = cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        
        if ('Meta',) not in tables:
            cur.execute("""CREATE TABLE Meta (
                        time TEXT,
                        cash REAL,
                        minute_calls INTEGER,
                        daily_calls INTEGER
            )""")
            fill = {'time': dt.now().isoformat(), 'cash': 0.0, 'minute_calls': 0, 'daily_calls': 0}
            cur.execute("INSERT INTO Meta VALUES (:time, :cash, :minute_calls, :daily_calls)", fill)
        
        if ('Orders',) not in tables:
            cur.execute("""CREATE TABLE Orders (
                        time TEXT,
                        stock_ticker TEXT,
                        quantity INTEGER
            )""")

        if ('Receipts',) not in tables:
            cur.execute("""CREATE TABLE Receipts (
                        time_posted TEXT,
                        stock_ticker TEXT,
                        quantity INTEGER,
                        price_per_share REAL,
                        total_amount REAL
            )""")
        
        if ('Overview',) not in tables:
            cur.execute("""CREATE TABLE Overview (
                        stock_ticker TEXT,
                        quantity INTEGER,
                        amount_invested REAL,
                        current_price REAL,
                        current_value REAL,
                        profit REAL,
                        time_updated TEXT
            )""")
        
        # Close cursor
        con.commit()
        con.close()

    # Makes Calls
    def make_order(self, stock_ticker, quantity):
        # Create cursor
        con = sqlite3.connect(self.database_name + ".db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        # Gather amount of shares being moved in the orders and receipts tables
        orders_quantities = dict(cur.execute("SELECT stock_ticker, SUM(quantity) AS total_shares FROM Orders GROUP BY stock_ticker").fetchall())
        receipts_quantities = dict(cur.execute("SELECT stock_ticker, SUM(quantity) AS total_shares FROM Receipts GROUP BY stock_ticker").fetchall())

        if (orders_quantities.setdefault(stock_ticker, 0) + receipts_quantities.setdefault(stock_ticker, 0) + quantity) >= 0:
            # Proceed with order
            fill = {'time': dt.now().isoformat(), 'stock': stock_ticker, 'quantity': quantity}
            cur.execute("INSERT INTO Orders VALUES (:time, :stock, :quantity)", fill)
            
            # Close cursor
            con.commit()
            con.close()

            return 0
        else:
            # Do not proceed with order & close cursor
            con.commit()
            con.close()

            return 1
        
    def update(self):
        def pause(seconds):
            start = dt.now()
            while ((dt.now() - start) <= timedelta(seconds=seconds)):
                pass
        
        def retrieve_price(time, stock_ticker):
            check_time = time
            while True:
                # Check minute & daily calls: 5 calls per minute; I do not know of any daily cap, but keep just in case
                '''
                if (self.check_daily_calls() >= 1000):
                    print("Daily call limit reach; cannot be continued")
                    return "Error"
                '''

                if (self.check_minute_calls() >= 5):
                    print("Minute call limit reach; please wait 65 seconds")
                    pause(65)

                # If check_time is a weekend, subtract the datetime back to the most recent Friday
                if (5 <= check_time.weekday()):
                    check_time -= timedelta(days=(check_time.weekday() - 4))
                
                # Retrieve Data
                url_data = requests.get(f"https://api.polygon.io/v1/open-close/{stock_ticker}/{check_time.date().isoformat()}?adjusted=true&apiKey={self.api_key}")
                data = url_data.json()
                self.increment_minute_daily_calls()

                if (data['status'] == 'OK'):
                    return check_time, data['close']
                elif ((time - check_time) >= timedelta(days=5)):
                    return "Error", "Error"
                
                # If check_time does not have an associated share_price, it could be because of a holiday, so increment it back with the assumption that
                # Wallstreet does not have holidays that last longer than 5 days
                check_time -= timedelta(days=1)
            
        # Create cursor
        con = sqlite3.connect(self.database_name + '.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        # Post orders onto Receipts table
        orders_table = pd.read_sql("""
                    SELECT stock_ticker, SUM(quantity) AS shares_moved, MIN(time) AS oldest_transaction
                    FROM Orders
                    GROUP BY stock_ticker
                    ORDER BY datetime(oldest_transaction) ASC
                    """, con)
        orders_table.set_index('stock_ticker', inplace=True)
        orders_table['oldest_transaction'] = orders_table['oldest_transaction'].map(dt.fromisoformat)

        stocks_received = {}
        for ticker in orders_table.index:
            # Gather information for time_posted, stock_ticker, quantity, price_per_share, & total_amount
            time_posted = dt.now() - timedelta(days=1)
            quantity = int(orders_table.loc[ticker, 'shares_moved'])
            
            if (quantity == 0):
                cur.execute("DELETE FROM Orders WHERE stock_ticker = :stock_ticker", {'stock_ticker': ticker})
                con.commit()
                continue

            time_posted, price_per_share = retrieve_price(time_posted, ticker)
            if (price_per_share == "Error"):
                print(f'Could not retrieve data for {ticker} with {quantity} share(s); check if {ticker} is a proper stock ticker.')
                continue
            
            # This stores relevant stock information to add into the overview table
            stocks_received[ticker] = price_per_share

            total_amount = math.ceil(price_per_share*quantity*100)/100
            if (self.add_remove_cash(-1*total_amount) == 1):
                print(f'Not enough cash to buy {ticker} shares; add more funds.')
                continue

            # Apply information to Receipts & delete the Orders
            fill = {'time_posted': time_posted.isoformat(), 'stock_ticker': ticker, 'quantity': quantity, 'price_per_share': price_per_share, 'total_amount': total_amount}
            cur.execute("INSERT INTO Receipts VALUES (:time_posted, :stock_ticker, :quantity, :price_per_share, :total_amount)", fill)
            cur.execute("DELETE FROM Orders WHERE stock_ticker = :stock_ticker", {'stock_ticker': ticker})
            con.commit()

        # Summarize Receipts onto orders
        receipts_table = pd.read_sql("""
                                    SELECT stock_ticker, SUM(quantity) AS shares_moved, SUM(total_amount) as total_invested, MIN(time_posted) AS oldest_transaction
                                    FROM Receipts
                                    GROUP BY stock_ticker
                                    ORDER BY datetime(oldest_transaction)""", con)
        receipts_table.set_index('stock_ticker', inplace=True)
        receipts_table['oldest_transaction'] = receipts_table['oldest_transaction'].map(dt.fromisoformat)

        overview_table = pd.read_sql("SELECT * FROM Overview", con)
        overview_table.set_index('stock_ticker', inplace=True)
        
        for ticker in receipts_table.index:
            # Gather information for stock_ticker, quantity, amount_invested, current_price, current_value, profit, & time_updated         
            quantity = int(receipts_table.loc[ticker, 'shares_moved'])
            if (quantity == 0):
                if (ticker in overview_table.index):
                    cur.execute("DELETE FROM Overview WHERE stock_ticker = :stock_ticker", {'stock_ticker': ticker})
                    con.commit()
                continue
            
            amount_invested = float(receipts_table.loc[ticker, 'total_invested'])
            
            if (ticker in stocks_received):
                time_updated = receipts_table.loc[ticker, 'oldest_transaction']
                current_price = stocks_received[ticker]
            else:
                time_updated = dt.now() - timedelta(days=1)
                time_updated, current_price = retrieve_price(time_updated, ticker)
                if (current_price == 'Error'):
                    current_price = -1
                    print(f"Error emerged with current price per share retrieval; price has been set to -1")
                    continue
            
            current_value = math.ceil(current_price*quantity*100)/100
            profit = math.floor((current_value - amount_invested)*100)/100

            fill = {'stock_ticker': ticker, 'quantity': quantity, 'amount_invested': amount_invested, 'current_price': current_price, 'current_value': current_value, 'profit': profit, 'time_updated': time_updated.isoformat()}
            if (ticker in overview_table.index):
                cur.execute("UPDATE Overview SET quantity = :quantity, amount_invested = :amount_invested, current_price = :current_price, current_value = :current_value, profit = :profit, time_updated = :time_updated WHERE stock_ticker = :stock_ticker", fill)
                con.commit()
            else:
                cur.execute("INSERT INTO Overview VALUES (:stock_ticker, :quantity, :amount_invested, :current_price, :current_value, :profit, :time_updated)", fill)
                con.commit()

        # Close cursor
        con.commit()
        con.close()

    def graph_portfolio(self):
        overview_df = self.overview_table()
    
        if (overview_df.size == 0):
            return 1

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
        ax1.pie(x=overview_df['quantity'], labels=overview_df.index, autopct=lambda pct: quantity_format(pct, overview_df['quantity'].sum()))
        ax1.set_title('Quantity of Stocks Owned')

        # 2 Invested
        def currency_format(pct, allvals):
            value = allvals*(pct/100)
            output = '${:0.2f}'.format(value)
            return output
        ax2.pie(x=overview_df['amount_invested'], labels=overview_df.index, autopct=lambda pct: currency_format(pct, overview_df['amount_invested'].sum()))
        ax2.set_title('Amount Invested Across Stocks')

        # 3 Current Worth
        ax3.pie(x=overview_df['current_value'], labels=overview_df.index, autopct=lambda pct: currency_format(pct, overview_df['current_value'].sum()))
        ax3.set_title('Current Value of Stocks')

        # 4 Revenue Accross Stocks
        
        colors = ['g' if value > 0 else 'r' for value in overview_df['profit']]
        bar_chart = ax4.bar(overview_df.index, overview_df['profit'], color = colors)
        
        ax4.set_title('Money Made Across Stocks')
        ax4.axes.get_yaxis().set_visible(False)
        ax4.bar_label(bar_chart, fmt = '$%0.2f')

        plt.show()
        return 0

    def add_remove_cash(self, amount):
        # Create cursor
        con = sqlite3.connect(self.database_name + ".db")
        cur = con.cursor()

        # Add into change
        new_amount = round(self.check_cash() + math.ceil(amount*100)/100, 2)
        if new_amount < 0:
            con.close()
            return 1
        cur.execute("UPDATE Meta SET cash = :new_amount", {"new_amount": new_amount})

        # Close cursor
        con.commit()
        con.close()
        
        return 0

    def increment_minute_daily_calls(self):
        # Retrieve current minute and daily call amounts and add them by one
        amount_of_minute_calls = self.check_minute_calls() + 1
        amount_of_daily_calls = self.check_daily_calls() + 1

        # Create cursor
        con = sqlite3.connect(self.database_name + ".db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        fill = {'amount_of_minute_calls': amount_of_minute_calls, 'amount_of_daily_calls': amount_of_daily_calls}
        cur.execute("UPDATE Meta SET minute_calls = :amount_of_minute_calls, daily_calls = :amount_of_daily_calls", fill)

        # Close cursor
        con.commit()
        con.close()

    # Fetch amount of cash left in portfolio
    def check_cash(self):
        # Create cursor
        con = sqlite3.connect(self.database_name + ".db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        amount_of_cash = cur.execute("SELECT cash FROM Meta").fetchone()['cash']

        # Close cursor
        con.commit()
        con.close()

        return amount_of_cash
    
    # Fetch amount of minute calls
    def check_minute_calls(self):
        # Create cursor
        con = sqlite3.connect(self.database_name + ".db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        # Get current datetime, compare with listed time, and if day, hour, or minute has changed changed, revert minute_calls to 0
        current_dt = dt.now()
        meta_dt = dt.fromisoformat(cur.execute("SELECT time FROM Meta").fetchone()['time'])

        if ((current_dt - meta_dt) >= timedelta(days=1)):
            fill = {'current_time': current_dt.isoformat(), 'amount_of_minute_calls': 0, 'amount_of_daily_calls': 0}
            cur.execute("UPDATE Meta SET time = :current_time, minute_calls = :amount_of_minute_calls, daily_calls = :amount_of_daily_calls", fill)
            con.commit()
        elif ((current_dt - meta_dt) >= timedelta(minutes=1)):
            fill = {'current_time': current_dt.isoformat(), 'amount_of_minute_calls': 0}
            cur.execute("UPDATE Meta SET time = :current_time, minute_calls = :amount_of_minute_calls", fill)
            con.commit()

        amount_of_minute_calls = cur.execute("SELECT minute_calls FROM Meta").fetchone()['minute_calls']

        # Close cursor
        con.commit()
        con.close()
        
        return amount_of_minute_calls
    
    # Fetch amount of daily calls
    def check_daily_calls(self):
        # Create cursor
        con = sqlite3.connect(self.database_name + ".db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        # Get current datetime, compare with listed time, and if day, hour, or minute has changed changed, revert minute_calls to 0
        current_dt = dt.now()
        meta_dt = dt.fromisoformat(cur.execute("SELECT time FROM Meta").fetchone()['time'])

        if ((current_dt - meta_dt) >= timedelta(days=1)):
            fill = {'current_time': current_dt.isoformat(), 'amount_of_minute_calls': 0, 'amount_of_daily_calls': 0}
            cur.execute("UPDATE Meta SET time = :current_time, minute_calls = :amount_of_minute_calls, daily_calls = :amount_of_daily_calls", fill)
            con.commit()

        amount_of_daily_calls = cur.execute("SELECT daily_calls FROM Meta").fetchone()['daily_calls']

        # Close cursor
        con.commit()
        con.close()
        
        return amount_of_daily_calls
    
    # Fetch table
    def overview_table(self):
        # Create cursor
        con = sqlite3.connect(self.database_name + ".db")

        table = pd.read_sql("SELECT * FROM Overview ORDER BY stock_ticker ASC", con)
        
        # Close cursor
        con.commit()
        con.close()
        
        # Format table's index & date time elements
        table.set_index('stock_ticker', inplace=True)
        table['time_updated'] = table['time_updated'].map(dt.fromisoformat)

        return table

if __name__ == '__main__':
    # Test program
    pm = PortfolioMaster('practice', 'Stock_API_Key')

    print(f"Start Cash: {pm.check_cash()}")
    
    # pm.make_order('AAPL', 2)
    # pm.make_order('IBM', 2)
    # pm.make_order('BA', 3)

    pm.update()
    

    print(pm.overview_table())

    print(f"End Cash: {pm.check_cash()}")

    print(f"\nCurrent Time: {dt.now()}")
    print(f"Minute Calls: {pm.check_minute_calls()}")
    print(f"Daily Calls: {pm.check_daily_calls()}")