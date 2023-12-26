from PortfolioMaster import PortfolioMaster

from datetime import date
import os

print("Welcome to Portfolio Manager (v.1.1.0)! (Now with SQL!)")
print("For more information, please see the ReadMe file on GitHub.\n")

# Open / Create a portfolio
select_state = input("Type \'L\' to load an exiting portfolio or \'N\' to create a new portfolio: ").upper()
while (select_state != 'L' and select_state != 'N'):
    select_state = input("Type \'L\' or \'N\': ").upper()

if 'Databases' not in os.listdir():
    os.makedirs('Databases')

options = list(map(lambda x: x[:-3], list(filter(lambda x: x.endswith('.db'), os.listdir('Databases')))))

portfolio_name = str()
if len(options) == 0 and select_state == 'L':
    print("There are no pre-existing portfolios. Create a new portfolio.")
    select_state = 'N'

if select_state == 'L':
    # File Options
    while portfolio_name not in options:
        print(f"Select from the following: {', '.join(options)}")
        portfolio_name = input()

elif select_state == 'N':
    portfolio_name = input("Enter a porfolio name: ")
    while portfolio_name in options:
        portfolio_name = input("Name has been taken; enter another name: ")

portfolio_name = 'Databases\\' + portfolio_name

print()
print("Access Granted!\n")

# Access Main Menu
# Options: Add Funds, Call/Sell, Update, Read, Graph, & Quit
portfolio = PortfolioMaster(portfolio_name, 'Stock_API_Key')

print("Welcome to the Main Menu!")
print("Select from the following options:\n- Add/Remove Cash (\'A\')\n- Make a Call/Sell (\'P\')\n- Update Portfolio (\'U\')\n- Display Portfolio (\'D\')\n- Info on API Limits (\'I\')\n- Quit (\'Q\')\n")

while (select_state != 'Q'):
    select_state = input("Enter a choice: ")
    select_state = select_state.upper()

    if (select_state == 'A'):
        # Adds/Subtract cash
        print(f"Current Funds: {portfolio.check_cash()}")
        funds = float(input("Enter Amount to Add (or Subtract): "))
        if (portfolio.add_remove_cash(funds) == 1):
            print("Cannot have funds less than 0")

    elif (select_state == 'P'):
        # Buy/Sell shares
        try:
            stock_name = input('Enter ticker symbol: ')
            quantity = float(input('Enter amount to buy or sell: '))
            if (portfolio.make_order(stock_name, quantity) == 1):
                continue
        except:
            print("Improper Values")
        else:
            portfolio.update()

    elif (select_state == 'U'):
        # Updates overview table
        portfolio.update()

    elif (select_state == 'D'):
        # Display information about a portfolio's makeup with a table and graph
        portfolio.update()
        table = portfolio.overview_table()
        if table.size != 0:
            print(table)
            input('Press enter to generate graph')
            portfolio.graph_portfolio()
        else:
            print("Portfolio has no stock investments")

    elif (select_state == 'I'):
        # Shows info on API Limits
        print(f"Today's Date: {date.today()}")
        print(f"- Minute Calls: {portfolio.check_minute_calls()} / 5")
        print(f"- Calls Today: {portfolio.check_daily_calls()}")

    elif (select_state == 'Q'):
        print("Thank you for using our Portfolio Manager!")
        print("Have a great day!")

    else:
        print("Invalid option")

    print()