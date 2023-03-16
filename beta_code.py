from PortfolioMaster import PortfolioMaster as pm
import os

print('Welcome to the Portfolio Master!\n' + 'For more information, please see the attached ReadMe file.')

select_state = input('Type \'LOAD\' to load an existing portfolio or \'NEW\' to create a new portfolio.')

while (select_state != 'LOAD') and (select_state != 'NEW'):
    print()
    select_state = input('Please type \'LOAD\' or \'NEW\'')    

portfolio_link = input('\nType the Porfolio\'s URL link or name')

while True:
    if (select_state == 'LOAD') and (os.DirEntry.is_dir(portfolio_link)):
        portfolio = pm(portfolio_link)
        escape = False
        break

    if (select_state == 'LOAD' and not(os.DirEntry.is_dir(portfolio_link))):
        portfolio_link = input('Retype Porfolio URL')

    if select_state == 'NEW':
        portfolio = pm(portfolio_link)
        escape = False
        break

print('Please select from the following options:')
select_state = input('''-FUNDS\n-CALL\n-UPDATE\n-TABLE\n-EXIT\n''')

while True:
    if (select_state == 'FUNDS'):
        cash_change = float(input('Type a postive number for a deposit or a negative number for a withdrawal'))
        portfolio.add_remove_cash(cash_change)
        select_state = input('Pick another option')
    
    if (select_state == 'CALL'):
        stock_name = input('Enter the stock\'s ticker symbol')
        quantity = input('Enter the quantity you wish to purchase')
        portfolio.call_order(stock_name,)
        select_state = input('Pick another option')
    
    if (select_state == 'UPDATE'):
        portfolio.load_orders()
        portfolio.update()
        select_state = input('Pick another option')
    
    if (select_state == 'TABLE'):
        portfolio.table()
        select_state = input('Pick another option')
    
    if (select_state == 'EXIT'):
        break
    
    if select_state not in ['FUNDS', 'CALL', 'UPDATE', 'TABLE', 'EXIT']:
        select_state = input('Try Again')


print('\nThank you for using the program!')