import pandas as pd
import numpy as np
import os.path
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter

from ..Lib.file_loading_strategies import fileLoadingDF
from ..Lib.zscore_trend_trader import zscoreTrader

cpath = os.path.dirname(__file__) # current path


def fmt(x, pos):
    """
    A Simple format function used for colourbar formatting
    """
    return '{}%'.format(np.round(x*100, 0))

def main():

    save_results = False
    plot_results = True
    if save_results:
        results_outfile = cpath +"\\..\\Data\\deleteme.csv"

    
    # Load Dataframe
    #--------------------------------------------------------------------------
    infile = cpath+"\\..\\Data\\cryptocompareBTC_10000_hours_df.csv"
    loader = fileLoadingDF(infile)
    df = loader.get_data()
    if save_results:
        df_csv = df[['date']]
    #--------------------------------------------------------------------------

    # Define trading parameters
    #--------------------------------------------------------------------------
    symbols = [key for key in df.keys() if key not in ['date']]
    symbols = ['BCH']
    bandwidths = [2.0]#[1.0, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0]
    MAs = [100] #[5, 8, 10, 15, 20, 30, 40, 50, 80, 100, 200, 400]
    num_faster_MAs = 4 # number of faster MAs for each MA
    ZScore_MAs = [15]#[5, 6, 7, 8, 10, 12, 14, 15, 20, 30, 50, 80, 100]
    ylabels = []

    if plot_results:
        returns = np.zeros((len(MAs)*num_faster_MAs, len(ZScore_MAs))) # store final returns
    #--------------------------------------------------------------------------
    
    
    # Execute trading
    #--------------------------------------------------------------------------
    for bandwidth in bandwidths:

        for symbol in symbols:

            for i in range(len(MAs)): 

                # Define SMA periods for trends
                MA = MAs[i]
                faster_MAs = np.linspace(0, MA, num=num_faster_MAs, endpoint=False)
                faster_MAs = [int(item) for item in faster_MAs]

                for k in range(len(faster_MAs)):   
 
                    MAfast = faster_MAs[k]
                    if plot_results:                    
                        ylabels.append('{}v{}'.format(MA,MAfast))

                    for j in range(len(ZScore_MAs)):  
                        Z_MA = ZScore_MAs[j]      
                        asset_df = df[['date', symbol]].reset_index()
                        trader = zscoreTrader(asset_df, symbol, MA,
                                              Z_MA, bandwidth, 
                                              fast_MA_period=MAfast)
                        trader.trade(plot=True)

                        if plot_results:
                            loc = num_faster_MAs*i + k, j # plot location
                            returns[loc] = asset_df['returns'].cumsum().iloc[-1]
                        if save_results:
                            header = '{}_{}_{}_{}'.format(symbol, MA, 
                                                        Z_MA, bandwidth)
                            df_csv[header] = asset_df['returns']

        if plot_results:
            plt.imshow(returns, cmap='RdBu')
            plt.colorbar(format=FuncFormatter(fmt))
            max_ret = max(returns.min(), returns.max(), key=abs)
            plt.clim(vmin=-max_ret, vmax=max_ret)
            plt.yticks(np.arange(len(ylabels)), ylabels)
            plt.xticks(np.arange(len(ZScore_MAs)), ZScore_MAs)
            plt.ylabel("SMA Period")
            plt.xlabel("Z Score Period")
            plt.title("{}/BTC Bandwidth={}".format(symbol, bandwidth))
            if save_results:
                plt.savefig('{}_BTC_bw{}.png'. format(symbol, bandwidth))
            plt.show()
    #--------------------------------------------------------------------------

    if save_results:
        df_csv.to_csv(results_outfile)


if __name__ == "__main__":
    main()