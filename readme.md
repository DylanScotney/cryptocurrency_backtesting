# Title
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

#### Requirements:
This package uses the following libraries, and any of their dependencies. 

* abc
* datetime
* json
* maths
* matplotlib
* numpy
* pykalman
* requests
* statsmodels ([NOTE: Incompatible with SciPy 1.13 [20/06/2019]](https://github.com/statsmodels/statsmodels/issues/5759)) 


## Code Overview

#### Data Loading
Data loading/management is built using a strategy pattern:

* Context class: [dataLoader](\\Lib\\data_loader.py)
* abstract interface class: [dataLoadingStrat](\\Lib\\data_loading_strategy.py)
* concrete implementation 1: [webLoading](\\Lib\\web_loading_strategies.py)
* concrete implentation 2: [fileLoadingRaw](\\Lib\\file_loading_strategies.py)
* concrete implementation 3: [fileLoadingDF](\\Lib\\file_loading_strategies.py)

An example useage: 
```
loading_strat = fileLoadingDF(infile)
loader = dataLoader(loading_strat)
data = loader.get_data()
```


