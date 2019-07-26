import pandas as pd
import numpy as np
import os.path
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter

from ..Lib.file_loading_strategies import fileLoadingDF
from ..Lib.trading_strat_zscore import zScoreTrader
from ..Lib.strategy_backtester import backtest

cpath = os.path.dirname(__file__) # current path


def main():

    save_results = False
    plot_results = True
    if save_results:
        results_outfile = "dualSMAZscores"
    
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
    symbols = ['ETH']
    bandwidths = [2.0]#[1.0, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0]
    MAs = [40, 80]
    num_faster_MAs = 4 # number of faster MAs for each MAslow
    ZScore_MAs = [2, 3, 4, 5, 10]
    ylabels = []
    #--------------------------------------------------------------------------
    
    # Execute trading
    #--------------------------------------------------------------------------
    for bandwidth in bandwidths:
        if save_results:
            df_csv = df[['date']]
        if plot_results:
            returns = np.zeros((len(MAs)*num_faster_MAs, len(ZScore_MAs))) 

        for count, symbol in enumerate(symbols):

            for i in range(len(MAs)): 
                MAslow = MAs[i]
                faster_MAs = np.linspace(1, MAslow, num=num_faster_MAs, 
                                         endpoint=False)
                faster_MAs = [int(item) for item in faster_MAs]

                for k in range(num_faster_MAs):    
                    MAfast = faster_MAs[k]
                    if plot_results and count==0:     
                        # only append for first symbol so no repetitions               
                        ylabels.append('{}v{}'.format(MAslow, MAfast))

                    for j in range(len(ZScore_MAs)):  
                        Z_MA = ZScore_MAs[j]                                
                        print("Trading {} for {}v{} {} bw={}".format(symbol,
                                                                     MAslow, 
                                                                     MAfast, 
                                                                     Z_MA, 
                                                                     bandwidth))  
                        asset_df = df[['date', symbol]].reset_index()
                        strategy = zScoreTrader(asset_df, symbol, "SMA", 
                                                MAslow, Z_MA, bandwidth, 
                                                fast_MA=MAfast)
                        trader = backtest(strategy, plot_results=True)
                        trader.trade()

                        if plot_results:
                            loc = num_faster_MAs*i + k, j 
                            returns[loc] += asset_df['returns'].cumsum().iloc[-1]

                        if save_results:
                            key = '{}_{}v{}_{}_{}'.format(symbol, MAslow, 
                                                         MAfast, Z_MA, 
                                                         bandwidth)
                            df_csv[key] = asset_df['returns']
            count+=1

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
            if save_results:
                plt.savefig('{}_BTC_bw{}.png'. format(symbol, bandwidth))
            plt.show()
        
        if save_results:
            outfile = cpath +"\\..\\Data\\{}_bw{}.csv".format(results_outfile, 
                                                              bandwidth)
            df_csv.to_csv(results_outfile)
    #--------------------------------------------------------------------------


def fmt(x, pos):
    """
    Formats colourbar to display as a percentage
    """
    return '{}%'.format(np.round(x, 0))
    


if __name__ == "__main__":
    main()