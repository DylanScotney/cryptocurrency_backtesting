import os.path
import numpy as np

from ..Lib.data_loading.file_loading_strategies import fileLoadingDF
from ..Lib.data_loading.data_loader import dataLoader
from ..Lib.spread_class import pairsSpread
from ..Lib.trading_strat_pairs import pairsTrader

cpath = os.path.dirname(__file__)  # current path

def main():

    # Load data
    #--------------------------------------------------------------------------
    infile = cpath + "\\..\\Data\\cryptocompareBTC_10000_hours_df.csv"    
    loading_strat = fileLoadingDF(infile)
    loader = dataLoader(loading_strat)
    df = loader.get_data()
    #--------------------------------------------------------------------------
    XRP = df.loc[:, 'XRP']
    XLM = df.loc[:, 'XLM']
    #spread = pairsSpread(XRP, XLM, 'XRP', 'XLM')
    #spread.generateSpread(t0=100, T=102,plot=True)

    trader = pairsTrader(XRP, XLM, 'XRP', 'XLM')
    trader.trade(plot=True)


if __name__ == "__main__":
    main()