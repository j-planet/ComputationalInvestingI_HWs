__author__ = 'jjin'

from datetime import datetime

from utilities import getPrices, createBollingerEventFilter, plotBollingerBands


if __name__ == '__main__':
    startDate = datetime(2010, 1, 1)
    endDate = datetime(2010, 12, 31)
    lookBackPeriod = 20
    numOfStds = 2
    symbols = ['AAPL', 'GOOG', 'IBM', 'MSFT']

    # ----- compute prices and Bollinger stuff -----
    prices = getPrices(startDate, endDate, symbols, 'close')

    eventFilter, bollingerVals, means, _, lowerBand, upperBand, buyDates, sellDates = createBollingerEventFilter(prices, lookBackPeriod, numOfStds)

    # ----- plot -----
    for symbol in eventFilter.columns:
        title = symbol + ': ' + str(numOfStds) + '-stds Bollinger Bands'
        filename = "%s_%dlookback_%dstds_%s-%s.pdf" % (symbol, lookBackPeriod, numOfStds, str(startDate.date()), str(endDate.date()))

        plotBollingerBands(prices[symbol], means[symbol], lowerBand[symbol], upperBand[symbol], title,
                           bollingerVals[symbol], buyDates[symbol], sellDates[symbol], filename=filename)
