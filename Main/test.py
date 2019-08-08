import pandas as pd
import os.path
from matplotlib import pyplot as plt

from ..Lib.data_handler_class import dataHandler
from ..Lib.data_loading.file_loading_strategies import fileLoadingDF
from ..Lib.data_loading.data_loader import dataLoader

cpath = os.path.dirname(__file__)  # current path

def main():
    # Load data
    #--------------------------------------------------------------------------
    infile = cpath + "\\..\\Data\\cryptocompareBTC_10000_hours_df.csv"    
    loading_strat = fileLoadingDF(infile)
    loader = dataLoader(loading_strat)
    df = loader.get_data()
    #--------------------------------------------------------------------------
    XRP = dataHandler(df.XRP)

    XRP.addMovingAverage("20SMA", 100)

    plt.plot(XRP.price_series)
    plt.plot(XRP.data.20SMA.getArray(), label='20SMA')
    plt.show()




if __name__ == "__main__":
    main()