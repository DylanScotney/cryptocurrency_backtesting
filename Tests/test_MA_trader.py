from pytest import raises
from datetime import datetime
import os.path
import json
import pandas as pd

from ..Lib.MA_trend_trader import movingAverageTrader

def test_initialisation():
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