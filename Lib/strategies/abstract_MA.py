from matplotlib import pyplot as plt
import pandas as pd
import abc

from ..types.position import Position
from ..types.simple_moving_average import simpleMovingAverage
from ..types.exponential_moving_average import expMovingAverage


class movingAverageTrader(metaclass=abc.ABCMeta):
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
        if MA_type != "EMA" and MA_type != "SMA":
            raise ValueError("MA type not supported. Try 'SMA' or 'EMA")
        if trading_fee < 0 or trading_fee > 1:
            raise ValueError("Trading fee must be between 0 and 1.")

        self.df = df
        self.sym = asset_symbol
        self.trading_fee = trading_fee
        self.position = Position()
        self.df['returns'] = 0.0
        if MA_type == 'SMA':
            self.fastMA = simpleMovingAverage(df[self.sym], fast_MA)
            self.slowMA = simpleMovingAverage(df[self.sym], slow_MA)
        elif MA_type == 'EMA':
            self.fastMA = expMovingAverage(df[self.sym], fast_MA)
            self.slowMA = expMovingAverage(df[self.sym], slow_MA)

    def getSpotPrice(self, t):
        """
        Gets the spot price at index t in self.df
        """
        return self.df.loc[t, self.sym]

    def storeTradeReturns(self, t):
        """
        Stores trade returns in dataframe
        """

        self.df.loc[t, 'returns'] = self.position.tradereturn

    def openPosition(self, t, pos_type):
        """
        Opens a position at time t
        """
        spotprice = self.getSpotPrice(t)
        if pos_type == 'L':
            self.position.open(spotprice, 'L', fee=self.trading_fee)
        elif pos_type == 'S':
            self.position.open(spotprice, 'S', fee=self.trading_fee)
        else:
            raise ValueError("Position type not recognised")

    def closePosition(self, t):
        """
        Closes a position at time t
        """
        spotprice = self.getSpotPrice(t)
        self.position.close(spotprice, fee=self.trading_fee)
        self.storeTradeReturns(t)

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
