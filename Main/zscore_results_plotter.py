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
    return '{}%'.format(np.round(x*100, 0))

def main():

    bandwidth = 3.0
    plot_trade_distributions = False

    # Load data
    df = pd.read_csv(cpath+"\\..\\Data\\ZScore_Results\\bandwidth_{}.csv".format(bandwidth))

    # Define params
    #--------------------------------------------------------------------------
    total_returns = np.zeros((12,13))
    expected_trade_returns = np.zeros((12,13))
    cumReturns_df = df[['date']]
    trade_rets1 = []
    trade_rets2 = []
    trade_rets3 = []
    keys = [key for key in df.keys() if key not in ['date', 'Unnamed: 0']]
    SMAs = [5, 8, 10, 15, 20, 30, 40, 50, 80, 100, 200, 400]
    Zscores = [5, 6, 7, 8, 10, 12, 14, 15, 20, 30, 50, 80, 100]
    #--------------------------------------------------------------------------
    for ma in SMAs:
        for score in Zscores:
            cumReturns_df['{}SMA_{}Z'.format(ma, score)] = 0.0
    cumReturns_keys = [key for key in cumReturns_df.keys() if key not in ['date']]

    count = 0
    while(count < len(keys)):
        print(keys[count])
        count2 = 0
        for i in range(12):
            for j in range(13):
                
                # Compute total returns
                #--------------------------------------------------------------
                total_returns[i, j] += df[keys[count]].cumsum().iloc[-1]
                cumReturns_df[cumReturns_keys[count2]] += df[keys[count]].cumsum()*100
                #--------------------------------------------------------------

                # Compute expected returns
                #--------------------------------------------------------------
                temp_exp_rets = []
                for ret in df[keys[count]]:
                    if ret != 0:
                        temp_exp_rets.append(ret*100)
                if temp_exp_rets:
                    expected_trade_returns[i, j] += np.mean(temp_exp_rets)
                else:
                    expected_trade_returns[i, j] = 0
                #--------------------------------------------------------------

                if plot_trade_distributions:
                    if i == 11 and j == 6:
                        for ret in df[keys[count]]:
                            if ret != 0:
                                trade_rets1.append(ret*100)
                    if i == 9 and j == 8:
                        for ret in df[keys[count]]:
                            if ret != 0:
                                trade_rets2.append(ret*100)
                    if i == 11 and j == 9:
                        for ret in df[keys[count]]:
                            if ret != 0:
                                trade_rets3.append(ret*100)

                count += 1 # count total iters for key location
                count2 += 1
        

    total_returns = total_returns/23.0 # 23 assets so get average
    expected_trade_returns = expected_trade_returns/23.0
    cumReturns_df = cumReturns_df.drop(columns=['date'])
    cumReturns_df = cumReturns_df/23.0
    print(len(cumReturns_df.keys()))
    cumReturns_df.plot(legend=False)
    plt.ylabel("Returns (%)")
    plt.xlabel("Hours")
    plt.show()

    plt.imshow(total_returns, cmap='RdBu')
    plt.colorbar(format = FuncFormatter(fmt))
    max_ret = np.amax(np.fabs(total_returns))
    plt.clim(vmin=-max_ret, vmax=max_ret)
    plt.yticks(np.arange(len(SMAs)), SMAs)
    plt.xticks(np.arange(len(Zscores)), Zscores)
    plt.title("Average Returns Bandwidth = {}".format(bandwidth))
    plt.xlabel("Z Score Period")
    plt.ylabel("SMA Period")
    plt.show()

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

    if plot_trade_distributions:
        plt.subplot(311)
        weights = np.ones_like(trade_rets1)/float(len(trade_rets1))
        plt.hist(trade_rets1, weights=weights, bins=100, label='400v14', range=[-15, 15])
        plt.legend()

        plt.subplot(312)
        weights = np.ones_like(trade_rets2)/float(len(trade_rets2))
        plt.hist(trade_rets2, weights=weights, bins=100, label='100v20', range=[-15,15])
        plt.ylabel("Probability")
        plt.legend()

        plt.subplot(313)
        weights = np.ones_like(trade_rets3)/float(len(trade_rets3))
        plt.hist(trade_rets3, weights=weights, bins=100, label='400v30', range=[-20,20])
        plt.xlabel("Trade Returns (%)")
        plt.legend()

        plt.show()


if __name__ == "__main__":
    main()

