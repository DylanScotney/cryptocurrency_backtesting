from pytest import raises
from datetime import datetime
import os.path
import json
import pandas as pd

from ..Lib.file_loading_strategies import fileLoadingRaw


def test_initialisation1():
    testfile = "test.json"
    testsyms = ['a', 'b']
    ticksize = "hour"
    loader = fileLoadingRaw(testfile, testsyms, ticksize)

    assert(loader._infile == testfile)
    assert(loader._symbols == testsyms)
    assert(loader._ticksize == ticksize)
    assert(loader._freq == "1H")


def test_initialisation_failure1():
    nonjsonfile = "file.txt"    
    testsyms = ['a', 'b']
    ticksize = "hour"
    with raises(ValueError):
        fileLoadingRaw(nonjsonfile, testsyms, ticksize)


def test_initialisation_failure2():
    testfile = "test.json"
    non_str_syms = [1,2,3]
    ticksize = "hour"
    with raises(ValueError):
        fileLoadingRaw(testfile, non_str_syms, ticksize)


def test_initialisation_failure3():
    testfile = "test.json"    
    testsyms = ['a', 'b']
    incompatible_ticksize = 10
    with raises(ValueError):
        fileLoadingRaw(testfile, testsyms, incompatible_ticksize)


def test_initialisation_failure4():
    testfile = "test.json"    
    testsyms = ['a', 'b']
    ticksize = "hour"
    outfile = "noncsvfile.txt"
    with raises(ValueError):
        fileLoadingRaw(testfile, testsyms, ticksize, outfile=outfile)


def test_get_data():
    testfile = "expected_pull_data.json"
    syms = ['ETH']
    ticksize = "hour"
    loader = fileLoadingRaw(testfile, syms, ticksize)
    df = loader.get_data()

    expected_df = pd.DataFrame({'date': [datetime(2018,12,31,23), 
                                        datetime(2019,1,1)],
                                'ETH': [0.03553, 0.03562]})
    expected_df = expected_df.set_index('date')
    assert(expected_df.equals(df))


def test_get_data_saving():
    testfile = "expected_pull_data.json"
    syms = ['ETH']
    ticksize = "hour"
    loader = fileLoadingRaw(testfile, syms, ticksize, outfile="storecsv.csv")
    loader.get_data()

    df = pd.read_csv("storecsv.csv")
    df2 = pd.read_csv("expectedcsv.csv")

    assert(df.equals(df2))



