from matplotlib import pyplot as plt
import pandas as pd


class movingAverageTrader():
    """
    A class that backtests a moving average based trading algorithm 
    which attempts to capitalise on momentum and trends in the 
    cryptocurrency market.

    Uses a longer (slower) moving average and a shorter (faster)
    moving average. Will enter a long if faster MA crosses upwards 
    through slower MA and a short if it crosses downwards.

    Initialisation:
    - df:               (pandas DataFrame) containing asset price
                        history
    - asset_symbol:     (str) header of asset price history in df
    - fast_MA:          (int) period of shorter, faster MA
    - slow_MA:          (int) period of longer, slower MA
    - MA_type:          (str) 'SMA' or 'EMA' for simple MA or 
                        exponential MA

    Notes:
    - Currently designed to only open one positon at a time
    - Opening a long simultaneously closes any open shorts
    """


    def __init__(self, df, asset_symbol, fast_MA, slow_MA, MA_type):

        if not isinstance(df, pd.DataFrame):
            raise ValueError("df must be a pandas DataFrame")
        if not isinstance(asset_symbol, str):
            raise ValueError("asset symbol must be a string")
        if asset_symbol not in df.keys():
            raise ValueError("asset symbol not in dataframe headers")
        if slow_MA < fast_MA:
            raise ValueError("Slower moving average must have the shorter period")
        if not isinstance(slow_MA, int):
            raise ValueError("slow_MA period must be an integer")
        if not isinstance(fast_MA, int):
            raise ValueError("fast_MA period must be integer")
        if MA_type != "EMA" and MA_type != "SMA":
            raise ValueError("MA type not supported. Try 'SMA' or 'EMA")

        self.df = df        
        self.sym = asset_symbol
        self.MAf_period = fast_MA
        self.MAs_period = slow_MA
        self.MA_type = MA_type

        # initialise with no position or entries
        self._entry_price = 0 
        self._pos = 0
        self.df['returns'] = 0.0

        # Generate moving averages upon initialisation
        if self.MA_type == 'EMA':
            self.MAf_str = '{}EMA'.format(self.MAf_period) # str for df headers
            self.MAs_str = '{}EMA'.format(self.MAs_period)
            self.generateMAs()
        elif self.MA_type == 'SMA':            
            self.MAf_str = '{}SMA'.format(self.MAf_period)
            self.MAs_str = '{}SMA'.format(self.MAs_period)
            self.generateMAs()


    def generateMAs(self):
        """
        Generates the faster and slower moving averages and stores them
        in self.df
        """  

        if self.MA_type == 'SMA':
            self.df[self.MAf_str] = self.df[self.sym].rolling(window=self.MAf_period).mean()      
            self.df[self.MAs_str] = self.df[self.sym].rolling(window=self.MAs_period).mean()         
        elif self.MA_type == 'EMA':
            self.df[self.MAf_str] = self.df[self.sym].ewm(span=self.MAf_period).mean()
            self.df[self.MAs_str] = self.df[self.sym].ewm(span=self.MAs_period).mean()


    def getSpotPrice(self, t):
        """
        Gets the spot price at index t in self.df
        """
        return self.df.loc[t, self.sym]

        
    def getMA(self, t):
        """
        Gets the value of MAs at index t in self.df
        """
        return self.df.loc[t, self.MAs_str], self.df.loc[t, self.MAf_str]

    
    def _setTradeReturns(self, t, returns):
        """
        Private function used by self.closePosition() that stores a
        given return at index t in self.df
        """

        self.df.loc[t, 'returns'] += returns*self._pos

    
    def openPosition(self, t, pos_type):
        """
        Executes the logic behind opening a position.
        """   

        self._entry_price = self.getSpotPrice(t) 
        if pos_type == 'L':
            self._pos = 1 
        elif pos_type == 'S':
            self._pos = -1 

    
    def closePosition(self, t):
        """
        Executes the logic behind closing a position and stores the
        returns in the df['returns']
        """

        exit_price = self.getSpotPrice(t)
        tradeReturn = (exit_price - self._entry_price)/abs(self._entry_price)
        self._setTradeReturns(t, tradeReturn)
        self._pos = 0 

    
    def plotTrading(self, longtimes, shorttimes):
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
        self.df.loc[t0:T, self.MAf_str].plot(label=self.MAf_str)
        self.df.loc[t0:T, self.MAs_str].plot(label=self.MAs_str)
        [plt.axvline(x, c='g', lw=0.5, ls='--') for x in longtimes]
        [plt.axvline(x, c='r', lw=0.5, ls='--') for x in shorttimes] 
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
                self.closePosition(t)
                self.openPosition(t, 'L')
                longtimes.append(t)


            if MAf_t < MAs_t and MAf_t_1 > MAs_t_1:
                self.closePosition(t)
                self.openPosition(t, 'S')
                shorttimes.append(t)

        if plot:
            self.plotTrading(longtimes, shorttimes)



             

    

    


