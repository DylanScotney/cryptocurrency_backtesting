from pytest import raises
from datetime import datetime
import os.path
import json
import pandas as pd

from ..Lib.file_loading_strategies import fileLoadingDF


def test_initialisation():
    loader = fileLoadingDF("testfile.csv")
    assert(loader._infile == "testfile.csv")


def test_initialisation_failure():
    not_a_csv = "somefile.txt"
    with raises(ValueError):
        fileLoadingDF(not_a_csv)


def test_get_data():
    infile = "storecsv.csv"
    loader = fileLoadingDF(infile)
    df = loader.get_data()
    expected_df = pd.read_csv("expectedcsv.csv")

    assert(expected_df.equals(df))

