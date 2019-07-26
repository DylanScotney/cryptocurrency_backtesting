
class simpleMovingAverage():

    def __init__(self, series, period):
        if not isinstance(period, int) or period < 1:
            raise ValueError("Period must be a positive int")

        self._period = period
        self._MA = series.rolling(window=period).mean()
        self.name = '{} SMA'.format(period)

    def getValue(self, t):
        return self._MA[t]
    
    def getPeriod(self):
        return self._period

    def getArray(self):
        return self._MA
