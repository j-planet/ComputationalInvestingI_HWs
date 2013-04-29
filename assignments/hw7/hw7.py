__author__ = 'jjin'

from datetime import datetime
import matplotlib.pyplot as plt

from utilities import getPrices, createBollingerEventFilter, calculateBollingerValues, makeOrdersAccordingToEvents, \
    marketsim, analyze, calculateMetrics
from QSTK.qstkstudy.EventProfiler import eventprofiler

if __name__ == '__main__':
    startDate = datetime(2008, 1, 1)
    endDate = datetime(2009, 12, 30)

    lookBackPeriod = 20
    numOfStds = 1
    marketSymbol = 'SPY'
    symbols = 'SP5002012'
    bolBenchMark = -2
    marketBenchMark = 1

    holdingPeriod = 5
    numStocksTraded = 100
    initialInvestment = 100000

    # ----- compute prices and create events -----
    prices = getPrices(startDate, endDate, symbols, 'close', isSymbolsList=True, additionalSymbol=marketSymbol)
    # prices = getPrices(startDate, endDate, symbols, 'close', additionalSymbol=marketSymbol)
    bollingerVals, _, _, _, _ = calculateBollingerValues(prices, lookBackPeriod, numOfStds)

    eventFilter, actionDates = createBollingerEventFilter(bollingerVals,
                                                          {'type': 'CROSS_WRT_MARKET_FALL', 'bolBenchMark': bolBenchMark,
                                                           'marketBenchMark': marketBenchMark, 'marketSymbol': marketSymbol,
                                                           'lookBackPeriod': lookBackPeriod, 'numOfStds': numOfStds})

    try:
        eventprofiler(eventFilter, {'close': prices}, i_lookback=lookBackPeriod, i_lookforward=holdingPeriod,
                      b_market_neutral=True, b_errorbars=True, s_market_sym=marketSymbol, s_filename='eventPlot.pdf')
    except:
        print "There aren't enough events for the event profiler."

    # ----- trade and evaluate -----
    orders = makeOrdersAccordingToEvents(eventFilter, holdingPeriod, numStocksTraded, saveIntermediateResults=True)

    portValues = marketsim(orders, initialInvestment)
    # calculateMetrics(portValues, saveIntermediateResults=True)

    analyze(portValues, '$SPX', plotFname='performancePlot.pdf', verbosity=0)

    plt.show()