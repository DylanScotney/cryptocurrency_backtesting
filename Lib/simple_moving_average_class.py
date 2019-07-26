import pandas as pd

class simpleMovingAverage():

    def __init__(self, series, period):
        if not isinstance(period, int):
            raise ValueError("Period must be integer")

        self._period = period
        self._MA = series.rolling(window=period).mean()

    def getValue(self, t):
        return self.MA[t]
    
    def getPeriod(self):
        return self._period

    def getArray(self):
        return self._MA.to_numpy()
