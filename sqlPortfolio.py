import sqlite3
from datetime import datetime as dt
from datetime import timedelta
import os

import pandas as pd
import requests

class PortfolioMaster():
    # Creates database with tables if not pre-existing;
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

        if table.size == 0:
            return 1
        
        # Format table's index & date time elements
        table.set_index('stock_ticker', inplace=True)
        table['time_updated'] = table['time_updated'].map(dt.fromisoformat)

        return table

if __name__ == '__main__':
    pm = PortfolioMaster('practice', 'Stock_API_key')
    pm.increment_minute_daily_calls()
    print(f"Minute Calls: {pm.check_minute_calls()} Daily Calls: {pm.check_daily_calls()}")
    table = pm.overview_table()
    if table == 1:
        print("Empty Portfolio")
    else:
        print(table)