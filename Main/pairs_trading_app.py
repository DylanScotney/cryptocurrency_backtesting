import os.path
import numpy as np
from statsmodels.tsa.stattools import coint
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter

from ..Lib.data_loading.file_loading_strategies import fileLoadingDF
from ..Lib.data_loading.data_loader import dataLoader
from ..Lib.strategies.pairs import pairsTrader
from ..Lib.strategy_backtester import backtest

cpath = os.path.dirname(__file__)  # current path

def main():

    # Load data
    # -------------------------------------------------------------------------
    infile = cpath + "\\..\\Data\\mock_df.csv" 
    save_results = False   
    loading_strat = fileLoadingDF(infile)
    loader = dataLoader(loading_strat)
    df = loader.get_data()
    if save_results:
        df_csv = df[['date']].drop(columns=['date'])
    df = df.drop(columns=['date'])
    # -------------------------------------------------------------------------

    # Get Cointegrated Pairs
    # -------------------------------------------------------------------------
    _, pairs = get_coint_pairs(df)    
    # -------------------------------------------------------------------------

    # Define trading params
    # -------------------------------------------------------------------------
    zperiods = [5, 8, 12, 20, 50]
    bandwidths = [1.0, 1.5, 2.0]    
    returns = np.zeros((len(bandwidths), len(zperiods)))
    # -------------------------------------------------------------------------

    # Execute trading
    # -------------------------------------------------------------------------
    for i in range(len(bandwidths)):
        bandwidth = bandwidths[i]        
        for j in range(len(zperiods)):
            period = zperiods[j]
            for pair in pairs:
                asset1, asset2 = pair[0], pair[1]                
                print("Trading {} against {} for BW: {}, Z period: {}"
                      .format(asset1, asset2, bandwidth, period))

                x = df.loc[:, asset1]
                y = df.loc[:, asset2]
                strategy = pairsTrader(x, y, asset1, asset2, 
                                       period, bandwidth=bandwidth)
                trader = backtest(strategy)
                trader.trade()
                cum_returns = strategy.df['returns'].cumsum().iloc[-1]
                returns[i, j] += cum_returns
                print("Cumulative Returns: {0:.2f}%\n"
                      .format(cum_returns*100))

                if save_results:
                    header = asset1+"_"+asset2+"_"+str(bandwidth)+"_"+ str(period)
                    df_csv[header] = strategy.df['returns']

    if save_results:
        df_csv.to_csv("results.csv")
    # -------------------------------------------------------------------------
    
    # Plot
    # -------------------------------------------------------------------------
    returns = returns*100/len(pairs)
    plt.imshow(returns, cmap='RdBu')
    plt.colorbar(format=FuncFormatter(fmt))
    max_ret = max(returns.min(), returns.max(), key=abs)
    plt.clim(vmin=-max_ret, vmax=max_ret)
    plt.xticks(np.arange(len(zperiods)), zperiods)
    plt.yticks(np.arange(len(bandwidths)), bandwidths)
    plt.xlabel("Z Score Period")
    plt.ylabel("Bandwidth")
    plt.title("Total Returns Bandwidth={}".format(bandwidth))
    plt.show()
    # -------------------------------------------------------------------------

def get_coint_pairs(df, threshold=0.05, plot=False):

    """
    Determines cointegrated pairs of 2 or more assets for a given 
    theshold. 

    Inputs:
    - df:           (pandas Dataframe) dataframe storing asset price history
    - threshold:    (float) cointegration threshold

    Outputs:
    - p_values:     (2D array, floats) storing pvalues between pairs 
    - pairs:        (list) of cointegrated pairs w/ their coint factor. 
    """

    symbols = [symbol for symbol in df.keys()]
    num_assets = len(symbols)
    p_values = np.ones((num_assets, num_assets))
    pairs = []

    for j in range(num_assets):
        for i in range(j+1, num_assets):
            asset1 = symbols[i]
            asset2 = symbols[j]            
            _, pval, _ = coint(df[asset1], df[asset2])

            if pval < threshold:
                pairs.append([asset1, asset2, pval])
                print("{} and {} are cointegrated with p value: {}\n"
                      .format(asset1, asset2, pval))
            
            p_values[i, j] = pval
    
    if(plot):
        mask = np.triu(p_values)
        p_values = np.ma.array(p_values, mask=mask) 
        plt.imshow(p_values, cmap = 'Spectral')
        plt.colorbar()
        plt.xticks(np.arange(num_assets), symbols, rotation=90)
        plt.yticks(np.arange(num_assets), symbols)
        plt.title("co-integration factor between top {} assets".format(num_assets))
        plt.show()

    return p_values, pairs

def fmt(x, pos):
    """
    Formats colourbar to display as a percentage
    """
    return '{}%'.format(np.round(x, 0))
    
if __name__ == "__main__":
    main()