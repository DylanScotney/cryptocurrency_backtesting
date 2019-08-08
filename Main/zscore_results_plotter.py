import os.path
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

cpath = os.path.dirname(__file__) # current path

def fmt(x, pos):
    """
    Function for formatting colorbar plot
    """
    return '{}%'.format(np.round(x, 1))

def main():

    bandwidth = 2.5

    # Load data
    df = pd.read_csv(cpath+"\\..\\Data\\ZScore_Results\\bandwidth_{}.csv".format(bandwidth))

    # Define params
    #--------------------------------------------------------------------------
    total_returns = np.zeros((12,13))
    expected_trade_returns = np.zeros((12,13))
    cumReturns_df = df[['date']]
    trade_rets1 = []
    keys = [key for key in df.keys() if key not in ['date', 'Unnamed: 0', 'ETC', 'BCH', 'MKR']]
    SMAs = [5, 8, 10, 15, 20, 30, 40, 50, 80, 100, 200, 400]
    Zscores = [5, 6, 7, 8, 10, 12, 14, 15, 20, 30, 50, 80, 100]
    #--------------------------------------------------------------------------
    numtrades = 0
    numtrades_best = 0
    count = 0

    while(count < len(keys)):
        print(keys[count])
        for i in range(len(SMAs)):
            for j in range(len(Zscores)):
                
                # Compute total returns
                #--------------------------------------------------------------
                total_returns[i, j] += df[keys[count]].cumsum().iloc[-1]
                #--------------------------------------------------------------

                # Compute expected returns
                #--------------------------------------------------------------
                temp_exp_rets = [ret for ret in df[keys[count]] if ret != 0]
                numtrades += len(temp_exp_rets)
                if i == SMAs.index(400) and j == Zscores.index(10):
                    numtrades_best += len(temp_exp_rets)
                    for ret in df[keys[count]]:
                        if ret!=0:
                            trade_rets1.append(ret*100)
                if temp_exp_rets:
                    expected_trade_returns[i, j] += np.mean(temp_exp_rets)
                else: 
                    expected_trade_returns[i, j] += 0
                #--------------------------------------------------------------

                count += 1 # count total iters for key location
        
    
    total_returns = total_returns*100/20.0 # 23 assets so get average
    expected_trade_returns = expected_trade_returns*100/20.0
    print("Number of trades: {}".format(numtrades))
    print("Best performer returns: {}".format(total_returns[SMAs.index(200), Zscores.index(15)]))
    print("Best performer ave return: {}".format(expected_trade_returns[SMAs.index(200), Zscores.index(15)]))
    print("Best performer ave trades: {}".format(numtrades_best/20))

    plt.subplot(121)
    plt.imshow(total_returns, cmap='RdBu')
    plt.colorbar(format = FuncFormatter(fmt))
    max_ret = np.amax(np.fabs(total_returns))
    plt.clim(vmin=-max_ret, vmax=max_ret)
    plt.yticks(np.arange(len(SMAs)), SMAs)
    plt.xticks(np.arange(len(Zscores)), Zscores)
    plt.title("Average Returns Bandwidth = {}".format(bandwidth))
    plt.xlabel("Z Score Period")
    plt.ylabel("SMA Period")

    plt.subplot(122)
    plt.imshow(expected_trade_returns, cmap='RdBu')
    plt.colorbar(format = FuncFormatter(fmt))
    max_ret = np.amax(np.fabs(expected_trade_returns))
    plt.clim(vmin=-max_ret, vmax=max_ret)
    plt.yticks(np.arange(len(SMAs)), SMAs)
    plt.xticks(np.arange(len(Zscores)), Zscores)
    plt.title("Expected Trade Return Bandwidth = {}".format(bandwidth))
    plt.xlabel("Z Score Period")
    plt.ylabel("SMA Period")
    plt.show()
    
    weights = np.ones_like(trade_rets1)/float(len(trade_rets1))
    plt.hist(trade_rets1, weights=weights, bins=100, range = [-20, 20])
    plt.ylabel("Probability")
    plt.xlabel("Return (%)")
    plt.show()


if __name__ == "__main__":
    main()

