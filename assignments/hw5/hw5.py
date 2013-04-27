__author__ = 'jjin'

from datetime import datetime

from utilities import getPrices, calculateBollingerValues, createBollingerEventFilter, plotBollingerBands


if __name__ == '__main__':
    startDate = datetime(2010, 1, 1)
    endDate = datetime(2010, 12, 31)
    lookBackPeriod = 20
    numOfStds = 2
    symbols = ['AAPL', 'GOOG', 'IBM', 'MSFT']

    # ----- compute prices and Bollinger stuff -----
    prices = getPrices(startDate, endDate, symbols, 'close')

    bollingerVals, means, stds, lowerBand, upperBand = calculateBollingerValues(prices, lookBackPeriod, numOfStds, verbose=False)
    _, _, buyDates, sellDates = createBollingerEventFilter(bollingerVals, {'type': 'SIMPLE_CROSS', 'upperVal': 1, 'lowerVal': -1}, verbose=False)

    # ----- plot -----
    for symbol in symbols:
        title = symbol + ': ' + str(numOfStds) + '-stds Bollinger Bands'
        filename = "%s_%dlookback_%dstds_%s-%s.pdf" % (symbol, lookBackPeriod, numOfStds, str(startDate.date()), str(endDate.date()))

        plotBollingerBands(prices[symbol], means[symbol], lowerBand[symbol], upperBand[symbol], title,
                           bollingerVals[symbol], buyDates[symbol], sellDates[symbol], filename=filename)
