from matplotlib import pyplot as plt
import pandas as pd

from .abstract_MA import movingAverageTrader


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

    Members:
    - self.df:          df (see initialisation)
    - self.sym:         asset_symbol (see initialisation)
    - self.trading_fee: tradine_fee (see initialisation)
    - self.position:    (Position) Custom position object to handle
                        trade positions
    - self.fastMA:      (moving average) custom moving average type
                        object that handles moving average of series
    - self.slowMA:      moving average with longer period than
                        self.fastMA

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

        t0 = self.slowMA.period
        T = self.df.shape[0]
        plt.subplot(211)
        self.df.loc[t0:T, self.sym].plot(label=self.sym)
        self.slowMA.values.loc[t0:T].plot(label=self.slowMA.name)
        if self.fastMA.period > 1:
            self.fastMA.values.loc[t0:T].plot(label=self.fastMA.name)
        [plt.axvline(x, c='g', lw=0.5, ls='--') for x in opentimes]
        [plt.axvline(x, c='r', lw=0.5, ls='--') for x in closetimes]
        plt.ylabel('{}/BTC'.format(self.sym))
        plt.legend()

        plt.subplot(212)
        returns = self.df.loc[t0:T, 'returns'].cumsum()*100
        returns.plot()
        plt.ylabel('Returns (%)')
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

        for t in range(self.slowMA.period + 1, self.df.shape[0]):
            slowMA_t = self.slowMA.getValue(t)
            fastMA_t = self.fastMA.getValue(t)
            slowMA_t_1 = self.slowMA.getValue(t-1)
            fastMA_t_1 = self.fastMA.getValue(t-1)

            if fastMA_t > slowMA_t and fastMA_t_1 < slowMA_t_1:
                if self.position.position != 0:
                    self.closePosition(t)
                self.openPosition(t, 'L')
                longtimes.append(t)

            if fastMA_t < slowMA_t and fastMA_t_1 > slowMA_t_1:
                if self.position.position != 0:
                    self.closePosition(t)
                self.openPosition(t, 'S')
                shorttimes.append(t)

        if plot:
            self.plotTrading(longtimes, shorttimes)

        return self.df['returns'].cumsum().iloc[-1]
