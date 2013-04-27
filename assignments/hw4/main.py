__author__ = 'jjin'

from datetime import datetime
from utilities import find_crossing_threshold_events, graphStrategies, evaluateEventTrades


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