import json
import numpy as np
from datetime import datetime
import pandas as pd
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters

from .data_loading_strategy import dataLoadingStrat

class fileLoadingRaw(dataLoadingStrat):
    """
    concrete data loading strategy used for dataLoader class. 
    Designed to load raw data stored from CryptoCompare api that as been 
    stored in json format

    Initialisation / construction:
    - infile:               desired json file to load. json file has 
                            been saved using the related webLoading
                            class, that is file is of format:
                            { "asset": [
                                        {
                                            "time": 1552147200,
                                            "close": 3937.14,
                                            "high": 3975.25,
                                            "low": 3933.41,
                                            "open": 3956.05,
                                            "volumefrom": 2041.4,
                                            "volumeto": 8097477.69
                                        },
                                        ...
                                        ],
                            ...
                            }

    """

    def __init__(self, infile, symbols, ticksize, outfile=False):
        
        self._infile = infile
        
        self._symbols = symbols

        if ticksize == "hour":
            self._freq = '1H'
        elif ticksize == "day":
            self._freq = '1D'
        elif ticksize == 'minute':
            self._freq = '1T'
        else: 
            raise ValueError("Incompatible ticksize")
        
        self._ticksize = ticksize

        if outfile:
            self._outfile = outfile


    def get_data(self):
        """
        Loads close prices of all assets in self._symbols for ticksize 
        self._freq from raw data in self._infile by computing several 
        steps:
        1. First checks all data and get the earliest and latest
        timestamps
        2. Creates a pandas dataframe which stores a list of datetimes 
        as an index from earliest timestamp to latest timestamp in steps
        of self._ticksize.
        3. Then pulls associated close prices from raw json file and 
        stores in dataframe. 
        
        Outputs:
        - df:               (pandas DataFrame) holds close prices of all
                            assets in self._symbols along with
                            associated datetimes as index


        Notes:
        - If there is no close prices associated with a given date, 
        function takes price from associated w/ previous time. 
        - This function is reasonably ineffcient as iterates over the
        dataset twice. First to determine times and second to get data        
        """

        
        with open(self._infile) as json_file:
            raw_data = json.load(json_file)
    
        now = datetime.now()
        earliest_timestamp = (now - datetime(1970,1,1)).total_seconds()
        latest_timestamp = 0

        # determine the longest series in file to build dataframe 
        for symbol in self._symbols:
            asset = raw_data[symbol]
            for i in range(len(asset)):     
                if asset[i]['time'] < earliest_timestamp:
                    earliest_timestamp = asset[i]['time']
                if asset[i]['time'] > latest_timestamp:
                    latest_timestamp = asset[i]['time']

        # set up dataframe
        start_date = datetime.fromtimestamp(earliest_timestamp)
        end_date = datetime.fromtimestamp(latest_timestamp)
        times = pd.date_range(start=start_date, end=end_date, freq=self._freq)
        df = pd.DataFrame({'date': times})
        df = df.set_index('date')

        for symbol in self._symbols:
            print(symbol)
            df[symbol] = 0.0 # initilise asset row in df
            asset_data = raw_data[symbol]          

            close_times = [datetime.fromtimestamp(item['time']) for item in asset_data]
            if(self._ticksize=="day"):
                close_times = [time.date() for time in close_times]
            close_prices = [item["close"] for item in asset_data]

            # Store data in dataframe
            #-----------------------------------------------------------
            for i in range(df.shape[0]):
                date = df.index[i]
                if self._ticksize == "day":
                    date = date.date()
                try:
                    index = close_times.index(date)
                    df[symbol][i] = close_prices[index]
                except ValueError:
                    # if no data at date, assume the previous date's data
                    if i > 0:
                        df[symbol][i] = df[symbol][i-1]
            #-----------------------------------------------------------

            if self._outfile:
                df.to_csv(self._outfile)
        
        return df



class fileLoadingDF(dataLoadingStrat):
    """
    Concrete data loading strategy for the data loading class.
    Reads data stored in a pandas DataFrame.
    """

    def __init__(self, infile):
        self._infile = infile

    def get_data(self):
        return pd.read_csv(self._infile)            
        

            
            

        
        
        
        


