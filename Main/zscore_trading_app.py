import pandas as pd
import numpy as np
import os.path
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter

from ..Lib.data_loading.file_loading_strategies import fileLoadingDF
from ..Lib.strategies.zscore_trend import zScoreTrader
from ..Lib.strategy_backtester import backtest

cpath = os.path.dirname(__file__) # current path


def main():

    # Load Dataframe
    #--------------------------------------------------------------------------
    infile = cpath+"\\..\\Data\\mock_df.csv"
    loader = fileLoadingDF(infile)
    df = loader.get_data()
    df_csv = df[['date']]
    #--------------------------------------------------------------------------
    
    # Define trading parameters
    #--------------------------------------------------------------------------    
    save_results = False
    plot_results = True
    results_outfile = "dualSMAZscores"

    symbols = [key for key in df.keys() if key not in ['date']]
    bandwidths = [1.0, 1.5, 2.0]
    MAs = [80, 100]
    num_faster_MAs = 3 # number of faster MAs for each MA
    ZScore_MAs = [5, 8, 12]
    #--------------------------------------------------------------------------
    
    # Execute trading
    #--------------------------------------------------------------------------
    for bandwidth in bandwidths:
        if save_results:
            df_csv = df[['date']]
        returns = np.zeros((len(MAs)*num_faster_MAs, len(ZScore_MAs))) 
        ylabels = [] # plot labels

        for iter_cnt, symbol in enumerate(symbols):
            for i in range(len(MAs)): 
                MAslow = MAs[i]
                faster_MAs = np.linspace(1, MAslow, num=num_faster_MAs, 
                                         endpoint=False)
                faster_MAs = [int(item) for item in faster_MAs]
                for k in range(num_faster_MAs):    
                    MAfast = faster_MAs[k]
                    if iter_cnt == 0:     
                        # only append for first symbol so no repetitions 
                        if num_faster_MAs == 1:
                            ylabels.append(MAslow)
                        else:
                            ylabels.append('{}v{}'.format(MAslow, MAfast))                        

                    for j in range(len(ZScore_MAs)):
                        Z_MA = ZScore_MAs[j]                        
                        print("Trading {} for Z score: {}, SMAs: {}v{}"
                              .format(symbol, Z_MA, MAfast, MAslow))

                        asset_df = df.loc[:, ['date', symbol]].reset_index()
                        strategy = zScoreTrader(asset_df, symbol, "SMA", 
                                                MAslow, Z_MA, bandwidth, 
                                                fast_MA=MAfast)
                        trader = backtest(strategy)
                        cum_returns = trader.trade()
                        loc = num_faster_MAs*i + k, j 
                        returns[loc] += cum_returns

                        print("Cumulative returns: {0:.2}%\n"
                              .format(cum_returns*100))

                        if save_results:
                            key = '{}_{}v{}_{}_{}'.format(symbol, MAslow, 
                                                         MAfast, Z_MA, 
                                                         bandwidth)
                            df_csv[key] = asset_df['returns']
        # ---------------------------------------------------------------------

        # Plot Results
        # ---------------------------------------------------------------------
        if plot_results:            
            num_symbols = len(symbols)
            returns = returns*100/num_symbols # average percentage rets
            plt.imshow(returns, cmap='RdBu')
            plt.colorbar(format=FuncFormatter(fmt))
            max_ret = max(returns.min(), returns.max(), key=abs)
            plt.clim(vmin=-max_ret, vmax=max_ret)
            plt.yticks(np.arange(len(ylabels)), ylabels)
            plt.xticks(np.arange(len(ZScore_MAs)), ZScore_MAs)
            plt.ylabel("SMA Period")
            plt.xlabel("Z Score Period")
            plt.title("Total Returns Bandwidth={}".format(bandwidth))
            plt.show()
        #----------------------------------------------------------------------

        if save_results:
            df_csv.to_csv(results_outfile)
   
def fmt(x, pos):
    """
    Formats colourbar to display as a percentage
    """
    return '{}%'.format(np.round(x, 0))

if __name__ == "__main__":
    main()