# Stock Portfolio Manager
### Introduction
Welcome to my Stock Portfolio Manager's Github page! This program allows users to run their own stock portfolios via the command prompt.

On the repository's main page, you will find 5 items:
1) `Databases`: Folder storing sql databases holding portfolio information; one database in the folder, `practice.db`, has an example portfolio
2) `ConsoleScript.py`: Contains code for the Stock Portfolio Manager menu
3) `PortfolioMaster.py`: Defines the `PortfolioMaster` class, which allows the program to setup, edit, and visualize portfolios
4) `requirements.txt`: Defines the python packages used when making the program

(**Note:** Although this program tracks financial data and involves adding/removing "cash", no money is actually managed by the program.)

### Setup
1) Get key from Polygon.io API: Polygon.io's free API has limits of 5 calls per minute and only provides access to historical, so the program will pause and unpause when necessary and get prices from the previous stock market opening.
   - Go to Polygon.io's [website](https://polygon.io/) and sign up for an account if you do not already have one

   - In your account's dashboard, scroll down to find your API Keys and copy/make note of your default API key

   - If you are using Windows, go to your computer settings, search and select "Edit environmental variables for your account", and add a new environmental variable with the name `Stock_API_Key` and the value of the provided key
 
   - If your using another OS, please check how to access and edit your environmental variables; this process allows your computer to use your own Polygon.io key when running the manager

2) Download files into a folder and download the modules in `requirements.txt` through pip (ideally in a venv)

4) Run `ConsoleScript.py` through python to use the portfolio manager