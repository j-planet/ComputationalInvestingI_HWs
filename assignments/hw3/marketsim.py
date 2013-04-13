__author__ = 'jjin'

"""
The simulator calculates the total value of the portfolio for each day using adjusted closing prices
(cash plus value of equities) and prints the result to the file values.csv.
"""

from datetime import datetime, timedelta
import pandas as pd
from utilities import getPrices
import sys


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