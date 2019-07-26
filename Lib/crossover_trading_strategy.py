from matplotlib import pyplot as plt
import pandas as pd

from .abstract_MA_trading_strategy import movingAverageTrading


class crossoverTrading(movingAverageTrading):
    """
    A class that backtests a moving average based trading algorithm
    which attempts to capitalise on momentum and trends in the
    cryptocurrency market.

    Uses a longer (slower) moving average and a shorter (faster)
    moving average. Will enter a long if faster MA crosses upwards
    through slower MA and a short if it crosses downwards.

    Returns are stored under df['returns']. Refer to base class,
    movingAverageTrading for more details.

    Initialisation:
    - df:               (pandas DataFrame) containing asset price
                        history
    - asset_symbol:     (str) header of asset price history in df
    - fast_MA:          (int) period of shorter, faster MA
    - slow_MA:          (int) period of longer, slower MA
    - MA_type:          (str) 'SMA' or 'EMA' for simple MA or
                        exponential MA
    - trading_fee:      (double) fractional trading fee between 0 and 1

    Notes:
    - Currently designed to only open one positon at a time
    - Opening a long simultaneously closes any open shorts
    """

    def __init__(self, df, asset_symbol, MA_type,
                 slow_MA, fast_MA=1, trading_fee=0.0):
        args = (df, asset_symbol, MA_type, slow_MA)
        kwargs = {"fast_MA": fast_MA, "trading_fee": trading_fee}
        super(crossoverTrading, self).__init__(*args, **kwargs)

    def plotTrading(self, opentimes, closetimes):
        """
        Plots the executed trading.
        2x1 subplots:
        subplot 1:          Asset price series w/ fast and slow MAs
        subplot 2:          Cumulative returns of trading

        Notes:
        - plot has green and red verticle lines indicating
        opening longs and shorts respectively
        """

        t0 = self.MAs_period
        T = self.df.shape[0]
        plt.subplot(211)
        self.df.loc[t0:T, self.sym].plot(label=self.sym)
        self.df.loc[t0:T, self.MAs_str].plot(label=self.MAs_str)
        if self.MAf_period > 1:
            self.df.loc[t0:T, self.MAf_str].plot(label=self.MAf_str)
        [plt.axvline(x, c='g', lw=0.5, ls='--') for x in opentimes]
        [plt.axvline(x, c='r', lw=0.5, ls='--') for x in closetimes]
        plt.ylabel('{}/BTC'.format(self.sym))
        plt.legend()

        plt.subplot(212)
        self.df.loc[t0:T, 'returns'].cumsum().plot()
        plt.ylabel('Returns')
        plt.xlabel('Hours')
        plt.show()


    def trade(self, plot=False):
        """
        Executes all trades from the earliest value that the SMA can be
        determined.

        Inputs:
        - plot:             (bool) optional arg to plot trading results
        """

        longtimes = []
        shorttimes = []

        for t in range(self.MAs_period + 1, self.df.shape[0]):
            MAs_t, MAf_t = self.getMA(t)
            MAs_t_1, MAf_t_1 = self.getMA(t-1)

            if MAf_t > MAs_t and MAf_t_1 < MAs_t_1:
                spotprice = self.getSpotPrice(t)
                if self.position.getPosition() != 0:
                    self.position.close(spotprice, fee=self.trading_fee)
                    self.storeTradeReturns(t)                
                self.position.open(spotprice, 'L', fee=self.trading_fee)
                longtimes.append(t)

            if MAf_t < MAs_t and MAf_t_1 > MAs_t_1:
                spotprice = self.getSpotPrice(t)
                if self.position.getPosition() != 0:
                    self.position.close(spotprice, fee=self.trading_fee)
                    self.storeTradeReturns(t)                
                self.position.open(spotprice, 'S', fee=self.trading_fee)
                shorttimes.append(t)

        if plot:
            self.plotTrading(longtimes, shorttimes)
