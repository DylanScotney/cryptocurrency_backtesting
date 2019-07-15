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
    return '{}%'.format(np.round(x*100, 2))

def main():

    bandwidth = 1.0
    plot_trade_distributions = False

    # Load data
    df = pd.read_csv(cpath+"\\..\\Data\\ZScore_Results\\dualZscores_bw{}.csv".format(bandwidth))
    df = df.drop(columns=['Unnamed: 0', 'date'])
    # Define params
    #--------------------------------------------------------------------------
    
    bandwidths = [1.0, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0]
    MAs = [80,100] #[20, 30, 40, 50, 80, 100, 160, 200, 400]
    num_faster_MAs = 10 # number of faster MAs for each MA
    ZScore_MAs = [5, 6, 7, 8, 10, 12, 14, 15, 20, 30, 50, 80, 100]
    returns = np.zeros((len(MAs)*num_faster_MAs, len(ZScore_MAs))) # store final returns
    
    #--------------------------------------------------------------------------
    for bandwidth in bandwidths:
        df = pd.read_csv(cpath+"\\..\\Data\\ZScore_Results\\extra_bw{}.csv".format(bandwidth))
        df = df.drop(columns=['Unnamed: 0', 'date'])
        ylabels = []
        
        returns = np.zeros((len(MAs)*num_faster_MAs, len(ZScore_MAs))) # store final returns
        expected_trade_returns = np.zeros((len(MAs)*num_faster_MAs, len(ZScore_MAs)))

        count = 0
        count2 = 0
        for item in df.keys():
            if count == 5980:
                break
            for i in range(len(MAs)):
                # Define SMA periods for trends
                MA = MAs[i]
                faster_MAs = np.linspace(1, MA, num=num_faster_MAs, endpoint=False)
                faster_MAs = [int(item) for item in faster_MAs]
                for k in range(num_faster_MAs):
                    MAfast = faster_MAs[k]
                    if count2 == 0:
                        ylabels.append('{}v{}'.format(MA,MAfast))
                    for j in range(len(ZScore_MAs)):
                        Z_MA = ZScore_MAs[j]   
                        key = df.keys()[count]
                        print(count, key)
                        loc = num_faster_MAs*i + k, j # plot location
                        returns[loc] += df[key].cumsum().iloc[-1]

                        temp_exp_rets = []
                        for ret in df[key]:
                            if ret != 0:
                                temp_exp_rets.append(ret*100)
                                
                        expected_trade_returns[loc] += np.mean(temp_exp_rets)
                        count+=1
            count2+=1

        returns = returns/23.0
        expected_trade_returns = expected_trade_returns/23.0

        plt.imshow(returns, cmap='RdBu')
        plt.colorbar(format=FuncFormatter(fmt))
        max_ret = max(returns.min(), returns.max(), key=abs)
        plt.clim(vmin=-max_ret, vmax=max_ret)
        plt.yticks(np.arange(len(ylabels)), ylabels)
        plt.xticks(np.arange(len(ZScore_MAs)), ZScore_MAs)
        plt.ylabel("SMA Period")
        plt.xlabel("Z Score Period")
        plt.title("Dual SMAs Bandwidth = {}".format(bandwidth))
        plt.show()

        plt.imshow(expected_trade_returns, cmap='RdBu')
        plt.colorbar(format=FuncFormatter(fmt))
        max_ret = np.nanmax(abs(expected_trade_returns))
        print(expected_trade_returns)
        print(max_ret)
        plt.clim(vmin=-max_ret, vmax=max_ret)
        plt.yticks(np.arange(len(ylabels)), ylabels)
        plt.xticks(np.arange(len(ZScore_MAs)), ZScore_MAs)
        plt.ylabel("SMA Period")
        plt.xlabel("Z Score Period")
        plt.title("Dual SMAs Average Trade Return Bandwidth = {}".format(bandwidth))
        plt.show()

if __name__ == "__main__":
    main()

