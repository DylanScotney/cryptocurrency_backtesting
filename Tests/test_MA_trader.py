from pytest import raises
from datetime import datetime
import os.path
import json
import pandas as pd

from ..Lib.MA_trend_trader import movingAverageTrader


def test_initialisation():
    """
    Tests basic initialisation
    """

    df = pd.DataFrame({'a':[5,4,7,4]})
    sym = 'a'
    fastMA = 5
    slowMA = 30
    MA_type = 'SMA'

    trader = movingAverageTrader(df, sym, fastMA, slowMA, MA_type)

    assert(trader.df.equals(df))
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


