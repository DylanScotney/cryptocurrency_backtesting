import numpy as np
import pandas as pd
import os.path
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter

from ..Lib.data_loader import dataLoader
from ..Lib.file_loading_strategies import fileLoadingDF, fileLoadingRaw
from ..Lib.cross_over_trader import crossOverTrading

cpath = os.path.dirname(__file__) # current path

def fmt(x, pos):
    """
    A Simple format function used for colourbar formatting
    """
    return '{}%'.format(np.round(x*100, 0))


def main(): 

    save_results = True
    plot_results = True
    MA_type = 'SMA'
    if save_results:
        results_outfile = cpath + "\\..\\Data\\deleteme.csv"

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
    symbols = [key for key in df.keys() if key not in ['date']]
    MA_list = [1, 10, 20, 40, 50, 80, 100, 120, 160]#, 200, 240, 280, 320, 360, 400]
    if plot_results:
        returns = np.zeros((len(MA_list), len(MA_list))) # store final returns
    #--------------------------------------------------------------------------
   
    
    # Execute Trading
    #--------------------------------------------------------------------------
    for symbol in symbols:
        for i in range(len(MA_list)):
            for j in range(i+1, len(MA_list)):
                MAs = MA_list[j]
                MAf = MA_list[i]
                print("Trading {} for {} v {}".format(symbol, MAs, MAf))
                asset_df = df[['date', symbol]].reset_index()
                trader = crossOverTrading(asset_df, symbol, MAf, MAs, MA_type, trading_fee=0.001)
                trader.trade()

                if plot_results:
                    returns[j, i] = asset_df['returns'].cumsum().iloc[-1]
                if save_results:
                    header = '{}_{}_{}'.format(symbol, MAs, MAf)
                    df_csv[header] = asset_df['returns']
        
        if plot_results:
            plt.imshow(returns, cmap='RdBu')
            plt.colorbar(format=FuncFormatter(fmt))
            max_ret = max(returns.min(), returns.max(), key=abs)
            plt.clim(vmin=-max_ret, vmax=max_ret)
            plt.yticks(np.arange(len(MA_list)), MA_list)
            plt.xticks(np.arange(len(MA_list)), MA_list)
            plt.ylabel("{} Period".format(MA_type))
            plt.xlabel("{} Period".format(MA_type))
            plt.title("{}/BTC Returns".format(symbol))
            if save_results:
                plt.savefig('{}_BTC_MAs.png'. format(symbol))
            plt.show()
    #--------------------------------------------------------------------------

    if save_results:
        df_csv.to_csv(results_outfile)


if __name__ == "__main__":
    main()