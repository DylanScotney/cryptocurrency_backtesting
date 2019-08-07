import pandas as pd

class zScore():
    """
    Class that handles zscore of a series

    Initialisation:
    - series:               pandas series
    - period:               (int) lookback period for zscore
    - _zscore:              (pandas series) stores zscore of series
    - name:                 name of object - can be used for plot labels
    """
    def __init__(self, series, period):
        if not isinstance(period, int) or period < 1:
            raise ValueError("Period must be a positive int")
        if not isinstance(series, pd.Series):
            raise ValueError("Series must be a pandas series")

        self._period = period
        self.name = '{} Zscr'.format(period)
        self._zScore = self.generateZScore(series)

    def generateZScore(self, series):
        mean = series.rolling(window=self._period).mean()
        std = series.rolling(window=self._period).std()
        return (series - mean)/std

    def getValue(self, t):
        """
        Returns value of zscore at index t
        """
        return self._zScore[t]
    
    def getPeriod(self):
        """
        Returns lookback period for zscore
        """
        return self._period

    def getArray(self):
        """
        Returns all zscore values
        """
        return self._zScore
