import requests
import json
from datetime import datetime, timedelta
import math
import pandas as pd

from .abstract_data_loading_strategy import dataLoadingStrat


class webLoading(dataLoadingStrat):
    """
    Concrete implementation of a data loading strategy used in
    dataLoader class. designed to pull crypto exchange OHLCV data
    from https://www.cryptocompare.com.

    Initialisation / construction:
    - api_key:      cryptocompare api key
    - symbols:      (list) of str of ticker symbols for coins to be considered
                    e.g. ["BTC", "LTC", "ETH", ...]
    - ticksize:     (str) ticksize of data considered. cryptocompare
                    currently only accepts: "day", "hour", or "minute"
    - end_date:     (python datetime) object of the most latest
                    date of desired data
    - lookback:     (int) number of ticks of data to request
    - outfile_raw:  (json) json file storing OHLCV data
    - outfile_df:   (csv) csv file that stores close prices in a pandas
                    DataFrame
    """

    def __init__(self, api_key, symbols, ticksize, end_date,
                 lookback, outfile_raw, outfile_df):

        if not all(isinstance(symbol, str) for symbol in symbols):
            raise ValueError("Symbols must be list of string types")

        if ticksize not in ("hour", "minute", "day"):
            raise ValueError(("Ticksize not compatible."
                              + "Use: 'day', 'hour', 'minute'"))

        if not isinstance(end_date, datetime):
            raise ValueError("end_date must be a datetime object")

        if not ((isinstance(lookback, int)) and (lookback >= 1)):
            raise ValueError("lookback must be a positive int")
        
        # private memebers as to be instiated on construction only
        self._key = api_key
        self._symbols = symbols
        self._ticksize = ticksize
        self._end_date = end_date
        self._lookback = lookback
        self._outfile_raw = outfile_raw
        self._outfile_df = outfile_df

        # Free CryptoCompare API has max 2000 datapoints per pull
        self._limit = 2000

        # Compute startdate from end date
        if ticksize == "minute":
            self._timedelta = timedelta(minutes=-self._lookback)
        elif ticksize == "hour":
            self._timedelta = timedelta(hours=-self._lookback)
        elif ticksize == "day":
            self._timedelta = timedelta(days=-self._lookback)
        self._start_date = self._end_date + self._timedelta

    def _construct_url(self, symbol, limit, timestamp='none'):
        """
        Constructs URL compatible with cryptocompare API software

        Inputs:
        - symbol:           (str) Desired ticker symbol, e.g. "BTC"
        - limit:            (int) Number of ticks to request
        - timestamp:        (int) Timestamp of the latest date of dataset
        """
        if timestamp == 'none':
            url = ("https://min-api.cryptocompare.com/data/histo{}?fsym={}&tsym=BTC&limit={}&api_key={}".format(self._ticksize, symbol, limit, self._key))

        else:
            url = ("https://min-api.cryptocompare.com/data/histo{}?fsym={}&tsym=BTC&limit={}&toTs={}&api_key={}".format(self._ticksize, symbol, limit, timestamp, self._key))
        return url

    def _pull_data(self, symbol, limit, timestamp='none'):
        """
        Used to request and store data in JSON files from cryptocompare.
        Default call will return close prices of asset
        '''

        Inputs:
        - symbol:           (str) ticker symbol of desired coin
        - limit:            (int) number of ticks to request
        - timestamp:        (int) lastest timestamp of dataseries

        Output:
        - content:          (list, floats) list of close prices for
                            given data
        '''
        """

        if timestamp == 'none':
            address = self._construct_url(symbol, limit)
        else:
            address = self._construct_url(symbol, limit, timestamp)
        response = requests.get(address)
        content = response.json()

        if(content["Response"] == "Error"):
            raise RuntimeError(content["Message"])

        return content

    def get_data(self):
        """
        Gets all available data for each asset in self.symbols
        from self._start_date to self._end_date. Stores data in outfiles

        Output:
        - df:                   (pandas dataframe) of format:
                                df = {
                                      'index' : [<list of dattimes>]
                                      'asset1': [<list of close prices>]
                                      ...
                                     }
        """

        # initialise dataframe
        # ---------------------------------------------------------------------
        if self._ticksize == "hour":
            freq = '1H'
        elif self._ticksize == "day":
            freq = '1D'
        elif self._ticksize == 'minute':
            freq = '1T'
        else:
            raise ValueError("incompatible ticksize")

        times = pd.date_range(start=self._start_date,
                              end=self._end_date, freq=freq)
        df = pd.DataFrame({'date': times})
        df = df.set_index('date')
        # ---------------------------------------------------------------------
        # Declare some params for extraction
        enddate_stamp = (self._end_date - datetime(1970, 1, 1)).total_seconds()
        calls_needed = math.ceil(self._lookback/self._limit)
        final_call_limit = self._lookback % self._limit

        data_dict = {}

        # ---------------------------------------------------------------------
        for symbol in self._symbols:
            df[symbol] = 0.0  # initialise asset row in df

            # Extract data from api
            # -----------------------------------------------------------------
            data = []

            for i in range(1, calls_needed+1):
                if (i == calls_needed) and (final_call_limit > 0):
                    limit = final_call_limit
                else:
                    limit = self._limit

                # Request limit hours of data up to enddate_stamp
                content = self._pull_data(symbol, limit, enddate_stamp)

                # update timestamp for next request
                enddate_stamp = content["TimeFrom"]

                # store extracted data
                data.extend(content['Data'])
            # -----------------------------------------------------------------

            close_times = ([datetime.fromtimestamp(item['time'])
                           for item in data])
            if(self._ticksize == "day"):
                close_times = [time.date() for time in close_times]
            close_prices = [item["close"] for item in data]

            # Store data in dataframe
            # -----------------------------------------------------------------
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
            # -----------------------------------------------------------------

            data_dict[symbol] = data

            # redeclare end_stamp to pull next symbol data
            enddate_stamp = ((self._end_date - datetime(1970, 1, 1))
                             .total_seconds())
        # ---------------------------------------------------------------------

        # save raw data and dataframe
        with open(self._outfile_raw, 'w') as json_file:
            json.dump(data_dict, json_file, indent=4)
        df.to_csv(self._outfile_df)

        return df
