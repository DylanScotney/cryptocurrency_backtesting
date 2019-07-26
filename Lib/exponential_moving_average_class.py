from .simple_moving_average_class import simpleMovingAverage

class expMovingAverage(simpleMovingAverage):

    def __init__(self, series, period):
        
        if not isinstance(period, int) or period < 1:
            raise ValueError("Period must be a positive int")

        self._period = period
        self._MA = series.ewm(period).mean()
        self.name = '{} EMA'.format(period)