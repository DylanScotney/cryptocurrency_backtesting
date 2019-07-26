from matplotlib import pyplot as plt
import pandas as pd

from .trading_strat_abstract_MA import movingAverageTrader


class zScoreTrader(movingAverageTrader):
    """
    A class that backtests a z score based trading algorithm which
    attempts to capitalise on the over compensation of moves in the
    cryptocurrency market.

    Returns are stored under df['returns']. Refer to base class,
    movingAverageTrading for more details.

    Uses a (typically longer) moving average to determine the overall
    trend. Only longs (shorts) trades will be executed if asset is in
    uptrend (downtrend).
    A second (typically shorter) lookback period is used to determine
    the zscore of the asset and execute trading logic

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

        self.zscore_period = zscore_period
        self.bandwith = bandwidth

        self.Z_str = '{}Z'.format(zscore_period)
        self.generateZscore()

    def generateZscore(self):
        """
        Generates the Z score of the asset and stores in the dataframe
        Note: this function is called on initialisation.
        """

        mean = self.df[self.sym].rolling(window=self.zscore_period).mean()
        std = self.df[self.sym].rolling(window=self.zscore_period).std()
        self.df[self.Z_str] = (self.df[self.sym] - mean)/std

    def getZScore(self, t):
        """
        Gets the value of the Z score at index t in self.df
        """

        return self.df.loc[t, self.Z_str]

    def plotTrading(self, opentimes, closetimes):
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
        t0 = self.slowMA.getPeriod()
        T = self.df.shape[0]
        zscore_MA = self.df[self.sym].rolling(window=self.zscore_period).mean()

        plt.subplot(311)
        self.df.loc[t0:T, self.sym].plot(label=self.sym)
        self.slowMA.getArray().loc[t0:T].plot(label=self.slowMA.name)
        if self.fastMA.getPeriod() > 1:
            self.fastMA.getArray().loc[t0:T].plot(label=self.fastMA.name)
        zscore_MA[t0:T].plot(label='Z score SMA')
        plt.ylabel('{}/BTC'.format(self.sym))
        [plt.axvline(x, c='g', lw=0.5, ls='--') for x in opentimes]
        [plt.axvline(x, c='r', lw=0.5, ls='--') for x in closetimes]
        plt.legend()

        plt.subplot(312)
        self.df.loc[t0:T, self.Z_str].plot()
        plt.plot([t0, T], [bw, bw], c='k', ls='--', lw=0.5)
        plt.plot([t0, T], [-bw, -bw], c='k', ls='--', lw=0.5)
        plt.plot([t0, T], [0, 0], c='k', ls='--', lw=0.5)
        [plt.axvline(x, c='g', lw=0.5, ls='--') for x in opentimes]
        [plt.axvline(x, c='r', lw=0.5, ls='--') for x in closetimes]
        plt.ylabel('Z Score')

        plt.subplot(313)
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

        opentimes = []
        closetimes = []

        for t in range(self.slowMA.getPeriod(), self.df.shape[0]):
            slowMA_t = self.slowMA.getValue(t)
            fastMA_t = self.fastMA.getValue(t)
            Z_t = self.getZScore(t)
            Z_t_1 = self.getZScore(t-1)

            if fastMA_t > slowMA_t:
                uptrend = True
            else:
                uptrend = False

            # Open position logic
            # -----------------------------------------------------------------
            if uptrend and self.position.getPosition() == 0:
                if Z_t > -self.bandwith and Z_t_1 < -self.bandwith:
                    spotprice = self.getSpotPrice(t)
                    self.position.open(spotprice, 'L', fee=self.trading_fee)
                    if plot:
                        opentimes.append(t)

            if not uptrend and self.position.getPosition() == 0:
                if Z_t < self.bandwith and Z_t_1 > self.bandwith:
                    spotprice = self.getSpotPrice(t)
                    self.position.open(spotprice, 'S', fee=self.trading_fee)
                    if plot:
                        opentimes.append(t)
            # -----------------------------------------------------------------

            # Close position logic
            # -----------------------------------------------------------------
            if self.position.getPosition() == 1 and Z_t > 0 and Z_t_1 < 0:
                spotprice = self.getSpotPrice(t)
                self.position.close(spotprice, fee=self.trading_fee)
                self.storeTradeReturns(t)
                if plot:
                    closetimes.append(t)

            if self.position.getPosition() == -1 and Z_t < 0 and Z_t_1 > 0:
                spotprice = self.getSpotPrice(t)
                self.position.close(spotprice, fee=self.trading_fee)
                if plot:
                    closetimes.append(t)
            # -----------------------------------------------------------------

        if plot:
            self.plotTrading(opentimes, closetimes)
