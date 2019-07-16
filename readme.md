# (--Title--)
## Dylan Scotney
### _Deparment of Physics, University College London_ 
### Accompanying code for [Thesis](---Add Thesis File---)

#

This package was written in order to validate some trading algorithms
applied to the crytocurrency market. 
Data was sourced from the [CryptoCompare API](https://min-api.cryptocompare.com). 
Data from CryptoCompare is sourced from an aggregated feed of over 150 
crypto exchanges giving you reliable and up-to-date traded rates that 
are used globally. We have systems in place to remove irregular prices, 
giving you the cleanest prices available. [Read more](https://www.cryptocompare.com/media/27010937/cccagg_methodology_2018-02-26.pdf).

#### Dependencies:
This package uses the following libraries, and any of their subsequent dependencies. 

* abc
* datetime
* json
* matplotlib
* numpy
* pandas
* pykalman
* requests
* statsmodels ([NOTE: Incompatible with SciPy 1.13 [20/06/2019]](https://github.com/statsmodels/statsmodels/issues/5759)) 


## Code Overview

#### Data Loading
Data loading/management is built using a strategy pattern:

* Context class: [dataLoader](\\Lib\\data_loader.py)
* abstract interface class: [dataLoadingStrat](\\Lib\\abstract_data_loading_strategy.py)
* concrete implementation 1: [webLoading](\\Lib\\web_loading_strategies.py)
* concrete implentation 2: [fileLoadingRaw](\\Lib\\file_loading_strategies.py)
* concrete implementation 3: [fileLoadingDF](\\Lib\\file_loading_strategies.py)

Example useage:

webLoading
```
symbols = [sym.rstrip('\n') for sym in open("alistofsymbols.txt")]
ticksize = "hour"
enddate = datetime(2019,6,1) # using datetime module 
lookback = 100 # get 100 hours
outfile_raw = "myrawdata.json" # store raw data here
outfile_df = "mycloseprices.csv" #store dataframe of closes here

loading_strat = webLoading(symbols, ticksize, enddate, lookback,
                           outfile_raw, outfile_df)
loader = dataLoader(loading_strat)
data = loader.get_data()
```

fileloadingRaw
```
infile = "myrawdata.json" # raw data stored by webLoading
symbols = [sym.rstrip('\n') for sym in open("alistofsymbols.txt")]
ticksize = "hour"

loading_strat = fileLoadingRaw(infile)
loader = dataLoader(loading_strat)
data = loader.get_data()
```

fileloadingDF
```
infile = "mydataframe.csv"
loading_strat = fileLoadingDF(infile) 
loader = dataLoader(loading_strat)
data = loader.get_data()
```

All three approaches store close prices in a pandas dataframe along with 
corresponding dates

#### Backtesting
Trading strateies are built and tested again using a stratergy pattern:
* Context class: [backtest](\\Lib\\strategy_backtester.py)
* Abstract interface class: [movingAverageTrading](\\Lib\\abstract_MA_trading_strategy.py)




