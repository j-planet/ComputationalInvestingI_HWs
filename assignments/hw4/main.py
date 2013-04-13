__author__ = 'jjin'

from collections import Iterable
from datetime import datetime
import sys, os
from copy import deepcopy
import numpy as np
import pandas as pd

from QSTK.qstkstudy.EventProfiler import eventprofiler

sys.path.append('C:\\Users\\jjin\\Google Drive\\qstk\\assignments')

from assignments.hw2.hw2 import find_crossing_threshold_events
from assignments.hw3.marketsim import marketsim
from assignments.hw3.analyze import analyze
from utilities import getPrices


def graphStrategies(eventMaker, startDate, endDate, symbols, marketSymbol, fieldName, isSymbolsList, holdingPeriodsToTry,
                    outputDir='.'):
    """
    run eventprofiler and produce graphs for given the strategy
    @param eventMaker: a function that takes prices as its sole argument
    @return: nothing. save graphs (xxxdays.pdf) to outputDir
    """

    prices = pd.concat([getPrices(startDate, endDate, symbols, fieldName, isSymbolsList=isSymbolsList),
                        getPrices(startDate, endDate, [marketSymbol], fieldName)], axis=1)
    events = eventMaker(prices)

    # make holdingPeriodsToTry iterable
    if not isinstance(holdingPeriodsToTry, Iterable):
        holdingPeriodsToTry = [holdingPeriodsToTry]

    for holdingPeriod in holdingPeriodsToTry:
        eventprofiler(deepcopy(events), {'close': prices}, i_lookback=holdingPeriod, i_lookforward=holdingPeriod,
                      s_filename=os.path.join(outputDir, str(holdingPeriod) + 'days.pdf'),
                      b_market_neutral=True, b_errorbars=True, s_market_sym=marketSymbol)


def makeOrdersAccordingToEvents(events, holdingPeriod, numberOfStocksTraded,
                                saveIntermediateResults=False, outputDir='.'):
    """
    figure out trades according to events
    @param events: dataframe of which stocks to buy and when (columns: stocks, rows: dates). NaN means no trade
    @param holdingPeriod: the number of TRADING days after which to clear out (ideally a df)
    @param numberOfStocksTraded: the number of stocks traded (ideally a df)
    @return orders. of the format
                            symbol  numShares
                2008-12-03   AAPL        130
                2008-12-05    IBM         50
                2008-12-08   AAPL       -130
    """

    # make trade data frame
    buyInd = events
    sellInd = events.shift(holdingPeriod) * -1
    finalInd = buyInd.combineAdd(sellInd)

    # zero out on the last day
    s = finalInd[:-1].sum()     # sum of trades PRIOR to the last day
    finalInd.ix[len(finalInd) - 1] = np.where(s != 0, s, np.NaN) * -1
    assert np.all([v == 0 or np.isnan(v) for v in finalInd.sum()]), 'Error: not all trades are zeroed out on the last day.'

    # convert trade data frame into orders
    orders = finalInd.dropna(how='all').stack().reset_index(0)     # remove days with no orders
    orders.index = orders['level_0'].values         # set index to dates
    del orders['level_0']
    orders = orders.rename(columns={'level_1': 'symbol', 0: 'numShares'})
    orders['numShares'] *= numberOfStocksTraded

    if saveIntermediateResults:
        events.to_csv(os.path.join(outputDir, 'events.csv'))
        temp = deepcopy(orders)
        temp['date'] = temp.index
        temp.index = range(len(temp))
        temp.to_csv(os.path.join(outputDir,'orders.csv'))

    return orders


def evaluateEventTrades(startDate, endDate, symbols, isSymbolsList, eventMaker, holdingPeriod, numberOfStocksTraded,
                        initialInvestment, marketSymbol, fieldName='actual_close', verbosity=2,
                        saveIntermediateResults=False, outputDir='.'):
    """ Evaluate the profitability of trading according to "events".
    @param symbols: either a string or a list of strings, representing stock symbols or a group of stocks (e.g. 'sp5002012')
    @param isSymbolsList: whether symbols is a group of stocks who doesn't have a ticker
    @param holdingPeriod: how long to hold the stock for (TODO: could be different across stocks and dates)
    @param numberOfStocksTraded: how many stocks to trade (TODO: could be different across stocks and dates)
    @param eventMaker: a function that takes prices as its sole argument
    """

    # make events
    prices = getPrices(startDate, endDate, symbols, fieldName, isSymbolsList=isSymbolsList)
    events = eventMaker(prices)
    # print events[:10].to_string()

    # make orders
    orders = makeOrdersAccordingToEvents(events, holdingPeriod, numberOfStocksTraded,
                                         saveIntermediateResults=saveIntermediateResults)

    # back-test (calculate portfolio values)
    portfolio = marketsim(orders, initialInvestment, verbose=(verbosity > 0))

    # analyze results
    analyze(portfolio, marketSymbol, verbosity=verbosity)

    if saveIntermediateResults:
        prices.to_csv(os.path.join(outputDir, 'prices.csv'))
        portfolio.to_csv(os.path.join(outputDir, 'portfolioValues.csv'))


def question1():
    startDate = datetime(2008, 1, 1)
    endDate = datetime(2009, 12, 31)
    symbols = 'sp5002012'
    eventMaker = lambda price: find_crossing_threshold_events(price, threshold=6)
    initialInvestment = 50000
    holdingPeriod = 5
    numberOfStocksTraded = 100
    marketSymbol = '$SPX'

    graphStrategies(eventMaker, startDate, endDate, symbols, marketSymbol, 'actual_close', True, holdingPeriod)

    evaluateEventTrades(startDate, endDate, symbols, True, eventMaker, holdingPeriod, numberOfStocksTraded,
                        initialInvestment, marketSymbol, verbosity=0)


def question2():
    startDate = datetime(2008, 1, 1)
    endDate = datetime(2009, 12, 31)
    symbols = 'sp5002012'
    eventMaker = lambda price: find_crossing_threshold_events(price, threshold=10)
    initialInvestment = 50000
    holdingPeriod = 5
    numberOfStocksTraded = 100
    marketSymbol = '$SPX'

    graphStrategies(eventMaker, startDate, endDate, symbols, marketSymbol, 'actual_close', True, holdingPeriod)

    evaluateEventTrades(startDate, endDate, symbols, True, eventMaker, holdingPeriod, numberOfStocksTraded,
                        initialInvestment, marketSymbol, verbosity=0)


if __name__ == '__main__':

    # startDate = datetime(2008, 1, 1)
    # endDate = datetime(2009, 12, 31)
    # symbols = 'sp5002012'
    # holdingPeriod = 5
    # eventMaker = lambda price: find_crossing_threshold_events(price, threshold=5)
    # numberOfStocksTraded = 100
    # initialInvestment = 50000
    # marketSymbol = '$SPX'
    #
    # graphStrategies(eventMaker, startDate, endDate, symbols, marketSymbol, 'actual_close', True, holdingPeriod)
    #
    # evaluateEventTrades(startDate, endDate, symbols, True, eventMaker, holdingPeriod, numberOfStocksTraded,
    #                     initialInvestment, marketSymbol, verbosity=0)

    question2()