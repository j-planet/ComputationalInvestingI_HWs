__author__ = 'jjin'

from QSTK.qstkutil.DataAccess import DataAccess
from QSTK.qstkutil.qsdateutil import getNYSEdays
from QSTK.qstkutil.tsutil import returnize0

from copy import copy
import numpy as np
from datetime import datetime, timedelta
from pprint import pprint
from scipy.misc import comb


def combineStocks(prices, allocations):
    """
    calculates the allocated "prices"
    @param prices: a np array of original prices
    @param allocations: allocations to the equities (buy and hold) in decimals. e.g. [0.2, 0.3, 0.5]
    @type prices numpy.array
    @type allocations list
    @return: a vector with length equal to prices' row count
    """

    assert prices.shape[1] == len(allocations), 'Number of stocks in prices and allocations do not match.'

    return (prices / prices[0,:] * allocations).sum(axis=1)


def simulate(startDate, endDate, symbols, allocations, timeOfDay = timedelta(hours=16), verbose=True, cache=False):
    """
    simulate and assess the performance of a buy-and-hold 4 stock portfolio
    @param startDate: the start date
    @param endDate: the end date
    @param symbols: symbols for the equities, a list
    @param allocations: allocations to the equities (buy and hold) in decimals. e.g. [0.2, 0.3, 0.5]
    @type startDate dt.datetime
    @type endDate dt.datetime
    @type allocations list
    @type symbols list
    @return: Standard deviation of daily returns of the total portfolio, Average daily return of the total portfolio,
    Sharpe ratio (Always assume you have 252 trading days in an year. And risk free rate = 0) of the total portfolio,
    Cumulative return of the total portfolio
    """

    # make time stamps
    timeStamps = getNYSEdays(startDate, endDate, timeOfDay)

    # read data
    dataReader = DataAccess('Yahoo', cachestalltime = 12 if cache else 0)
    data = dataReader.get_data(timeStamps, symbols, ['close'])[0].values    # get the values as a np array
    if verbose: print '-------- Data read ------------\n', data

    # allocate
    portPrices = combineStocks(data, allocations)
    if verbose: print '-------- Portfolio Prices ------------\n', portPrices

    # compute returns
    dailyReturns = copy(portPrices)
    returnize0(dailyReturns)
    if verbose: print '-------- Portfolio Returns ------------\n', dailyReturns

    # compute metrics
    stdDailyRets = np.std(dailyReturns)
    avgDailyRets = np.mean(dailyReturns)
    sharpeRatio = avgDailyRets / stdDailyRets * np.sqrt(252)
    cumRet = portPrices[-1]

    if verbose:
        print '--------- Metrics -------------'
        print 'STD of daily returns =', stdDailyRets
        print 'Average daily returns =', avgDailyRets
        print 'Sharpe Ratio =', sharpeRatio
        print 'Cumulative return =', cumRet

    return stdDailyRets, avgDailyRets, sharpeRatio, cumRet


def findPartitions(n, k):
    """
    k positive integers that add up to n
    @return: a 2D numpy array
    """

    # base case
    if k==1: return np.array([n])

    if n==0: return np.repeat(0, k).reshape(1, -1)

    # recurse
    res = np.empty(shape=(0, k), dtype=int)

    # for firstTerm in np.arange(n - k + 1)+1:
    for firstTerm in np.arange(n+1):
        partialRes = findPartitions(n - firstTerm, k-1)
        part1 = np.repeat(firstTerm, partialRes.shape[0])
        part2 = np.column_stack((part1, partialRes))
        # print 'n =', n, ', k =', k, ', firstTerm =', firstTerm
        # print 'res =', res
        # print 'partialRes =', partialRes
        # print 'part1 =', part1
        # print 'part2 =', part2
        res = np.vstack((res, part2))

    return res


def findBestPortfolio(startDate, endDate, symbols, verbose=True):
    """
    finds the legal allocation (in increments of 0.1) that maximizes the Sharpe Ratio
    @return: (the allocation as a numpy array, the best sharpe ratio)
    """

    allAllocs = findPartitions(10, len(symbols)) / 10.0
    allSharpRatios = [simulate(startDate, endDate, symbols, alloc, verbose=False, cache=True)[2] for alloc in allAllocs]

    if verbose: pprint(dict(zip([tuple(a) for a in allAllocs], allSharpRatios )))

    return allAllocs[np.argmax(allSharpRatios)], max(allSharpRatios)

if __name__ == '__main__':
    # startDate = datetime(2011, 1, 1)
    # endDate = datetime(2011, 12, 31)
    # symbols = ['AAPL', 'GOOG', 'IBM', 'MSFT']
    startDate = datetime(2011, 1, 1)
    endDate = datetime(2011, 12, 31)
    symbols = ['AAPL', 'GLD', 'GOOG', 'XOM']
    allocations = [0.0, 0.0, 0.0, 1.0]

    # compute metrics
    stdDailyRets, avgDailyRets, sharpeRatio, cumRet = simulate(startDate, endDate, symbols, allocations)

    # finds the optimal portfolio
    bestAlloc, bestSharpeRatio = findBestPortfolio(startDate, endDate, symbols)
    print 'the best allocation =', bestAlloc
    print 'the best Sharpe Ratio =', bestSharpeRatio

    print '>>>> FIN <<<<'