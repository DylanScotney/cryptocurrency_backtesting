from pytest import raises, approx
from datetime import datetime
import os.path
import json
import pandas as pd
import numpy as np

from ..Lib.MA_trend_trader import movingAverageTrader


def test_initialisation():
    """
    Tests basic initialisation. Note this also tests the generateMA()
    function called in the constructor
    """

    df = pd.DataFrame({'a':[5,2,5,2]})
    expected_df = df[['a']]        
    expected_df['returns'] = 0.0
    expected_df['2SMA'] = [np.nan, 3.5, 3.5, 3.5]
    expected_df['3SMA'] = [np.nan, np.nan, 4, 3]
    sym = 'a'
    fastMA = 2
    slowMA = 3
    MA_type = 'SMA'

    trader = movingAverageTrader(df, sym, fastMA, slowMA, MA_type)

    assert(trader.df.equals(expected_df))
    assert(trader.sym == sym)
    assert(trader.MAf_period == fastMA)
    assert(trader.MAs_period == slowMA)
    assert(trader.MA_type == MA_type)


def test_initialisation_failure1():
    """
    Tests error is raised if df is incorrrect type
    """

    df = "i'm not a dataframe"
    sym = 'a'
    fastMA = 5
    slowMA = 30
    MA_type = 'SMA'
    
    with raises(ValueError):
        movingAverageTrader(df, sym, fastMA, slowMA, MA_type)


def test_initialisation_failure2():
    """
    Tests error is raised if symbol is incorrrect type
    """

    df = pd.DataFrame({'a':[5,4,7,4]})
    sym = 5
    fastMA = 5
    slowMA = 30
    MA_type = 'SMA'
    
    with raises(ValueError):
        movingAverageTrader(df, sym, fastMA, slowMA, MA_type)


def test_initialisation_failure3():
    """
    Tests error is raised if symbol not in df
    """

    df = pd.DataFrame({'a':[5,4,7,4]})
    sym = 'b'
    fastMA = 5
    slowMA = 30
    MA_type = 'SMA'
    
    with raises(ValueError):
        movingAverageTrader(df, sym, fastMA, slowMA, MA_type)


def test_initialisation_failure4():
    """
    Tests error is raised if fastMA period > slowMA period
    """

    df = pd.DataFrame({'a':[5,4,7,4]})
    sym = 'a'
    fastMA = 40
    slowMA = 30
    MA_type = 'SMA'
    
    with raises(ValueError):
        movingAverageTrader(df, sym, fastMA, slowMA, MA_type)


def test_initialisation_failure5():
    """
    Tests types for slow, fast MAs
    """

    df = pd.DataFrame({'a':[5,4,7,4]})
    sym = 'b'
    fastMA = 20
    slowMA = 30.1
    MA_type = 'SMA'
    
    with raises(ValueError):
        movingAverageTrader(df, sym, fastMA, slowMA, MA_type)
    
    slowMA = 30
    fastMA = 20.1
    with raises(ValueError):
        movingAverageTrader(df, sym, fastMA, slowMA, MA_type)

    
def test_initialisation_failure6():
    """
    Tests error is raised if fastMA period > slowMA period
    """

    df = pd.DataFrame({'a':[5,4,7,4]})
    sym = 'a'
    fastMA = 20
    slowMA = 30
    MA_type = 'non compatible ma type'
    
    with raises(ValueError):
        movingAverageTrader(df, sym, fastMA, slowMA, MA_type)


def test_getSpotPrice():
    """
    Tests getspotprice
    """

    df = pd.DataFrame({'a':[5,2,5,2]})
    sym = 'a'
    fastMA = 2
    slowMA = 3
    MA_type = 'SMA'

    trader = movingAverageTrader(df, sym, fastMA, slowMA, MA_type)
    
    assert (trader.getSpotPrice(0) == 5)


def test_getMA():
    """
    Tests getMA
    """

    df = pd.DataFrame({'a':[5,2,5,2]})      
    sym = 'a'
    fastMA = 2
    slowMA = 3
    MA_type = 'SMA'

    trader = movingAverageTrader(df, sym, fastMA, slowMA, MA_type)
    slow, fast = trader.getMA(3)
    assert(slow == 3)
    assert(fast == 3.5)


def test_setTradeReturns():
    """
    Tests setTradeReturns
    """

    df = pd.DataFrame({'a':[5,2,5,2]})      
    sym = 'a'
    fastMA = 2
    slowMA = 3
    MA_type = 'SMA'

    trader = movingAverageTrader(df, sym, fastMA, slowMA, MA_type)
    trader._pos = 1
    trader._setTradeReturns(0, 99)
    assert(trader.df.loc[0, 'returns'] == 99)


def test_openPosition():
    """
    Tests openPosition()
    """
    df = pd.DataFrame({'a':[5,2,5,2]})      
    sym = 'a'
    fastMA = 2
    slowMA = 3
    MA_type = 'SMA'

    trader = movingAverageTrader(df, sym, fastMA, slowMA, MA_type)

    trader.openPosition(0, 'L')
    assert(trader._pos == 1)
    assert(trader._entry_price == 5)

    trader.openPosition(3, 'S')    
    assert(trader._pos == -1)
    assert(trader._entry_price == 2)


def test_closePosition():
    """
    tests closePosition()
    """
    df = pd.DataFrame({'a':[5,2,5,2]})      
    sym = 'a'
    fastMA = 2
    slowMA = 3
    MA_type = 'SMA'

    trader = movingAverageTrader(df, sym, fastMA, slowMA, MA_type)
    trader.openPosition(0, 'L')
    trader.closePosition(3)
    assert(trader._pos == 0)
    assert(trader.df.loc[3, 'returns'] == -0.6)

    trader.openPosition(0, 'S')
    trader.closePosition(1)
    assert(trader._pos == 0)
    assert(trader.df.loc[1, 'returns'] == 0.6) 


