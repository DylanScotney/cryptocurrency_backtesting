import numpy as np
import pandas as pd
import os.path
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter
from datetime import datetime

from ..Lib.data_loader import dataLoader
from ..Lib.file_loading_strategies import fileLoadingDF, fileLoadingRaw
from ..Lib.web_loading_strategies import webLoading
from ..Lib.crossover_trading_strategy import crossoverTrader
from ..Lib.strategy_backtester import backtest

cpath = os.path.dirname(__file__) # current path

def main(): 

    save_results = False
    plot_results = True
    MA_type = 'SMA'
    if save_results:
        results_outfile = cpath + "\\..\\Data\\EMA_results.csv"
    symbols = [symbol.rstrip('\n') for symbol in open(cpath+"\\..\\Data\\list_of_tickers.txt")]

    # Load Dataframe
    #--------------------------------------------------------------------------
    infile = cpath + "\\..\\Data\\cryptocompareBTC_10000_hours_df.csv"    
    loading_strat = fileLoadingDF(infile)
    loader = dataLoader(loading_strat)
    df = loader.get_data()
    if save_results:
        df_csv = df[['date']]
    #--------------------------------------------------------------------------

    # Define Trading Parameters
    #--------------------------------------------------------------------------
    symbols = [key for key in df.keys() if key not in ['date', 'ETC', 'BCH', 'MKR']]
    symbols = ['QTUM']
    MA_list = [1, 10, 20, 40, 50, 80, 100, 120, 160, 200, 240, 280, 320, 360, 400]
    MA_list = [1, 10, 400]
    if plot_results:
        returns = np.zeros((len(MA_list), len(MA_list))) # store final returns
    #--------------------------------------------------------------------------
    
    # Execute Trading
    #--------------------------------------------------------------------------
    for symbol in symbols:
        for i in range(len(MA_list)):
            for j in range(i+1, len(MA_list)):
                fast_MA = MA_list[i]                
                slow_MA = MA_list[j]

                print("Trading {} for {} v {}".format(symbol, slow_MA, fast_MA))

                asset_df = df[['date', symbol]].reset_index()
                strategy = crossoverTrader(asset_df, symbol, MA_type, slow_MA, 
                                           fast_MA=fast_MA, trading_fee=0.0)
                trader = backtest(strategy, plot_results=True)
                trader.trade()

                if plot_results:
                    returns[j, i] += asset_df['returns'].cumsum().iloc[-1]
                if save_results:
                    header = '{}_{}_{}'.format(symbol, slow_MA, fast_MA)
                    df_csv[header] = asset_df['returns']
    #--------------------------------------------------------------------------

    # Plot Results
    #--------------------------------------------------------------------------
    num_symbols = float(len(symbols))
    returns = returns*100/num_symbols # average returns as a percentage

    if plot_results:
        plt.imshow(returns, cmap='RdBu')
        plt.colorbar(format=FuncFormatter(fmt))        
        max_ret = np.nanmax(abs(returns))
        plt.clim(vmin=-max_ret, vmax=max_ret)
        plt.yticks(np.arange(len(MA_list)), MA_list)
        plt.xticks(np.arange(len(MA_list)), MA_list)
        plt.ylabel("{} Period".format(MA_type))
        plt.xlabel("{} Period".format(MA_type))
        plt.title("Average Returns")
        if save_results:
            plt.savefig('Returns_{}.png'.format(MA_type))
        plt.show()
    #--------------------------------------------------------------------------

    # Store Results
    #--------------------------------------------------------------------------
    if save_results:
        df_csv.to_csv(results_outfile)
    #--------------------------------------------------------------------------


def fmt(x, pos):
    """
    Formats colourbar values to use percentages
    """
    return '{}%'.format(np.round(x, 0))


if __name__ == "__main__":
    main()