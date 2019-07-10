from pytest import raises
from datetime import datetime
import os.path
import json
import pandas as pd

from ..Lib.web_loading_strategies import webLoading


def test_initialisation():
    enddate = datetime(2019,1,1)
    expected_start_date = datetime(2018,12,31,23)
    test = webLoading(['a'], "hour", enddate, 1, "jsonfile.json", "csvfile.csv")

    assert(test._symbols == ['a'])
    assert(test._ticksize == "hour")
    assert(test._end_date == enddate)
    assert(test._lookback == 1)
    assert(test._outfile_raw == "jsonfile.json")
    assert(test._outfile_df == "csvfile.csv")
    assert(test._start_date == expected_start_date)


def test_initialisation2():
    enddate = datetime(2019,1,1)
    expected_start_date = datetime(2018,12,31)
    test = webLoading(['a'], "day", enddate, 1, "jsonfile.json", "csvfile.csv")

    assert(test._symbols == ['a'])
    assert(test._ticksize == "day")
    assert(test._end_date == enddate)
    assert(test._lookback == 1)
    assert(test._outfile_raw == "jsonfile.json")    
    assert(test._outfile_df == "csvfile.csv")
    assert(test._start_date == expected_start_date)


def test_initialisation3():
    enddate = datetime(2019,1,1)
    expected_start_date = datetime(2018,12,31,23,59)
    test = webLoading(['a'], "minute", enddate, 1, "jsonfile.json", "csvfile.csv")

    assert(test._symbols == ['a'])
    assert(test._ticksize == "minute")
    assert(test._end_date == enddate)
    assert(test._lookback == 1)
    assert(test._outfile_raw == "jsonfile.json")    
    assert(test._outfile_df == "csvfile.csv")
    assert(test._start_date == expected_start_date)


def test_initialisation_failure1():
    enddate = datetime(2019,1,1)
    symbols = ["not", 1, "all strings"]
    with raises(ValueError):
        webLoading(symbols, "hour", enddate, 1, "jsonfile.json", "csvfile.csv")
    

def test_initialisation_failure2():
    enddate = datetime(2019,1,1)
    ticksize = "non compatible ticksize"
    with raises(ValueError):
        webLoading(['a'], ticksize , enddate, 1, "jsonfile.json", "csvfile.csv")


def test_initialisation_failure3():
    enddate = "non compatible enddate"
    with raises(ValueError):
        webLoading(['a'], "hour" , enddate, 1, "jsonfile.json", "csvfile.csv")


def test_initialisation_failure4():
    enddate = datetime(2019, 1, 1)

    lookback1 = 0
    with raises(ValueError):
        webLoading(['a'], "hour" , enddate, lookback1, "jsonfile.json", "csvfile.csv")

    lookback2 = 1.2
    with raises(ValueError):
        webLoading(['a'], "hour" , enddate, lookback2, "jsonfile.json", "csvfile.csv")


def test_construct_url1():
    enddate = datetime(2019, 1, 1)
    loader = webLoading(["ETH"], "hour", enddate, 1, "jsonfile.json",  "csvfile.csv")
    expected_url = ("https://min-api.cryptocompare.com/data/histohour?fsym=" +
                    "ETH&tsym=BTC&limit=1&api_key=ed65515376edee87d01ec914b" +
                    "ebcd66d66f97cb4f0b7266f54a043b0966758b9")
    url = loader._construct_url("ETH", 1)

    assert(url == expected_url)


def test_construct_url2():
    enddate = datetime(2019, 1, 1)
    loader = webLoading(["ETH"], "hour", enddate, 1, "jsonfile.json", "csvfile.csv")
    expected_url = ("https://min-api.cryptocompare.com/data/histohour?fsym=" +
                    "ETH&tsym=BTC&limit=1&toTs=timestamp&api_key=ed65515376" +
                    "edee87d01ec914bebcd66d66f97cb4f0b7266f54a043b0966758b9")
    url = loader._construct_url("ETH", 1, "timestamp")

    assert(url == expected_url)


def test_pull_data():
    enddate = datetime(2019, 1, 1)
    with open ("expected_pull_data.json") as json_file:
        expected_response = json.load(json_file)
    loader = webLoading(["ETH"], "hour", enddate, 1, "jsonfile.json", "csvfile.csv")
    response = loader._pull_data("ETH", 1, datetime.timestamp(enddate))    

    assert(response == expected_response)


def test_get_data():
    enddate = datetime(2019, 1, 1)
    loader = webLoading(["ETH"], "hour", enddate, 1, "expected_pull_data.json", "csvfile.csv")
    df = loader.get_data()
    df = df.reset_index()
    expected_df = pd.DataFrame({'date': [datetime(2018,12,31,23), 
                                         datetime(2019,1,1)],
                                'ETH': [0.03553, 0.03562]
                                })

    assert(expected_df.equals(df))
    

