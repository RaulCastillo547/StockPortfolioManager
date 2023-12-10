from datetime import datetime
from datetime import time
from datetime import timedelta
import os
import requests
import math

import pandas as pd

def pause(seconds):
    tmp = datetime.now()
    while (datetime.now() - tmp).total_seconds() <= seconds:
        pass

class PortfolioMaster():
    # Sets up variables for the class and creates 
    # the files storing stock data if they are not present
    def __init__(self, folder_name, API_KEY):
        self.folder_name = folder_name
        self.hold_url = self.folder_name + '/Transactions on Hold.csv'
        self.post_url = self.folder_name + '/Posted Transactions.csv'
        self.overview_url = self.folder_name + '/Overview.csv'
        self.meta_url = self.folder_name + '/Meta.csv'

        self.api_key = os.environ.get(API_KEY)

        if self.folder_name not in os.listdir():
            os.makedirs(self.folder_name)

        if 'Overview.csv' not in os.listdir(self.folder_name):
            overview_df = pd.DataFrame({'Stock': [], 'Quantity': [], 
                                        'Amount Invested': [], 
                                        'Invested per Share': [], 
                                        'Current Worth': [], 'Price per Share': [], 
                                        'Current Profit/Loss': [], 'Last Updated': []})
            overview_df.to_csv(self.overview_url, index=False, mode='w+')

        if 'Transactions on Hold.csv' not in os.listdir(self.folder_name):
            hold_df = pd.DataFrame({'Date': [], 'Stock': [], 'Quantity Moved': []})
            hold_df.to_csv(self.hold_url, index=False, mode='w+')
        
        if 'Posted Transactions.csv' not in os.listdir(self.folder_name):
            post_df = pd.DataFrame({'Time Posted': [], 'Stock': [],
                                    'Quantity Moved': [], 'Price Per Share': [],
                                    'Amount Moved': [], 'Last Updated': []})
            post_df.to_csv(self.post_url, index=False, mode='w+')

        if 'Meta.csv' not in os.listdir(self.folder_name):
            meta_df = pd.DataFrame({'Item': ['Cash'], 
                                    'Quantity': [0.00]})
            meta_df.to_csv(self.meta_url, index=False, mode='w+')

    def call_order(self, symbol, quantity):
        # Begins a transaction that is placed in the Hold Transactions csv
        # before load_orders() is called

        hold_df = pd.read_csv(self.hold_url)
        post_df = pd.read_csv(self.post_url)

        try:
            hold_counts = hold_df.groupby('Stock').get_group(symbol)['Quantity Moved'].astype(int).sum()
        except:
            hold_counts = 0

        try:
            post_counts = post_df.groupby('Stock').get_group(symbol)['Quantity Moved'].astype(int).sum()
        except:
            post_counts = 0
        if (hold_counts+post_counts+quantity < 0 or quantity==0):
            return 1

        add_on_df = pd.DataFrame({'Date': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')], 
                                    'Stock': [symbol],'Quantity Moved':[quantity]}).set_index('Stock')
        
        hold_df.set_index('Stock', inplace=True)

        if (symbol in hold_df.index):
            add_on_df.loc[symbol, 'Quantity Moved'] += hold_counts
            
            if (add_on_df.loc[symbol, 'Quantity Moved'] == 0):
                hold_df.drop(symbol, inplace=True)
            else:
                hold_df.update(add_on_df, inplace=True)
        else:
            hold_df.loc[symbol] = add_on_df.loc[symbol]
        
        hold_df.reset_index(inplace=True)

        hold_df.to_csv(self.hold_url, index=False,  mode='w')

        return 0

    def load_orders(self):
        # Brings the transactions listed on the Hold Transactions csv
        # onto the posted transactions csv

        current = datetime.now() - timedelta(days=1)
        hold_df = pd.read_csv(self.hold_url)

        hold_extract = {'Time Posted': [], 'Stock': [], 
                        'Quantity Moved': [], 'Price Per Share': [], 
                        'Amount Moved': [], 'Last Updated': []}
        index_removeable = []

        for index in hold_df.index:
            if (self.count_total_daily_calls()) > 25:
                print('Exceeded API Cap of 25 Calls per Day')
                break
            if (index + 1 + self.count_minute_calls()) % 5 == 0:
                print('Program Paused')
                pause(65)
                print('Program Continued')

            # Extract data from Hold Transactions csv
            stock = hold_df['Stock'][index]
            quantity = float(hold_df['Quantity Moved'][index])
            last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Extract data from JSON with current stock information
            url_link = (r"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval=15min&apikey={}".format(stock, self.api_key))
            url_data = requests.get(url_link)
            json_data = url_data.json()

            # Parsing through date data from JSON and associated price per share data
            try:
                dates = pd.DataFrame(json_data['Time Series (15min)']).transpose().reset_index()
                dates = pd.to_datetime(dates['index']).dt.date
            except:
                print(json_data)
                break

            if current.date() not in dates:
                stock_time = (datetime.strptime(json_data['Meta Data']['3. Last Refreshed'], '%Y-%m-%d %H:%M:%S').replace(hour=16, minute=0, second=0, microsecond=0)).strftime('%Y-%m-%d %H:%M:%S')
                price_per_share = float(json_data['Time Series (15min)'][stock_time]['4. close'])

            elif (time(hour = 9, minute=30) <= current.time()) and (current.time() <= time(hour=16)):
                stock_time = json_data['Meta Data']['3. Last Refreshed']
                price_per_share = float(json_data['Time Series (15min)'][stock_time]['4. close'])
                
            elif (time.min <= current.time()) and (current.time() < time(hour=9, minute=30)): 
                stock_time = (current.replace(hour=16, minute=0, second=0, microsecond=0) - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                price_per_share = float(json_data['Time Series (15min)'][stock_time]['4. close'])
                
            elif (time(hour=16) <= current.time()) and (current.time() < time.max):
                stock_time = current.replace(hour=16, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
                price_per_share = float(json_data['Time Series (15min)'][stock_time]['4. close'])

            # Calculate change in cash balance
            meta_df = pd.read_csv(self.meta_url, index_col='Item')
            if (meta_df['Quantity']['Cash'] - math.ceil(price_per_share*quantity*100)/100) >= 0:
                self.add_remove_cash(-1*math.ceil(price_per_share*quantity*100)/100)
            else:
                print('Not Enough Money to Invest')
                break

            # Summarize Data
            hold_extract['Time Posted'] += [stock_time]
            hold_extract['Stock'] += [stock]
            hold_extract['Quantity Moved'] += [quantity]
            hold_extract['Price Per Share'] += [price_per_share]
            hold_extract['Amount Moved'] += [math.ceil(price_per_share*quantity*100)/100]
            hold_extract['Last Updated'] += [last_updated]

            # Add Index
            index_removeable += [index]

        # Add to Posted Transactions
        post_df = pd.read_csv(self.post_url)
        addon_df = pd.DataFrame(hold_extract)
        if post_df.size > 0:
            post_df = pd.concat([post_df, addon_df], axis=0, ignore_index=True)
        else:
            post_df = addon_df
        post_df.to_csv(self.post_url, index=False, mode='w')
        
        # Remove Transactions That Were Posted
        hold_df.drop(index_removeable, inplace=True)
        hold_df.to_csv(self.hold_url, index=False, mode='w')

    def update(self):
        # Summarizes the data on the Posted Transactions csv 
        # onto the Overview csv
        post_df = pd.read_csv(self.post_url)
        post_dfgb = post_df.groupby('Stock')

        output = {'Stock': [], 'Quantity': [], 
                    'Amount Invested': [], 'Invested per Share': [], 
                    'Current Worth': [], 'Price per Share': [], 
                    'Current Profit/Loss': [], 'Last Updated': []}

        for index, group in enumerate(post_dfgb.groups):
            if (self.count_total_daily_calls()) >= 25:
                print('Exceeded API Cap of 25 Calls per Day')
                break

            if (index + 1 + self.count_minute_calls()) % 5 == 0:
                print('Program Paused')
                pause(65)
                print('Program Continued')

            df_stock = post_dfgb.get_group(group)

            # Extract from Post Transactions CSV
            stock = group
            quantity = df_stock['Quantity Moved'].astype(float).sum()
            if quantity <= 0:
                continue
            amount_invested = df_stock['Amount Moved'].astype(float).sum()
            invested_per_share = (df_stock['Amount Moved'].astype(float).sum() 
                                    / df_stock['Quantity Moved'].astype(float).sum())

            # Extract data from JSON with current stock information
            url_link = (r"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval=15min&apikey={}".format(group, self.api_key))
            url_data = requests.get(url_link)
            json_data = url_data.json()
            
            current = datetime.now() - timedelta(days=1)

            try:
                dates = pd.DataFrame(json_data['Time Series (15min)']).transpose().reset_index()
                dates = pd.to_datetime(dates['index']).dt.date
            except:
                print(json_data)
                break

            # Parsing through date data from JSON and associated price per share data
            if current.date() not in dates:
                stock_time = (datetime.strptime(json_data['Meta Data']['3. Last Refreshed'], '%Y-%m-%d %H:%M:%S').replace(hour=16, minute=0, second=0, microsecond=0)).strftime('%Y-%m-%d %H:%M:%S')
                price_per_share = float(json_data['Time Series (15min)'][stock_time]['4. close'])
            elif (time(hour = 9, minute=30) <= current.time()) and (current.time() <= time(hour=16)):
                stock_time = json_data['Meta Data']['3. Last Refreshed']
                price_per_share = float(json_data['Time Series (15min)'][stock_time]['4. close'])
            elif (time.min <= current.time()) and (current.time() < time(hour=9, minute=30)): 
                stock_time = (current.replace(hour=16, minute=0, second=0, microsecond=0) - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                price_per_share = float(json_data['Time Series (15min)'][stock_time]['4. close'])
            elif (time(hour=16) <= current.time()) and (current.time() < time.max):
                stock_time = current.replace(hour=16, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
                price_per_share = float(json_data['Time Series (15min)'][stock_time]['4. close'])
            
            current_worth = (price_per_share)*df_stock['Quantity Moved'].astype(float).sum()
            profit_loss = (price_per_share)*df_stock['Quantity Moved'].astype(float).sum() - df_stock['Amount Moved'].astype(float).sum()
            profit_loss = float(('{:.2f}').format(profit_loss))

            # Read overview csv
            tmp_overview_df = pd.read_csv(self.overview_url)

            if tmp_overview_df.size > 0: 
                tmp_overview_df[['Post_#', 'Posting Dates']] = tmp_overview_df['Last Updated'].apply(lambda x: pd.Series(str(x).split('_')))
                tmp_overview_df['Posting Dates'] = tmp_overview_df['Posting Dates'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date())
            tmp_overview_df.set_index('Stock', inplace=True)

            try:
                if tmp_overview_df.loc[stock, 'Posting Dates'] == datetime.now().date():
                    count = int(tmp_overview_df.loc[stock, 'Post_#']) + 1
                else:
                    count = 1
            except:
                count = 1

            # Summarize Data
            output['Stock'] += [stock]
            output['Quantity'] += [int(quantity)]
            output['Amount Invested'] += [amount_invested]
            output['Invested per Share'] += [invested_per_share]
            output['Price per Share'] += [price_per_share]
            output['Current Worth'] += [current_worth]
            output['Current Profit/Loss'] += [round(profit_loss,2)]
            output['Last Updated'] += [str(count) + '_' + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))]
        
        # Apply extracted data onto Overview csv
        overview_df = pd.read_csv(self.overview_url)
        
        if overview_df.size > 0:
            overview_df.set_index('Stock', inplace=True)
            add_on = pd.DataFrame(output).set_index('Stock')
            overview_df.update(add_on)
            
            for stock in post_dfgb.groups:
                if stock not in overview_df.index and stock in output['Stock']:
                    overview_df.loc[stock] = add_on.loc[stock]
                
                quantity = post_df.groupby('Stock').get_group(stock)['Quantity Moved'].astype(float).sum()
                
                if stock in overview_df.index and quantity <= 0:
                    overview_df.drop(stock, inplace=True)

            overview_df.reset_index(col_level=0, inplace=True)
        else:
            overview_df = pd.DataFrame(output)

        overview_df.to_csv(self.overview_url, index=False, mode='w')
        return 0

    def overview_table(self):
        overview_df = pd.read_csv(self.overview_url, index_col='Stock')
        overview_df['Last Updated'] = overview_df['Last Updated'].apply(lambda x: str(x).removeprefix(str(x)[:str(x).find('_')+1]))
        return overview_df

    def money_count(self):
        meta_df = pd.read_csv(self.meta_url, index_col="Item")
        count = round(pd.to_numeric(meta_df.loc['Cash', 'Quantity']),2)
        return count

    def count_total_daily_calls(self):
        current_date = datetime.now().date()
        count = 0

        overview_df = pd.read_csv(self.overview_url)
        if overview_df.size > 0: 
            overview_df[['Post_#', 'Posting Dates']] = overview_df['Last Updated'].apply(lambda x: pd.Series(str(x).split('_')))

            for index in overview_df.index:
                if current_date.strftime('%Y-%m-%d') == datetime.strptime(overview_df.loc[index, 'Posting Dates'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d'):
                    count += pd.to_numeric(overview_df.loc[index, 'Post_#'])
        post_df = pd.read_csv(self.post_url)
        post_df = pd.to_datetime(post_df['Last Updated']).dt.date

        for i in post_df:
            if i == current_date:
                count += 1

        return count

    def count_minute_calls(self):
        count = 0

        # Go through Overview csv
        overview_df = pd.read_csv(self.overview_url)
        if overview_df.size > 0:
            overview_df[['Post_#', 'Dates']] = overview_df['Last Updated'].apply(lambda x: pd.Series(str(x).split('_')))
            overview_df['Dates'] = overview_df['Dates'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S').replace(second=0, microsecond=0))

            for date in overview_df['Dates']:
                if date == datetime.now().replace(second=0, microsecond=0):
                    count += 1
        
        # Go through Posted Transactions csv
        post_df = pd.read_csv(self.post_url)
        if post_df.size > 0:
            post_df['Last Updated'] = post_df['Last Updated'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S').replace(second=0, microsecond=0))
            for date in post_df['Last Updated']:
                if date == datetime.now().replace(second=0, microsecond=0):
                    count += 1

        return count

    def add_remove_cash(self, change):
        meta_df = pd.read_csv(self.meta_url, index_col='Item')

        cash = meta_df['Quantity']['Cash'] + change
        meta_df.loc['Cash', 'Quantity'] = cash
        meta_df.reset_index(col_level=0, inplace=True)

        meta_df.to_csv(self.meta_url, index=False, mode='w')
