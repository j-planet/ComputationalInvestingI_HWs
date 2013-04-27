__author__ = 'jjin'

from datetime import datetime
from pprint import pprint

from utilities import getPrices, createBollingerEventFilter, calculateBollingerValues
from QSTK.qstkstudy.EventProfiler import eventprofiler

if __name__ == '__main__':
    startDate = datetime(2008, 1, 1)
    endDate = datetime(2009, 12, 31)
    lookBackPeriod = 20
    numOfStds = 1
    marketSymbol = 'SPY'
    # symbols = ['AAPL', 'GOOG', 'IBM', 'MSFT']
    symbols = 'SP5002012'

    # ----- compute prices and Bollinger stuff -----
    prices = getPrices(startDate, endDate, symbols, 'close', isSymbolsList=True, additionalSymbol=marketSymbol)
    bollingerVals, _, _, _, _ = calculateBollingerValues(prices, lookBackPeriod, numOfStds)

    eventFilter, actionDates = createBollingerEventFilter(bollingerVals,
                                                          {'type': 'CROSS_WRT_MARKET_FALL', 'bolBenchMark': -2,
                                                           'marketBenchMark': 2, 'marketSymbol': marketSymbol,
                                                           'lookBackPeriod': lookBackPeriod, 'numOfStds': numOfStds})
    pprint(actionDates)

    eventprofiler(eventFilter, {'close': prices}, i_lookback=lookBackPeriod, i_lookforward=1,
                  s_filename = None, b_market_neutral=True, b_errorbars=True, s_market_sym=marketSymbol)