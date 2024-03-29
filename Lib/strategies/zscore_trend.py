from matplotlib import pyplot as plt
import pandas as pd

from .abstract_MA import movingAverageTrader
from ..types.zscore import zScore


class zScoreTrader(movingAverageTrader):
    """
    A class that backtests a z score and MA based trading algorithm
    which attempts to capitalise on the over compensation of moves in
    the cryptocurrency market.

    Returns are stored under df['returns']. Refer to base class,
    movingAverageTrading for more details.

    Uses a (typically longer) moving average to determine the overall
    trend. Only longs (shorts) trades will be executed if asset is in
    uptrend (downtrend).
    A second (typically shorter) lookback period is used to determine
    the zscore of the asset and execute trading logic.

    Initialisation:
    - df:               pandas dataframe containing asset price history
    - asset_symbol:     header of asset price history in df
    - slow_MA:          period of a moving average that is used to
                        to determine the trend
    - zscore_period:    lookback period for calculating z score
    - bandwidth:        bandwidth of zscore values on which trading
                        logic is executed.
    - fast_MA:          A MA period shorter than slow_MA that will
                        determine trend. If not specified period=0
                        (i.e. spotprice is used)

    Members:
    - self.df:          df (see initialisation)
    - self.sym:         asset_symbol (see initialisation)
    - self.trading_fee: tradine_fee (see initialisation)
    - self.position:    (Position) Custom position object to handle
                        trade positions.
    - self.fastMA:      (moving average) custom moving average type
                        object that handles moving average of series.
    - self.slowMA:      moving average with longer period than
                        self.fastMA.
    - self.zscore:      (zScore) custom zScore object that handles
                        z score of corresponding series.
    - self.bandwidth:   (float) bandwidth for trading logic
    - self.opentimes:   (list, int) holds indeces of trade opening times
    - self.closetimes:  (list, int) holds indeces of trade closing times

    Notes:
    - Currently designed to only open one positon at a time
    """

    def __init__(self, df, asset_symbol, MA_type, slow_MA, zscore_period,
                 bandwidth, fast_MA=1, trading_fee=0.0):
        if not isinstance(zscore_period, int) or zscore_period <= 0:
            raise ValueError("Z score period must be positive integer")

        args = (df, asset_symbol, MA_type, slow_MA)
        kwargs = {"fast_MA": fast_MA, "trading_fee": trading_fee}
        super(zScoreTrader, self).__init__(*args, **kwargs)

        self.zscore = zScore(df[self.sym], zscore_period)
        self.bandwith = bandwidth
        self.opentimes = []
        self.closetimes = []

    def trade(self, plot=False):
        """
        Executes all trades from the earliest value that the SMA can be
        determined.

        Inputs:
        - plot:             (bool) optional arg to plot trading results
        """

        self.opentimes = []
        self.closetimes = []

        for t in range(self.slowMA.period, self.df.shape[0]):
            slowMA_t = self.slowMA.getValue(t)
            fastMA_t = self.fastMA.getValue(t)
            Z_t = self.zscore.getValue(t)
            Z_t_1 = self.zscore.getValue(t-1)

            if fastMA_t > slowMA_t:
                uptrend = True
            else:
                uptrend = False

            # Open position logic
            # -----------------------------------------------------------------
            if uptrend and self.position.position == 0:
                if Z_t > -self.bandwith and Z_t_1 < -self.bandwith:
                    self.openPosition(t, 'L')
                    self.opentimes.append(t)

            if not uptrend and self.position.position == 0:
                if Z_t < self.bandwith and Z_t_1 > self.bandwith:
                    self.openPosition(t, 'S')
                    self.opentimes.append(t)
            # -----------------------------------------------------------------

            # Close position logic
            # -----------------------------------------------------------------
            if self.position.position == 1 and Z_t > 0 and Z_t_1 < 0:
                self.closePosition(t)
                self.closetimes.append(t)

            if self.position.position == -1 and Z_t < 0 and Z_t_1 > 0:
                self.closePosition(t)
                self.closetimes.append(t)
            # -----------------------------------------------------------------

        if plot:
            self.plotTrading()

        return self.df['returns'].cumsum().iloc[-1]

    def plotTrading(self):
        """
        Plots the executed trading.
        3x1 subplots:
        subplot 1:          asset price w/ longer MA to dictate trend
                            and shorter MA to determine moves via zscore
        subplot 2:          Z score with specified bandwidths
        subplot 3:          Cumulative returns

        Notes:
        - All three plots have green and red verticle lines indicating
        opening and closing positions
        - Will only open longs in uptrend (spotprice > longer MA)
        and only enter shorts in downtrend (spotprice < longer MA)
        """

        bw = self.bandwith
        t0 = self.slowMA.period
        T = self.df.shape[0]
        zscore_MA = (self.df[self.sym]
                     .rolling(window=self.zscore.period)
                     .mean())

        plt.subplot(311)
        self.df.loc[t0:T, self.sym].plot(label=self.sym)
        self.slowMA.values.loc[t0:T].plot(label=self.slowMA.name)
        zscore_MA.loc[t0:T].plot(label=self.zscore.name)
        if self.fastMA.period > 1:
            self.fastMA.values.loc[t0:T].plot(label=self.fastMA.name)
        plt.ylabel('{}/BTC'.format(self.sym))
        [plt.axvline(x, c='g', lw=0.5, ls='--') for x in self.opentimes]
        [plt.axvline(x, c='r', lw=0.5, ls='--') for x in self.closetimes]
        plt.legend()

        plt.subplot(312)
        self.zscore.values.loc[t0:T].plot()
        plt.plot([t0, T], [bw, bw], c='k', ls='--', lw=0.5)
        plt.plot([t0, T], [-bw, -bw], c='k', ls='--', lw=0.5)
        plt.plot([t0, T], [0, 0], c='k', ls='--', lw=0.5)
        [plt.axvline(x, c='g', lw=0.5, ls='--') for x in self.opentimes]
        [plt.axvline(x, c='r', lw=0.5, ls='--') for x in self.closetimes]
        plt.ylabel('Z Score')

        plt.subplot(313)
        returns = self.df.loc[t0:T, 'returns'].cumsum()*100
        returns.plot()
        plt.ylabel('Returns (%)')
        plt.xlabel('Hours')
        plt.show()
