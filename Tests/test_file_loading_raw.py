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
