import pandas as pd
import os.path
from matplotlib import pyplot as plt

from ..Lib.data_loader import dataLoader
from ..Lib.file_loading_strategies import fileLoadingDF

cpath = os.path.dirname(__file__)

def main():
    infile = cpath + "\\..\\Data\\cryptocompareBTC_10000_hours_df.csv"

    loading_strat = fileLoadingDF(infile)
    loader = dataLoader(loading_strat)
    df = loader.get_data()


    symbols = [symbol for symbol in df.keys() if symbol not in ['date']]
    numcoins = [x.strip() for x in open(cpath + "\\..\\Data\\nums.txt")]
    df['total'] = 0.0

    for i, symbol in enumerate(symbols):
        numcoin = int(numcoins[i])
        df[symbol] = df[symbol]*numcoin
        df['total'] += df[symbol]
    
    df['total'].plot()
    plt.show()


if __name__ == "__main__":
    main()