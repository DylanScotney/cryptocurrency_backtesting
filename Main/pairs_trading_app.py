import os.path
import numpy as np

from ..Lib.data_loading.file_loading_strategies import fileLoadingDF
from ..Lib.data_loading.data_loader import dataLoader
from ..Lib.strategies.pairs import pairsTrader

cpath = os.path.dirname(__file__)  # current path

def main():

    # Load data
    #--------------------------------------------------------------------------
    infile = cpath + "\\..\\Data\\cryptocompareBTC_10000_hours_df.csv"    
    loading_strat = fileLoadingDF(infile)
    loader = dataLoader(loading_strat)
    df = loader.get_data()
    #--------------------------------------------------------------------------
    XMR = df.loc[:, 'XMR']
    XEM = df.loc[:, 'XEM']
    #spread = pairsSpread(XRP, XLM, 'XRP', 'XLM')
    #spread.generateSpread(t0=100, T=102,plot=True)

    trader = pairsTrader(XMR, XEM, 'XMR', 'XEM')
    trader.trade(plot=True)


if __name__ == "__main__":
    main()