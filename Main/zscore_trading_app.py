import pandas as pd
import numpy as np
import os.path
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter

from ..Lib.data_loading.file_loading_strategies import fileLoadingDF
from ..Lib.trading_strat_zscore import zScoreTrader
from ..Lib.strategy_backtester import backtest

cpath = os.path.dirname(__file__) # current path


def main():

    # Load Dataframe
    #--------------------------------------------------------------------------
    infile = cpath+"\\..\\Data\\cryptocompareBTC_10000_hours_df.csv"
    loader = fileLoadingDF(infile)
    df = loader.get_data()
    df_csv = df[['date']]
    #--------------------------------------------------------------------------
    
    # Define trading parameters
    #--------------------------------------------------------------------------    
    save_results = False
    plot_results = True
    if save_results:
        results_outfile = "dualSMAZscores"

    symbols = [key for key in df.keys() if key not in ['date']]
    bandwidths = [2.5]#[1.0, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0]
    MAs = [400]#[5,8,10,15,20, 30,40,50,80,100,200,400]
    num_faster_MAs = 1 # number of faster MAs for each MAslow
    ZScore_MAs = [10]#[5,6,7,8,10,12,14,15,20,30,50,80,100] 
    ylabels = []
    #--------------------------------------------------------------------------
    
    # Execute trading
    #--------------------------------------------------------------------------
    for bandwidth in bandwidths:
        if save_results:
            df_csv = df[['date']]
        if plot_results:
            returns = np.zeros((len(MAs)*num_faster_MAs, len(ZScore_MAs))) 
            ave_returns = np.zeros((len(MAs)*num_faster_MAs, len(ZScore_MAs))) 
        num_trades = 0
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
                        if num_faster_MAs == 1:
                            ylabels.append(MAslow)
                        else:
                            ylabels.append('{}v{}'.format(MAslow, MAfast))
                        

                    for j in range(len(ZScore_MAs)):  
                        Z_MA = ZScore_MAs[j]                                
                        print("Trading {} for {}v{} {} bw={}".format(symbol,
                                                                     MAslow, 
                                                                     MAfast, 
                                                                     Z_MA, 
                                                                     bandwidth))  
                        asset_df = df.loc[5000:8000, ['date', symbol]].reset_index()
                        strategy = zScoreTrader(asset_df, symbol, "SMA", 
                                                MAslow, Z_MA, bandwidth, 
                                                fast_MA=MAfast)
                        trader = backtest(strategy)
                        trader.trade()

                        if plot_results:
                            loc = num_faster_MAs*i + k, j 
                            returns[loc] += asset_df['returns'].cumsum().iloc[-1]
                            trade_rets = [ret for ret in asset_df['returns'] if ret != 0]
                            ave_returns[loc] = np.mean(trade_rets)
                            num_trades += len(trade_rets)

                        if save_results:
                            key = '{}_{}v{}_{}_{}'.format(symbol, MAslow, 
                                                         MAfast, Z_MA, 
                                                         bandwidth)
                            df_csv[key] = asset_df['returns']
            count+=1
        
        if plot_results:            
            num_symbols = len(symbols)
            returns = returns*100/num_symbols # average percentage rets
            ave_returns = ave_returns*100/num_symbols
            print(returns)
            print(ave_returns)
            print(num_trades)
            plt.subplot(121)
            plt.imshow(returns, cmap='RdBu')
            plt.colorbar(format=FuncFormatter(fmt1))
            max_ret = max(returns.min(), returns.max(), key=abs)
            plt.clim(vmin=-max_ret, vmax=max_ret)
            plt.yticks(np.arange(len(ylabels)), ylabels)
            plt.xticks(np.arange(len(ZScore_MAs)), ZScore_MAs)
            plt.ylabel("SMA Period")
            plt.xlabel("Z Score Period")
            plt.title("Total Returns Bandwidth={}".format(bandwidth))

            plt.subplot(122)
            plt.imshow(ave_returns, cmap='RdBu')
            plt.colorbar(format=FuncFormatter(fmt2))
            max_ret = max(ave_returns.min(), ave_returns.max(), key=abs)
            plt.clim(vmin=-max_ret, vmax=max_ret)
            plt.yticks(np.arange(len(ylabels)), ylabels)
            plt.xticks(np.arange(len(ZScore_MAs)), ZScore_MAs)
            plt.ylabel("SMA Period")
            plt.xlabel("Z Score Period")
            plt.title("Expected Returns Bandwidth={}".format(bandwidth))
            if save_results:
                plt.savefig('{}_BTC_bw{}.png'. format(symbol, bandwidth))
            plt.show()


        print(num_trades)
        if save_results:
            outfile = cpath +"\\..\\Data\\{}_bw{}.csv".format(results_outfile, 
                                                              bandwidth)
            df_csv.to_csv(results_outfile)
    #--------------------------------------------------------------------------


def fmt1(x, pos):
    """
    Formats colourbar to display as a percentage
    """
    return '{}%'.format(np.round(x, 0))

def fmt2(x, pos):
    """
    Formats colourbar to display as a percentage
    """
    return '{}%'.format(np.round(x, 2))


if __name__ == "__main__":
    main()