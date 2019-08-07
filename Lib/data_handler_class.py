import pandas as pd

from ..Lib.zscore_class import zScore
from ..Lib.simple_moving_average_class import simpleMovingAverage
from ..Lib.exponential_moving_average_class import expMovingAverage

class dataHandler():
    """
    Class for handling time series data in order to handle moving
    average and z score classes along side series. 

    Intialisation/Construction:
    - self.price_series:            (pandas series) pandas series type 
                                    of time series data
    - self.data:                    dictionary that holds other data 
                                    members outside of the price series 
    
    """

    def __init__(self, series):
        self.price_series = series
        print(type(self.price_series))
        self.data = {}

    def addMovingAverage(self, name, period, Type="SMA"):
        """
        Adds a moving average object of a given period to the self.data 
        dictionary under the name key.
        """
        if(Type == "SMA"):
            self.data[name] = simpleMovingAverage(self.price_series, period)
        elif(Type == "EMA"):
            self.data[name] = expMovingAverage(self.series, period)
        else:
            raise ValueError("Type not recognised. Use 'SMA' or 'EMA'")

    def addZScore(self, name, period):
        """
        Adds a zScore object of a given period to the self.data 
        dictionary under the name key.
        """
        self.data[name] = zScore(self.price_series, period)
    
    def deleteData(self, name):
        """
        Deletes the data member name from self.data. Throws a KeyError
        if name not in self.data
        """
        self.data.pop(name)
    
    

        

