from matplotlib import pyplot as plt
import pandas as pd


class zscoreTrader():
    """
    A class that backtests a z score based trading algorithm which
    attempts to capitalise on the over compensation of moves in the 
    cryptocurrency market.

    Uses a (typically longer) moving average to determine the overall 
    trend. Only longs (shorts) trades will be executed if asset is in 
    uptrend (downtrend).
    A second (typically shorter) lookback period is used to determine
    the zscore of the asset and execute trading logic

    Initialisation:
    - df:               pandas dataframe containing asset price history
    - asset_symbol:     header of asset price history in df
    - slow_MA_period:   period of a moving average that is used to
                        to determine the trend
    - zscore_period:    lookback period for calculating z score
    - bandwidth:        bandwidth of zscore values on which trading
                        logic is executed. 
    - fast_MA_period:   A MA period shorter than slow_MA_period that will
                        determine trend. If not specified period=0 
                        (i.e. spotprice is used)

    Notes:
    Currently designed to only open one positon at a time
    """


    def __init__(self, df, asset_symbol, slow_MA_period, zscore_period, bandwidth, fast_MA_period=1, trading_fee=0.0):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("df must be a pandas DataFrame")
        if not isinstance(asset_symbol, str):
            raise ValueError("asset symbol must be a string")
        if asset_symbol not in df.keys():
            raise ValueError("asset symbol not in dataframe headers")
        if fast_MA_period >= slow_MA_period:
            raise ValueError("fast MA period must be shorter than slow period")
        if not isinstance(slow_MA_period, int) or slow_MA_period < 2:
            raise ValueError("slow_MA_period period must be an int > 2")
        if not isinstance(fast_MA_period, int) or fast_MA_period < 1:
            raise ValueError("fast_MA period must be a positive int")        
        if trading_fee < 0 or trading_fee > 1:
            raise ValueError("Trading fee must be between 0 and 1.")

        self.df = df
        self.sym = asset_symbol
        self.MA_period = slow_MA_period 
        self.fast_MA_period = fast_MA_period
        self.zscore_period = zscore_period 
        self.bandwith = bandwidth
        self.trading_fee = trading_fee 

        # Strings for dataframe headers
        self.MAs_str = '{}SMA'.format(slow_MA_period) # Slow MA
        self.MAf_str = '{}SMA'.format(fast_MA_period)  # Fast MA
        self.Z_str = '{}Z'.format(zscore_period)
        
        # no position or returns when initialised
        self._entry_price = 0  
        self._pos = 0
        self.df['returns'] = 0.0

        # Generate data when initialised
        self.generateMAs()
        self.generateZscore()


    def generateMAs(self):
        """
        Generates fast and slow SMAs over all time and stores it in 
        dataframe.
        Will only generate fast MA if specified since otherwise
        spotprice is used.

        Note: this function is called on initialisation.
        """
        self.df[self.MAs_str] = self.df[self.sym].rolling(window=self.MA_period).mean()

        if self.fast_MA_period > 1:
            self.df[self.MAf_str] = self.df[self.sym].rolling(window=self.fast_MA_period).mean()
    

    def generateZscore(self):
        """
        Generates the Z score of the asset and stores in the dataframe
        Note: this function is called on initialisation.
        """
        mean = self.df[self.sym].rolling(window=self.zscore_period).mean()
        std = self.df[self.sym].rolling(window=self.zscore_period).std()
        self.df[self.Z_str] = (self.df[self.sym] - mean)/std


    def getSpotPrice(self, t):
        """
        Gets the spot price at index t in self.df
        """
        return self.df.loc[t, self.sym]
    

    def getMA(self, t):
        """
        Gets the values of the fast and slow SMAs at index t in self.df
        """
        if self.fast_MA_period == 1:
            return self.df.loc[t, self.MAs_str], self.getSpotPrice(t)
        else:
            return self.df.loc[t, self.MAs_str], self.df.loc[t, self.MAf_str] 


    def getZScore(self, t):
        """
        Gets the value of the Z score at index t in self.df
        """
        return self.df.loc[t, self.Z_str]

    
    def _setTradeReturns(self, t, returns):
        """
        Private function used by self.closePosition() that stores a given return
        at index t in self.df
        """

        self._pos *= (1 - self.trading_fee)
        self.df.loc[t, 'returns'] += returns*self._pos


    def openPosition(self, t, pos_type):
        """
        Executes the logic behind opening a position.
        """        
        self._entry_price = self.getSpotPrice(t) 
        if pos_type == 'L':
            self._pos = 1*(1 - self.trading_fee)
        elif pos_type == 'S':
            self._pos = -1*(1 - self.trading_fee)


    
    def closePosition(self, t):
        """
        Executes the logic behind closing a position and stores the
        returns in the df['returns']
        """
        exit_price = self.getSpotPrice(t)
        tradeReturn = (exit_price - self._entry_price)/abs(self._entry_price)
        self._setTradeReturns(t, tradeReturn)
        self._pos = 0 

    
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
        t0 = self.MA_period
        T = self.df.shape[0]
        zscore_MA = self.df[self.sym].rolling(window=self.zscore_period).mean()

        plt.subplot(311)
        self.df.loc[t0:T, self.sym].plot(label=self.sym)
        self.df.loc[t0:T,self.MAs_str].plot(label='slow SMA')        
        if self.fast_MA_period > 0:
            self.df.loc[t0:T,self.MAf_str].plot(label='fast SMA')
        zscore_MA[t0:T].plot(label='Z score SMA')
        plt.ylabel('{}/BTC'.format(self.sym))
        [plt.axvline(x, c='g', lw=0.5, ls='--') for x in opentimes]
        [plt.axvline(x, c='r', lw=0.5, ls='--') for x in closetimes] 
        plt.legend()

        plt.subplot(312)
        self.df.loc[t0:T, self.Z_str].plot()
        plt.plot([t0,T], [bw,bw], c='k', ls='--', lw=0.5)
        plt.plot([t0,T], [-bw,-bw], c='k', ls='--', lw=0.5)
        plt.plot([t0,T], [0,0], c='k', ls='--', lw=0.5)            
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

        for t in range(self.MA_period, self.df.shape[0]):
            slowMA_t, fastMA_t = self.getMA(t)
            Z_t = self.getZScore(t)
            Z_t_1 = self.getZScore(t-1)

            if fastMA_t > slowMA_t:
                uptrend = True
            else:
                uptrend = False
            
            # Open position logic
            #------------------------------------------------------------------
            if uptrend and self._pos == 0:
                if Z_t > -self.bandwith and Z_t_1 < -self.bandwith:
                    self.openPosition(t, 'L')
                    if plot:
                        opentimes.append(t)
            
            if not uptrend and self._pos == 0:
                if Z_t < self.bandwith and Z_t_1 > self.bandwith:
                    self.openPosition(t, 'S')
                    if plot:
                        opentimes.append(t)
            #------------------------------------------------------------------

            # Close position logic
            #------------------------------------------------------------------
            if self._pos == 1 and Z_t > 0 and Z_t_1 < 0:
                self.closePosition(t)
                if plot:
                    closetimes.append(t)
        
            if self._pos == -1 and Z_t < 0 and Z_t_1 > 0:
                self.closePosition(t)
                if plot:
                    closetimes.append(t)
            #------------------------------------------------------------------

        if plot:
            self.plotTrading(opentimes, closetimes)            
