import pandas as pd

from .simple_moving_average import simpleMovingAverage


class expMovingAverage(simpleMovingAverage):
    """
    Class that handles the exponential moving average of a timeseries
    Inherited from simpleMovingAverage class.

    Initialisation:
    - series:               (pd series) of asset
    - period:               (int) period of moving average

    Members:
    - self._period:         (int) period of moving average
    - self._MA:             (pd series, float) panda series of moving
                            average values
    - self.name:            (str) name of object. Primarily used for
                            plot labels.

    Notes:
    - Requires series input is a pandas series

    To Do:
    - Generalise series input to take any type of list/array and convert
    to pandas series on construction.
    """

    def __init__(self, series, period):
        if not isinstance(period, int) or period < 1:
            raise ValueError("Period must be a positive int")
        if not isinstance(series, pd.Series):
            raise ValueError("Series must be a pandas series")

        self._period = period
        self._MA = series.ewm(period).mean()
        self.name = '{} EMA'.format(period)
