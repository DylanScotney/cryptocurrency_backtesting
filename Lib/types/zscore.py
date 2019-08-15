import pandas as pd


class zScore():
    """
    Class that computes and handles zscore of a series.

    Initialisation:
    - series:               (pandas series) of series values
    - period:               (int) lookback period for zscore

    Members:
    - self._period:         (int) lookback period for z score
    - self.name:            (str) name of the object. Primarily used
                            for plot labels
    - self._zScore:         (pd series, float) z score of the
                            corresponding series.

    Notes:
    - Currently requires input series to be a pandas series.
    - Doesn't store input series to save memory.

    To Do:
    - Improve generalisation by taking series input to be a
    list/np array/pandas series and convert to pandas series if
    necessary
    - Add option to store corresponding input series.
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
        """
        Generates the z score of the input series.
        """
        mean = series.rolling(window=self._period).mean()
        std = series.rolling(window=self._period).std()
        return (series - mean)/std

    def getValue(self, t):
        """
        Returns value of zscore at index t
        """
        return self._zScore[t]

    # read only member accessors
    @property
    def period(self):
        """
        Returns lookback period for zscore
        """
        return self._period

    @property
    def values(self):
        """
        Returns all zscore values
        """
        return self._zScore
