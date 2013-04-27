__author__ = 'jjin'

from QSTK.qstkutil.qsdateutil import getNYSEdays
from QSTK.qstkutil.DataAccess import DataAccess
from QSTK.qstkutil.tsutil import returnize0

import matplotlib.pyplot as plt
from datetime import timedelta
from copy import copy, deepcopy
import numpy as np
import pandas as pd


def analyze(prices, marketSymbol, plotFname=None, verbosity=2):
    """
    Calulates and prints metrics & a plot of the portfolio and given marketSymbol.
    @param prices: a time Series
    @param marketSymbol
    @param plotFname: if None (default) the plot will be displayed on screen, otherwise saved as a pdf as given file name
    """

    marketPrices = getPrices(prices.index[0], prices.index[-1], [marketSymbol], 'close')[marketSymbol]

    # metrics
    print '============= PORTFOLIO ============='
    calculateMetrics(prices, verbosity=max(verbosity, 1))
    print '\n============= MARKET EQUITY ============='
    calculateMetrics(marketPrices, verbosity=max(verbosity, 1))

    # plot
    pd.DataFrame({'Market': marketPrices / marketPrices[0] * prices[0], 'Portfolio': prices}).plot(title='Comparison of Historical Prices')

    if plotFname is None:
        plt.show()
    else:
        plt.savefig(plotFname, format='pdf')


def marketsim(ordersData, initialInvestment, verbose=True):
    """
    Compute portfolio given stock trading activity and initial invested amount
    @param ordersData: of the format
                            symbol  numShares
                2008-12-03   AAPL        130
                2008-12-05    IBM         50
                2008-12-08   AAPL       -130
    @param initialInvestment: a scalar
    @return portfolio value in a timeSeries
    """

    ordersData = ordersData.sort_index()    # sort by date

    if verbose:
        print '\nordersData:\n', ordersData

    # --- read relevant data ---
    startDate = ordersData.index[0]
    endDate = ordersData.index[-1]
    symbols = ordersData['symbol'].unique()     # find symbols

    pricesDF = getPrices(startDate, endDate, symbols, 'close')

    # --- get the number of shares of each stock on each day ---
    numSharesDF = ordersData.copy()
    numSharesDF['date'] = numSharesDF.index
    numSharesDF = numSharesDF.pivot_table(rows=['date'], cols=['symbol'], values='numShares')
    if verbose:
        print '\nNumber of shares traded:\n', numSharesDF

    # number of shares of each symbol at the BEGINNING of the day
    numSharesDF = numSharesDF.reindex(index=pricesDF.index).fillna(0).cumsum()    # expand index
    numSharesDF.ix[1:] = numSharesDF.ix[0:-1]
    numSharesDF.ix[0] = 0
    if verbose:
        print '\nNumber of shares held at the beginning of the day:\n', numSharesDF

    # calculate portfolio value
    priceChanges = numSharesDF * pricesDF.diff()

    if verbose:
        print '\npriceChanges for each stock:\n', priceChanges

    priceChanges = priceChanges.sum(axis=1).fillna(0)

    portfolioValue = priceChanges.cumsum() + initialInvestment

    if verbose:
        print '------ Orders ------'
        print ordersData.to_string()
        print '\n------ Stock Prices ------'
        print pricesDF.to_string()
        print '\n------ Trade Book ------'
        print numSharesDF.to_string()
        print '\n------ Portfolio Balances ------'
        print portfolioValue.to_string()

    return portfolioValue

def find_crossing_threshold_events(data, threshold, symbols=None):
    """
    Finds the event data frame.
    The event is defined as when the ACTUAL close of the stock price drops below $5.00,
    more specifically, when:
        price[t-1] >= threshold
        price[t] < threshold
    an event has occurred on date t.
    @param threshold: the crossing of which triggers an event
    """

    print '--- Finding Events:'

    res = deepcopy(data) * np.NAN   # create an empty dataframe
    timeStamps = data.index         # time stamps for the event range

    if symbols is None:
        symbols = data.columns

    for symbol in symbols:
        for t in range(1, len(timeStamps)):

            price_yesterday = data[symbol].ix[timeStamps[t - 1]]
            price_today = data[symbol].ix[timeStamps[t]]

            if price_today < threshold <= price_yesterday:
                res[symbol].ix[timeStamps[t]] = 1

    return res

def fillNA(data):
    """
    fills the na in data
    @param data: a panda data frame
    """

    return data.fillna(method='ffill').fillna(method='bfill').fillna(1.0)


def getPrices(startDate, endDate, symbols, fields, fillna=True, isSymbolsList=False, includeLastDay=True, additionalSymbol=None):
    """
     reads stock prices from Yahoo
     the prices returned INCLUDE the endDate
     @param isSymbolsList: whether the symbols passed in is a stock symbol or a list symbol (e.g. sp5002012).
                           If true, symbols can contain only one symbol.
     @return prices with NaNs filled (forward, backward, 1.0)
    """

    assert not isSymbolsList or isinstance(symbols, str) or len(symbols) == 1, \
        'When isSymbolsList is true, symbols can only contain one symbol.'

    if includeLastDay:
        endDate += timedelta(days=1)

    dataReader = DataAccess('Yahoo')
    timeStamps = getNYSEdays(startDate, endDate, timedelta(hours=16))

    if isSymbolsList:
        symbols = dataReader.get_symbols_from_list(symbols if isinstance(symbols, str) else symbols[0])

    if additionalSymbol is not None:
        symbols += [additionalSymbol] if isinstance(additionalSymbol, str) else additionalSymbol

    data = dataReader.get_data(timeStamps, symbols, fields)

    if fillna:
        data = fillNA(data)

    data.index = pd.Series(data.index) - timedelta(hours=16)  # remove 16 from the dates

    return data


def calculateMetrics(prices, verbosity=2):
    """ Compute metrics of a series of prices
     @param prices: a series of prices. the dates are assumed consecutive and in increasing order
     @return stdDailyRets, avgDailyRets, sharpeRatio, cumRet
    """

    dailyReturns = copy(prices)
    returnize0(dailyReturns)

    stdDailyRets = np.std(dailyReturns)
    avgDailyRets = np.mean(dailyReturns)
    sharpeRatio = avgDailyRets / stdDailyRets * np.sqrt(252)
    cumRet = prices[-1] / prices[0]

    if verbosity >= 2:
        print '-------- Portfolio Prices ------------\n', prices
        print '\n-------- Portfolio Returns ------------\n', dailyReturns
    if verbosity >= 1:
        print '\n--------- Metrics -------------'
        print 'Final portfolio value =', prices[-1]
        print 'Date Range:', prices.index[0], 'to', prices.index[-1]
        print 'Sharpe Ratio =', sharpeRatio
        print 'Total return =', cumRet
        print 'Standard deviation of daily returns =', stdDailyRets
        print 'Average daily returns =', avgDailyRets

    return stdDailyRets, avgDailyRets, sharpeRatio, cumRet


def calculateBollingerValues(prices, lookBackPeriod, numOfStds, verbose=False):
    """
    @returns bollingerVals, means, stds, lowerBand, upperBand
    """

    # compute indicators
    means = pd.rolling_mean(prices, lookBackPeriod)
    stds = pd.rolling_std(prices, lookBackPeriod)
    lowerBand = means - numOfStds * stds
    upperBand = means + numOfStds * stds

    bollingerVals = (prices - means) / (numOfStds * stds)

    if verbose:
        print '------bollingerVals:'
        print bollingerVals

    return bollingerVals, means, stds, lowerBand, upperBand


def createBollingerEventFilter(bollingerVals, typeAndParams, verbose=False):
    """
    creates an event filter according to Bollinger indicators
    @param bollingerVals: the bollinger indicators: (prices - mean)/(num of stds * std)
    @param typeAndParams: a dict of the type of event filter to create and their parameters. Of the format {'type':..., ...}
        'SIMPLE_CROSS':
            when bollingerVals cross a certain value (specified as 'upperVal' and 'lowerVal')
            buy: when lowerVal is reached
            sell: when upperVal is reached
            returns buyEventFilter, sellEventFilter, buyDates and sellDates

        'CROSS_WRT_MARKET_FALL':
            typeAndParams has 'type', 'bolBenchMark', 'marketBenchMark', 'marketSymbol', 'lookBackPeriod', 'numOfStds'
            Bollinger value for the equity yesterday >= bolBenchMark
            Bollinger value for the equity today <= bolBenchMark
            Bollinger value for marketSymbol today >= marketBenchMark
            returns eventFilter, actionDates
    """

    allDates = bollingerVals.index
    allSymbols = bollingerVals.columns

    if typeAndParams['type'] == 'CROSS_WRT_MARKET_FALL':
        bolBenchMark = typeAndParams['bolBenchMark']
        marketBenchMark = typeAndParams['marketBenchMark']

        # get market bollinger values
        marketPrices = getPrices(bollingerVals.index[0], bollingerVals.index[-1], [typeAndParams['marketSymbol']], 'close')
        marketBV, _, _, _, _ = calculateBollingerValues(marketPrices, typeAndParams['lookBackPeriod'], typeAndParams['numOfStds'])

        # look at all criteria
        yesterdayInd = (bollingerVals >= bolBenchMark)
        yesterdayInd.values[1:] = yesterdayInd.values[0:-1] # note: we don't care about the first lookBackPeriod values
        todayInd = (bollingerVals <= bolBenchMark)
        marketInd = marketBV >= marketBenchMark
        eventInd = todayInd & yesterdayInd & np.repeat(marketInd.values, len(allSymbols), axis=1)

        # make the event filter
        eventFilter = deepcopy(bollingerVals) * np.NAN
        eventFilter[eventInd] = 1

        # get dates on which the eventFilter is 1
        actionDates = dict([(symbol, allDates[eventInd[symbol]]) for symbol in allSymbols])

        if verbose:
            print '------- eventFilter:\n', eventFilter
            print '------- actionDates:\n', actionDates

        return eventFilter, actionDates

    elif typeAndParams['type'] == 'SIMPLE_CROSS':
        upperVal = typeAndParams['upperVal']
        lowerVal = typeAndParams['lowerVal']

        buyInd = bollingerVals <= lowerVal
        sellInd = bollingerVals >= upperVal

        # create filters
        buyEventFilter = deepcopy(bollingerVals) * np.NAN
        sellEventFilter = deepcopy(bollingerVals) * np.NAN
        buyEventFilter[buyInd] = 1
        sellEventFilter[sellInd] = 1

        # create buy and sell dates
        buyDates = dict([(symbol, allDates[buyInd[symbol].values.flatten()]) for symbol in allSymbols])
        sellDates = dict([(symbol, allDates[sellInd[symbol].values.flatten()]) for symbol in allSymbols])

        if verbose:
            print '------- buyEventFilter:\n', buyEventFilter
            print '------- sellEventFilter:\n', sellEventFilter
            print '------- buyDates:\n', buyDates
            print '------- sellDates:\n', sellDates

        return buyEventFilter, sellEventFilter, buyDates, sellDates

    raise 'Invalid type %s' % typeAndParams['type']


def plotBollingerBands(prices, means, lowerBand, upperBand, title, bollingerVals, buyDates, sellDates, filename=None):
    plt.figure(figsize=(15, 8))

    # subplot1: prices and bands
    subplot1 = plt.subplot(2, 1, 1)
    plt.plot(prices.index, prices.values, 'b', label='Price', linewidth=1)
    plt.plot(means.index, means.values, 'g--', label='Rolling Mean')
    plt.fill_between(lowerBand.index, lowerBand.values.flatten(), upperBand.values.flatten(), facecolor='grey', alpha=0.2, edgecolor = None)
    plt.legend()

    plt.title(title)

    # subplot2: bollinger indicators
    subplot2 = plt.subplot(2, 1, 2)
    plt.plot(bollingerVals.index, bollingerVals.values)
    plt.fill_between(bollingerVals.index, -1, 1, facecolor='grey', alpha=0.2, edgecolor=None)

    # add vertical lines
    for d in buyDates:
        subplot1.axvline(d, color='g')
        subplot2.axvline(d, color='g')

    for d in sellDates:
        subplot1.axvline(d, color='r')
        subplot2.axvline(d, color='r')

    if filename is None:
        plt.show()
    else:
        plt.savefig(filename, format='pdf')