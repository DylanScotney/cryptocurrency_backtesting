import os.path
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib.ticker import FuncFormatter
from collections import Counter

from ..Lib.data_loader import dataLoader
from ..Lib.web_loading_strategies import webLoading
from ..Lib.file_loading_strategies import fileLoadingRaw, fileLoadingDF

cpath = os.path.dirname(__file__) # current path

infile = cpath + "\\..\\Data\\deleteme.csv"

df = pd.read_csv(infile)
df = df.drop(columns = ['Unnamed: 0', 'date'])
MAs = [1, 10, 20, 40, 50, 80, 100, 120, 160, 200, 240, 280, 320, 360, 400]
MAs = [1, 10, 20, 40, 50, 80, 100, 120, 160]
returns = np.ones((len(MAs), len(MAs)))

count = 0
results = []
keys = []

while (count < len(df.keys())): 
    for i in range(len(MAs)):        
        for j in range(i+1, len(MAs)):
            key = df.keys()[count]
            returns[j, i] += df[key].cumsum().iloc[-1]
            count += 1



def fmt(x, pos):
    return '{}%'.format(np.round(x*100, 0))

returns = returns/23
mask = np.triu(returns, 1)
returns = np.ma.array(returns, mask=mask)
plt.imshow(returns, cmap='RdBu')
plt.colorbar(format=FuncFormatter(fmt))
max_ret = np.nanmax(abs(returns))
max_ret = np.nanmax(returns)
plt.clim(vmax=max_ret, vmin=-max_ret)
plt.xticks(np.arange(len(MAs)), MAs)
plt.yticks(np.arange(len(MAs)), MAs)
plt.xlabel("SMA Period")
plt.ylabel("SMA Period")
plt.show()


#outfile_pfx = cpath + "\\..\\..\\Graphs\\Trend_Results\\probabilities\\"
keys = ["1MA_10MA", "80MA_100MA",  "1MA_200MA", "120MA_160MA", "360MA_400MA", "200MA_280MA"]

fig, ax = plt.subplots(3,2)
fig.add_subplot(111, frameon=False)
plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
plt.grid(False)
plt.xlabel("Trade Returns")
plt.ylabel("Probability")
axes = [ax[0,0], ax[0,1], ax[1,0], ax[1,1], ax[2,0], ax[2,1]]
ranges = [[-1, 1], [-1, 3], [-1, 1], [-1, 3], [-2, 6], [-2, 4]]


for i, key in enumerate(keys):
    diff = df[key].diff().to_numpy()
    diff = [item for item in diff if item != 0]
    diff = [item for item in diff if not np.isnan(item)]

    weights = np.ones_like(diff)/float(len(diff))
    axes[i].hist(diff, weights=weights, bins=100, label=key, range=ranges[i])
    axes[i].legend()
    #plt.savefig(outfile_pfx + "EMA_{}.png".format(key))
    #plt.close()

plt.show()








