# The Validation of Systematic Trading Strategies Applied to the Cryptocurrency Market



## Dylan Scotney
### Accompanying code for a dissertation submitted in partial fulfilment  of the requirements for the degree of  Master of Science of University College London

#

This package was written in order to validate some trading strategies
applied to the crytocurrency market. 
Data was sourced from the [CryptoCompare API](https://min-api.cryptocompare.com). 
Data from CryptoCompare is sourced from an aggregated feed of over 150 
crypto exchanges giving you reliable and up-to-date traded rates that 
are used globally. We have systems in place to remove irregular prices, 
giving you the cleanest prices available. [Read more](https://www.cryptocompare.com/media/27010937/cccagg_methodology_2018-02-26.pdf).

## **Dependencies**:
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

### **Data Loading**
Data loading/management is built using a strategy pattern:

* Context class: [dataLoader()](\\Lib\\data_loading\\data_loader.py)
* Abstract interface class: [dataLoadingStrat()](\\Lib\\data_loading\\abstract_data_loading_strategy.py)
* Concrete implementation 1: [webLoading()](\\Lib\\data_loading\\web_loading_strategies.py)
* Concrete implentation 2: [fileLoadingRaw()](\\Lib\\data_loading\\file_loading_strategies.py)
* Concrete implementation 3: [fileLoadingDF()](\\Lib\\data_loading\\file_loading_strategies.py)

Example useage:

webLoading()
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

fileloadingRaw()
```
infile = "myrawdata.json" # raw data stored by webLoading
symbols = [sym.rstrip('\n') for sym in open("alistofsymbols.txt")]
ticksize = "hour"

loading_strat = fileLoadingRaw(infile)
loader = dataLoader(loading_strat)
data = loader.get_data()
```

fileloadingDF()
```
infile = "mydataframe.csv"
loading_strat = fileLoadingDF(infile) 
loader = dataLoader(loading_strat)
data = loader.get_data()
```

All three approaches store close prices in a pandas dataframe along with 
corresponding dates


### **Custom Types**
To handle data and strategies in an object oriented manner, several 
custom types/classes were created these were: 
* [Position](\\Lib\\types\\position.py)
* [zScore](\\Lib\\types\\zscore.py)
* [simpleMovingAverage](\\Lib\\types\\simple_moving_average.py)
* [expMovingAverage](\\Lib\\types\\exponential_moving_average.py)



### **Backtesting Strategies**
All backtesting strategies were built to use a fixed position sizing. 
Trading strateies are built and tested again using a stratergy pattern:
* Context class: [backtest()](\\Lib\\strategy_backtester.py)
* Abstract interface class: [movingAverageTrader()](\\Lib\\strategies\\abstract_MA.py)
* Concrete implmentation 1: [crossoverTrader()](\\Lib\\strategies\\crossover.py)
* Concrete implementation 2: [zScoreTrader()](\\Lib\\strategies\\zscore_trend.py)
* Seperate implementation: [pairsTrader()](\\Lib\\strategies\\pairs.py)

Note: pairsTrader() does not inherit from movingAverageTrader() like 
crossoverTrader() and zScoreTrader() because spread data changes as 
trades are made so implementation has a different approach. General 
format and layout of classes remain consistent. 

**Example usage**:

crossoverTrader()
```
df = <pandas df containing close prices>
symbol = <asset ticker> # must correspond to header in df
MA_type = "SMA" # simple moving average
MAslow = 40 # period of slow MA
MAfast = 10 # period of fast MA

strategy = crossoverTrading(df, symbol, MA_type, MAslow, fast_MA=MAfast)
trader = backtest(strategy, plot_results=True)
trader.trade()
```

zScoreTrader()
```
df = <pandas df containing close prices>
symbol = <asset ticker> # must correspond to header in df
MA_type = "SMA" # simple moving average
MAslow = 40 # period of slow MA
MAfast = 10 # period of fast MA
Z_period = 5 # lookback period for determining z score
bw = 2 # bandwidth for trading logic

strategy = zScoreTrading(df, symbol, MA_type, MAslow, 
                        Z_period, bw, fast_MA=MAfast)
trader = backtest(strategy)
trader.trade()
```

pairsTrader()
```
x = <pandas series of first asset>
y = <pandas series of second asset>
xlabel = "x"  # label for x series
ylabel = "y"  # label for y series
period = 10  # z score period
bw = 2.0  # bandwidth

strategy = pairsTrader(x, y, xlabel, ylabel, period, bandwidth=bw)
trader = backtest(strategy)
trader.trade()
```



