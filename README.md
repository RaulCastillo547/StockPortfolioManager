# Stock Portfolio Manager
### Introduction
Welcome to my Stock Portfolio Manager's Github page! This program allows users to run their own stock portfolios via the command prompt.

On the repository's main page, you will find 5 items:
1) `Databases`: Folder storing sql databases holding portfolio information; one database in the folder, `practice.db` has an example portfolio
2) `ConsoleScript.py`: Contains code for the Stock Portfolio Manager menu
3) `PortfolioMaster.py`: Defines the `PortfolioMaster` class, which allows the program to setup, edit, and view their portfolios
4) `requirements.txt`: Defines the python packages used when making the program

(**Note:** Although this program tracks financial data and involves adding/removing "cash", no money is actually managed by the program.)

### Setup
1) Get key from Polygon.io API: A previous version used Alpha Vantage's free stock market api for data, but the api has been switch to Polygon.io's api; Polygon.io's free API as limits of 5 calls per limit, but the program limits this by pausing and unpausing when needed and using the least amount of calls as possible.
   - Go to Polygon.io's [website](https://polygon.io/) and sign up for an account if you do not already have one

   - In your account's dashboard, scroll down to find your API Keys and copy/make note of your default API key.

   - If your using Windows, go to your computer settings, search and select "Edit environmental variables for your account", and add a new environmental variable with the name `Stock_API_key` and a value of the provided key
 
   - If your using another , please check how to access and edit your environmental variables to add in a variable with the key; this process allows your computer to use your own Alpha Vantage API key when running the manager

2) Download files into a folder and download the modules in `requirements.txt` through pip; ideally, you should run a venv beforehand as to keep your system python imports unaffected

4) Run `ConsoleScript.py` with the command prompt (I use `py ConsoleScript.py`, but that may differ with your system) to use the portfolio manager

### Features:
- Porfolio Tables:
   - Meta: Contains information about the portfolio's cash balance and daily/minute call amounts
      - time (TEXT): Tracks the current minute and day in an ISO format date time string
      - cash (REAL): Tracks the amount of cash in the portfolio
      - minute_calls (INTEGER): Tracks the amount of minute calls made in a certain minute
      - daily_calls (INTEGER): Tracks the amount of daily calls made in a certain day
   - Orders: Contains listings for orders to be done
      - time (TEXT): Tracks the time an order was made
      - stock_ticker (TEXT): Names the stock being ordered
      - quantity (INTEGER): Lists the amount of shares being bought (if positive) or sold (if negative)
   - Receipts: Contains listings for completed orders
      - time_posted (TEXT): Tracks the time an order was completed
      - stock_ticker (TEXT): Stores the name of the stock that was ordered
      - quantity (TEXT): Stores the amount of stock being bought (if positive) or sold (if negative)
      - price_per_share (REAL): Stores the price of a stock's share at time of purchase
      - total_amount (REAL): Stores the amount of money given (if positive) or received (if negative) from a purchase
   - Overview: Summarizes Receipts table, showing what investments the portfolio currently has
      - stock_ticker (TEXT): Stores the name of the stock
      - quantity (INTEGER): Stores the amount of shares for a stock in the portfolio
      - amount_invested (REAL): Tracks the amount of money invested in the stock
      - current_price (REAL): Tracks the stocks current price
      - current_value (REAL): The current value of an investment if it were to be liquidated into cash
      - profit (REAL): The amount of money one has made (if positive) or loss (if negative) from an investment
      - time_updated (TEXT): Tracks the time that the stock's current price has been updated

- PortfolioManager(database_name, API_KEY): Defines class representing a portfolio using the name `database_name` and the api key `API_KEY`
   - make_order(stock_ticker, quantity): Calls an order of shares; outputs a 0 if order is possible and a 1 if an order is not possible
      - `stock_ticker`: Name of shares
      - `quantity`: Number of shares to order
   - update(): Keeps portfolio up-to-date, perfroming uncalled orders and updating the Orders table with the portfolio's current makeup
   - graph_portfolio(): Outputs a matplotlib figure summarizing the portfolio's makeup and performance; returns 1 if Overview table is empty (making graphing unnecessary) and 0 if Overview table is not empty
   - add_remove_cash(amount): Changes the amount of cash in the portfolio; returns 0 if change is valid and 1 if change leads to a negative balance
      - `amount`: Amount of cash to add (if positive) or remove (if negative)
   - increment_minute_daily_calls(): Used to increase the minute and daily call counts on the Meta table by one
   - check_cash(): Returns the amount of cash in the portfolio
   - check_minute_calls(): Returns the amount of minute calls performed in the current minute
   - check_daily_calls(): Returns the amount of daily calls performed in the current day
   - overview_table(): Returns the overview table as a Pandas dataframe
