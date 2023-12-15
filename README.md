# Stock Portfolio Manager
### Introduction
Welcome to my Stock Portfolio Manager's Github page! This program allows users to run their own stock portfolios via the command prompt.

On the repository's main page, you will find 5 items:
1) `TestPortfolio`: A file that makes up a premade portfolio
2) `ConsoleScript.py`: Contains code for the Stock Portfolio Manager menu
3) `Plotting.py`: Contains code for graphing the portfolio's information
4) `PortfolioMaster.py`: Defines the `PortfolioMaster` class, which allows the program to setup and manage portfolios
5) `requirements.txt`: Defines the python packages used when making the program

(**Note:** Although this program tracks financial data and involves adding/removing "cash", no money is actually managed by the program.)

### Setup

1) Get key from Alpha Vantage API: This project uses Alpha Vantage's free stock market api to get access to data; this does cause some limitations, such as limits of 5 calls per minute and 25 calls a day, but the program accounts for these limits by pausing and unpausing when needed.
   - Go to Alpha Vantage's [website](https://www.alphavantage.co/) and select "Get Free API Key"
     
   - Fill out the form provided with your current position, organization, and email to retrieve your API key; save the key once you retrieve it
     
   - If your using Windows, go to settings, search and select "Edit environmental variables for your account", and add a new environmental variable with the name `Stock_API_key` and a value of the provided key
 
   - If your using another , please check how to access and edit your environmental variables to add in a variable with the key; this process allows your computer to use your own Alpha Vantage API key when running the manager

2) Download files into a folder and download the modules in `requirements.txt` through pip; ideally, you should run a venv beforehand as to keep your system python imports unaffected

4) Run `PortfolioMaster.py` with the command prompt (I use `py PortfolioMaster.py`, but that may differ with your system) to use the portfolio manager

### Future Updates
- Plan to use SQL Management Database
