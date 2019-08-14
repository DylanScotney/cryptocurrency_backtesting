from pytest import raises, approx
import pandas as pd

from ..Lib.types.simple_moving_average import simpleMovingAverage

def test_initialisation_series_failure():
    """
    Tests initialisation failure if incorrect input series
    """
    notAPandasSeries = [1,2,3,4,5]
    with raises(ValueError):
        simpleMovingAverage(notAPandasSeries, 5)

def test_initialisation_period_failure():
    """
    tests initialisation failure if incorrect input period
    """
    data = [1,2,3,4,5]
    series = pd.Series(data)
    
    non_postv_int = 0
    with raises(ValueError):
        simpleMovingAverage(series, non_postv_int)

    non_postv_int = -1
    with raises(ValueError):
        simpleMovingAverage(series, non_postv_int)

    non_postv_int = 'Im the incorrect type'
    with raises(ValueError):
        simpleMovingAverage(series, non_postv_int)

def test_initialisation():  
    """
    Tests correct initialisation.
    """  
    data = [1,2,3,4,5]
    series = pd.Series(data)
    period = 5

    SMA = simpleMovingAverage(series, period)
    assert(SMA.getPeriod() == period)
    assert(SMA.name == '5 SMA')

def test_getValue():
    """
    Tests getValue method
    """
    data = [1,2,3,4,5]
    series = pd.Series(data)
    period = 2

    SMA = simpleMovingAverage(series, period)
    assert(SMA.getValue(1) == approx(1.5))
    assert(SMA.getValue(2) == approx(2.5))
    assert(SMA.getValue(3) == approx(3.5))
    assert(SMA.getValue(4) == approx(4.5))