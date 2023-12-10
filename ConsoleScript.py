from PortfolioMaster import PortfolioMaster as pm
from Plotting import graph

from datetime import date

import os

print("Welcome to Portfolio Manager (v.1.0.0)!")
print("For more information, please see the ReadMe file on GitHub.\n")

# Open / Create a portfolio
select_state = input("Type \'L\' to load an exiting portfolio or \'N\' to create a new portfolio: ").upper()
while (select_state != 'L' and select_state != 'N'):
    select_state = input("Type \'L\' or \'N\': ").upper()

options = []
for entry in os.listdir():
    if os.path.isdir(entry) and entry not in ['.git', '.venv', '__pycache__', '.vscode']:
        options.append(entry)

portfolio_name = str()
if len(options) == 0 and select_state == 'L':
    print("There is no other portfolio. Create a new portfolio.")
    select_state = 'N'

select_state = select_state.upper()
if select_state == 'L':
    # File Options
    while portfolio_name not in options:
        print(f"Select from the following: {', '.join(options)}")
        portfolio_name = input()
elif select_state == 'N':
    portfolio_name = input("Enter a porfolio name: ")
    while portfolio_name in options:
        portfolio_name = input("Name has been taken; enter another name: ")

print()
print("Access Granted!\n")

# Access Main Menu
# Options: Add Funds, Call/Sell, Update, Read, Graph, & Quit
portfolio = pm(portfolio_name, 'Stock_API_key')

print("Welcome to the Main Menu!")
print("Select from the following options:\n- Add/Remove Cash (\'A\')\n- Make a Call/Sell (\'P\')\n- Update Portfolio (\'U\')\n- Display Portfolio (\'D\')\n- Info on API Limits (\'I\')\n- Quit (\'Q\')\n")

while (select_state != 'Q'):
    select_state = input("Enter a choice: ")
    select_state = select_state.upper()

    if (select_state == 'A'):
        # Adds/Subtract cash
        print(f"Current Funds: {portfolio.money_count()}")
        funds = float(input("Enter Amount to Add (or Subtract): "))
        portfolio.add_remove_cash(funds)

    elif (select_state == 'P'):
        # Buy/Sell shares
        try:
            stock_name = input('Enter ticker symbol: ')
            quantity = float(input('Enter amount to buy or sell: '))
            if (portfolio.call_order(stock_name, quantity) == 1):
                raise ValueError
        except:
            print("Improper Values")
        else:
            portfolio.load_orders()
            portfolio.update()

    elif (select_state == 'U'):
        # Updates overview table 
        portfolio.load_orders()
        portfolio.update()

    elif (select_state == 'D'):
        # Display information about a portfolio's makeup with a table and graph
        table = portfolio.overview_table()
        print(table)
        input('Press enter to generate graph')
        graph(portfolio)

    elif (select_state == 'I'):
        # Shows info on API Limits
        print(f"Today's Date: {date.today()}")
        print(f"- Minute Calls: {portfolio.count_minute_calls()} / 5")
        print(f"- Calls Today: {portfolio.count_total_daily_calls()} / 25")

    elif (select_state == 'Q'):
        print("Thank you for using our Portfolio Manager!")
        print("Have a great day!")

    else:
        print("Invalid option")

    print()