from .simple_moving_average_class import simpleMovingAverage

class expMovingAverage(simpleMovingAverage):

    def __init__(self, series, period):
        self._period = period
        self._MA = series.ewm(period).mean()