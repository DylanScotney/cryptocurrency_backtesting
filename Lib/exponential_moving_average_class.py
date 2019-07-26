from .simple_moving_average_class import simpleMovingAverage

class expMovingAverage(simpleMovingAverage):
    """
    Class that handles the exponential moving average of a timeseries
    Inherited from simpleMovingAverage class.

    Initialisation:
    - series:               pandas series
    - period:               (int) period of moving average
    - _MA:                  (pandas series) stores EMA series
    - name:                 name of object - can be used for plot labels
    """

    def __init__(self, series, period):        
        if not isinstance(period, int) or period < 1:
            raise ValueError("Period must be a positive int")            
        if not isinstance(series, pd.Series):
            raise ValueError("Series must be a pandas series")

        self._period = period
        self._MA = series.ewm(period).mean()
        self.name = '{} EMA'.format(period)