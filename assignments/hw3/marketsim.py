__author__ = 'jjin'

"""
The simulator calculates the total value of the portfolio for each day using adjusted closing prices
(cash plus value of equities) and prints the result to the file values.csv.
"""

from datetime import datetime, timedelta
import pandas as pd
from utilities import marketsim
import sys


def readOrdersData(fname):
    """ Read orders data from csv of format y | m | d | symbol | buy/sell | numShares
     @return a dataframe of the format
                        symbol  numShares
            2008-12-03   AAPL     130
            2008-12-08   AAPL    -130
            2008-12-05    IBM      50
    """

    df = pd.read_csv(fname, header=None, names=['y','m','d','symbol','bs','numShares','unused'])
    del df['unused']

    dates = df.apply(lambda row: datetime(row['y'], row['m'], row['d']), axis=1)
    numShares = df.apply(lambda row: row['numShares'] if row['bs'] == 'Buy' else -row['numShares'], axis=1)
    return pd.DataFrame({'symbol': df['symbol'].values, 'numShares': numShares.values}, index=dates)


def writePortfolioData(portData, fname):
    """ Output portfolio data.
    @param portData: a time series
    @param fname: name of the output file, which has the format y | m | d | value
    @return: nothing
    """

    f = open(fname, 'w')
    for i in xrange(portData.shape[0]):
        curDate = portData.index[i]
        f.write(str(curDate.year) + ',' + str(curDate.month) + ',' + str(curDate.day) + ',' + str(portData.ix[i]) + '\n')
    f.close()


if __name__ == '__main__':
    initialInvestment, ordersFname, outputFname = sys.argv

    """
    Test data:
               symbol  numShares
    2008-12-03   AAPL     130
    2008-12-08   AAPL    -130
    2008-12-05    IBM      50
    """
    # ordersData = pd.DataFrame([['AAPL', 130], ['AAPL', -130], ['IBM', 50]],
    #     index=[datetime(2008, 12, 3), datetime(2008, 12, 8), datetime(2008, 12, 5)],
    #     columns=['symbol', 'numShares'])

    ordersData = readOrdersData(ordersFname)
    portValues = marketsim(ordersData, initialInvestment, verbose=True)
    writePortfolioData(portValues, outputFname)