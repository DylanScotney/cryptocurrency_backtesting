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

infile = cpath + "\\..\\Data\\test.csv"

df = pd.read_csv(infile)
df = df.drop(columns = ['Unnamed: 0', 'date'])
df = (df - 1)/23
df = df*100
df.plot()
plt.show()
MAs = [1, 10, 20, 40, 50, 80, 100, 120, 160, 200, 240, 280, 320, 360, 400]
MAs = [1, 10, 20, 50, 80, 100, 200]
returns = np.ones((len(MAs), len(MAs)))

count = 0
results = []
keys = []

print(df.keys())
for key in df.keys():
    print(key, df[key].iloc[-1])
    keys.append(key)
    results.append(df[key].iloc[-1])

count = 0
for i in range(len(MAs)):
    for j in range(i, len(MAs)):
        returns[j,i] = results[count]
        count += 1


def fmt(x, pos):
    return '{}%'.format(x)


mask = np.triu(returns,1)
returns = np.ma.array(returns, mask=mask)
plt.imshow(returns, cmap = 'Spectral')
cb = plt.colorbar(format = FuncFormatter(fmt))
plt.clim(vmax=100)
plt.xticks(np.arange(len(MAs)), MAs)
plt.yticks(np.arange(len(MAs)), MAs)
plt.xlabel("EMA Period")
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








