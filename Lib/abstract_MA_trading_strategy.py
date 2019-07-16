from matplotlib import pyplot as plt
import pandas as pd
import abc


class movingAverageTrading(metaclass=abc.ABCMeta):
    """
    A base class for trading strategies that are based around moving
    average analysis. This class does not implement any trading.
    plotTrading and Trade methods are abstract.

    Strategies assume a fixed position size and stores returns from a
    round trip trade in df['returns'] for the corresponding time index
    as a decimal (i.e 0.3 == +30% or -0.2 == -20%)

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
    """

    def __init__(self, df, asset_symbol, MA_type,
                 slow_MA, fast_MA=1, trading_fee=0.0):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("df must be a pandas DataFrame")
        if not isinstance(asset_symbol, str):
            raise ValueError("asset symbol must be a string")
        if asset_symbol not in df.keys():
            raise ValueError("asset symbol not in dataframe headers")
        if slow_MA < fast_MA:
            raise ValueError("Slower MA must have the shorter period")
        if not isinstance(slow_MA, int) or slow_MA < 1:
            raise ValueError("slow_MA period must be a positive int")
        if not isinstance(fast_MA, int) or fast_MA < 1:
            raise ValueError("fast_MA period must be a positive int")
        if MA_type != "EMA" and MA_type != "SMA":
            raise ValueError("MA type not supported. Try 'SMA' or 'EMA")
        if trading_fee < 0 or trading_fee > 1:
            raise ValueError("Trading fee must be between 0 and 1.")

        self.df = df
        self.sym = asset_symbol
        self.MAf_period = fast_MA
        self.MAs_period = slow_MA
        self.MA_type = MA_type
        self.trading_fee = trading_fee

        # initialise with no position or entries
        self._entry_price = 0
        self._pos = 0
        self.df['returns'] = 0.0

        # Generate moving averages upon initialisation
        if self.MA_type == 'EMA':
            self.MAf_str = '{}EMA'.format(self.MAf_period)  # str for df keys
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
            self.df[self.MAs_str] = (self.df[self.sym]
                                     .rolling(window=self.MAs_period)
                                     .mean())
            if self.MAf_period > 1:
                self.df[self.MAf_str] = (self.df[self.sym]
                                         .rolling(window=self.MAf_period)
                                         .mean())
        elif self.MA_type == 'EMA':
            self.df[self.MAs_str] = (self.df[self.sym]
                                     .ewm(span=self.MAs_period)
                                     .mean())
            if self.MAf_period > 1:
                self.df[self.MAf_str] = (self.df[self.sym]
                                         .ewm(span=self.MAf_period)
                                         .mean())

    def getSpotPrice(self, t):
        """
        Gets the spot price at index t in self.df
        """
        return self.df.loc[t, self.sym]

    def getMA(self, t):
        """
        Gets the value of fast and slow MAs at index t in self.df
        """
        if self.MAf_period == 1:
            return self.df.loc[t, self.MAs_str], self.getSpotPrice(t)
        else:
            return self.df.loc[t, self.MAs_str], self.df.loc[t, self.MAf_str]

    def _setTradeReturns(self, t, returns):
        """
        Private function used by self.closePosition() that stores a
        given return at index t in self.df
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

    @abc.abstractmethod
    def plotTrading(self, opentimes, closetimes):
        """
        This method should plot the complete trading activities

        Inputs:
        - opentimes:        (list) indices of when a position was opened
        - closetimes:       (list) indices of when a position was closed
        """

    @abc.abstractmethod
    def trade(self, plot=False):
        """
        This method should executes all trades from the earliest value
        that the SMA can be determined.

        Inputs:
        - plot:             (bool) optional arg to plot trading results
        """
