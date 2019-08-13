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
    #--------------------------------------------------------------------------
    infile = cpath + "\\..\\Data\\cryptocompareBTC_10000_hours_df.csv"    
    loading_strat = fileLoadingDF(infile)
    loader = dataLoader(loading_strat)
    df = loader.get_data()    
    df_csv = df[['date']].drop(columns=['date'])
    df = df.drop(columns=['date', 'ETC', 'BCH', 'MKR'])
    #--------------------------------------------------------------------------
    #get_coint_pairs(df, plot=True)
    pairs = [['NEO', 'ETH', 0.003612165730626407],
             ['NEO', 'EOS', 0.008579662928821775],
             ['ONT', 'EOS', 0.03422087889318235],
             ['QTUM', 'EOS', 0.012311951642757703],
             ['NEO', 'MIOTA', 2.77966317024553e-07],
             ['XEM', 'MIOTA', 0.02346824963834761],
             ['QTUM', 'MIOTA', 2.859898428527098e-06],
             ['OMG', 'MIOTA', 0.003068642272049997],
             ['STRAT', 'MIOTA', 0.0019609430836286146],
             ['QTUM', 'NEO', 0.012653497760793497],
             ['OMG', 'NEO', 5.1355649728857575e-08],
             ['ZRX', 'ZEC', 0.009726960805872743],
             ['OMG', 'QTUM', 6.816664786159693e-05],
             ['STRAT', 'QTUM', 0.021838747291384023]]
    pairs = [['QTUM', 'MIOTA']]
    zperiods = [7]#[5,7,8,9,10,12,15,20,50,100]
    bandwidths = [2.0]#, 1.5, 1.75, 2.0, 2.25, 2.5]    
    returns = np.zeros((len(bandwidths), len(zperiods)))
    for i in range(len(bandwidths)):
        bandwidth = bandwidths[i]        
        for j in range(len(zperiods)):
            period = zperiods[j]
            for pair in pairs:
                asset1, asset2 = pair[0], pair[1]
                print(asset1, asset2, bandwidth, period)
                x = df.loc[:1000, asset1]
                y = df.loc[:1000, asset2]
                strategy = pairsTrader(x, y, asset1, asset2, 
                                     zperiod=period, bandwidth=bandwidth)
                trader = backtest(strategy, plot_results=True)
                trader.trade()
                returns[i, j] += strategy.df['returns'].cumsum().iloc[-1]

                header = asset1+"_"+asset2+"_"+str(bandwidth)+"_"+ str(period)
                df_csv[header] = strategy.df['returns']
    
    df_csv.to_csv("test.csv")

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
    print(symbols)
    p_values = np.ones((num_assets, num_assets))
    pairs = []

    for j in range(num_assets):
        for i in range(j+1, num_assets):
            asset1 = symbols[i]
            asset2 = symbols[j]            
            _, pval, _ = coint(df[asset1], df[asset2])

            if pval < threshold:
                pairs.append([asset1, asset2, pval])
                print([asset1, asset2, pval])
            
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