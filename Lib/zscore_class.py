
class zScore():
    
    def __init__(self, series, period):
        if not isinstance(period, int) or period < 1:
            raise ValueError("Period must be a positive int")

        self._period = period
        self.name = '{} Zscr'.format(period)
        mean = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        self._zScore = (series - mean)/std

    def getValue(self, t):
        return self._zScore[t]
    
    def getPeriod(self):
        return self._period

    def getArray(self):
        return self._zScore
