from matplotlib import pyplot as plt
import pandas as pd

from .trading_strat_abstract_MA import movingAverageTrader


class crossoverTrader(movingAverageTrader):
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
        super(crossoverTrader, self).__init__(*args, **kwargs)

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

        t0 = self.slowMA.getPeriod()
        T = self.df.shape[0]
        plt.subplot(211)
        self.df.loc[t0:T, self.sym].plot(label=self.sym)
        self.slowMA.getArray().loc[t0:T].plot(label=self.slowMA.name)
        if self.fastMA.getPeriod() > 1:
            self.fastMA.getArray().loc[t0:T].plot(label=self.fastMA.name)
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

        for t in range(self.slowMA.getPeriod() + 1, self.df.shape[0]):
            slowMA_t = self.slowMA.getValue(t)
            fastMA_t = self.fastMA.getValue(t)
            slowMA_t_1 = self.slowMA.getValue(t-1)
            fastMA_t_1 = self.fastMA.getValue(t-1)

            if fastMA_t > slowMA_t and fastMA_t_1 < slowMA_t_1:
                spotprice = self.getSpotPrice(t)
                if self.position.getPosition() != 0:
                    self.position.close(spotprice, fee=self.trading_fee)
                    self.storeTradeReturns(t)                
                self.position.open(spotprice, 'L', fee=self.trading_fee)
                longtimes.append(t)

            if fastMA_t < slowMA_t and fastMA_t_1 > slowMA_t_1:
                spotprice = self.getSpotPrice(t)
                if self.position.getPosition() != 0:
                    self.position.close(spotprice, fee=self.trading_fee)
                    self.storeTradeReturns(t)                
                self.position.open(spotprice, 'S', fee=self.trading_fee)
                shorttimes.append(t)

        if plot:
            self.plotTrading(longtimes, shorttimes)
