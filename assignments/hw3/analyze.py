__author__ = 'jjin'

"""
Read in the daily values (cumulative portfolio value) from values.csv and plot them. It should use the symbol on the command line as a benchmark for comparison (in this case $SPX). Using this information, analyze.py should:
Plot the price history over the trading period.
Your program should also output:
Standard deviation of daily returns of the total portfolio
Average daily return of the total portfolio
Sharpe ratio (Always assume you have 252 trading days in an year. And risk free rate = 0) of the total portfolio
Cumulative return of the total portfolio
"""

from datetime import datetime, timedelta
import pandas as pd
import sys
from utilities import analyze

def readPriceData(fname):
    """ Read orders data from csv of format y | m | d | value
     @return a time series
    """

    df = pd.read_csv(fname, header=None, names=['y', 'm', 'd', 'value'])

    # parse dates
    dates = df.apply(lambda row: datetime(int(row['y']), int(row['m']), int(row['d'])), axis=1)

    return pd.Series(df['value'], index=dates)


if __name__ == '__main__':
    pricesFname, marketSymbol = sys.argv

    # test data:
    # prices = pd.TimeSeries(data=[100., 150., 120., 300., 100., 150., 120., 300.],
    #                        index=[datetime(2008, 12, 2), datetime(2008, 12, 3), datetime(2008, 12, 4), datetime(2008, 12, 5),
    #                               datetime(2008, 12, 20), datetime(2008, 12, 30), datetime(2008, 12, 25), datetime(2008, 12, 15)])

    prices = readPriceData(pricesFname)
    analyze(prices, marketSymbol, verbosity=1)