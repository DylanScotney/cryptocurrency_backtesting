
class simpleMovingAverage():

    """
    Class that handles the simple moving average of a timeseries

    Initialisation:
    - series:               pandas series
    - period:               (int) period of moving average
    - _MA:                  (pandas series) stores SMA series
    - name:                 name of object - can be used for plot labels
    """

    def __init__(self, series, period):
        if not isinstance(period, int) or period < 1:
            raise ValueError("Period must be a positive int")

        self._period = period
        self._MA = series.rolling(window=period).mean()
        self.name = '{} SMA'.format(period)

    def getValue(self, t):
        """
        Returns value of moving average at index t
        """
        return self._MA[t]
    
    def getPeriod(self):
        """
        Returns period of moving average
        """
        return self._period

    def getArray(self):
        """
        Returns whole array of moving averages
        """
        return self._MA
