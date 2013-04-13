__author__ = 'jj'

from pprint import pprint
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from numpy.random import multivariate_normal
from utilities import getPrices
from copy import deepcopy
import matplotlib.pyplot as plt


from QSTK.qstkutil.DataAccess import DataAccess
from QSTK.qstkutil.qsdateutil import getNYSEdays
from QSTK.qstkutil.tsutil import returnize1


startDate = datetime(2010, 8, 30)
endDate = datetime(2012, 8, 30)
symbols = ['AAPL', 'GLD', 'MCD', '$SPX']
forecastLength = 21
numPaths = 1000

origPrices = getPrices(startDate, endDate, symbols, 'close')

# get log returns
origLogRets = deepcopy(origPrices)
for col in origLogRets.columns: returnize1(origLogRets[col])
origLogRets = np.log(origLogRets)

print 'first 10 rows of origPrices:\n', origPrices[:10]
# print origLogRets

print '\nCorrelation matrix:\n', origLogRets.corr()

print '\nCholesky decomposition:\n', np.linalg.cholesky(origLogRets.corr())

# get correlated future log returns
meanVec = origLogRets.mean()
covMat = np.cov(origLogRets.T)
futureLogRets = multivariate_normal(meanVec, covMat, (forecastLength, numPaths))    # forecastLength x numpaths x numStocks
# print futureLogRets

# get future prices and plot
futureDates = getNYSEdays(endDate + timedelta(days=1), endDate + timedelta(days = forecastLength*2))[:forecastLength]
futurePrices = {}

origPricesUsedForPlot = origPrices[-2*forecastLength:]  # use twice the forecast length worth of existing data to plot
allDates = list(origPricesUsedForPlot.index) + futureDates

for i in range(len(symbols)):
    s = symbols[i]
    print '------', s, '------'
    curFuturePrices = np.exp(futureLogRets[:, :, i].cumsum(axis=0)) * origPrices.ix[-1, i]
    futurePrices[s] = curFuturePrices
    print 'Average future returns:', curFuturePrices.mean(axis=1)
    plotData = pd.DataFrame(np.row_stack((np.repeat(origPricesUsedForPlot[s].values, futureLogRets.shape[1]).reshape((-1, futureLogRets.shape[1])),
                             futurePrices[s])), index = allDates)

    plotData.plot(title=s, legend=None)
    plt.savefig(s + 'paths.pdf', format='pdf')
    # plt.show()
