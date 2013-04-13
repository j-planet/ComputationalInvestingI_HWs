# computational investing homework 2

__author__ = 'jjin'

import numpy as np
from copy import deepcopy
from os.path import join

from QSTK.qstkutil.qsdateutil import getNYSEdays
from datetime import datetime, timedelta
from QSTK.qstkutil.DataAccess import DataAccess
from QSTK.qstkstudy.EventProfiler import eventprofiler

rootDir = r'C:\Users\jjin\Google Drive\qstk\assignments\hw2'


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


def question_1():

    startDate = datetime(2008, 1, 1)
    endDate = datetime(2009, 12, 31)
    timeStamps = getNYSEdays(startDate, endDate, timedelta(hours=16))

    dataReader = DataAccess('Yahoo')

    for symbolsListName in ['sp5002008', 'sp5002012']:
        # read data
        symbols = dataReader.get_symbols_from_list(symbolsListName)
        symbols.append('SPY')
        data = fillNA(dataReader.get_data(timeStamps, symbols, 'actual_close')) # read data and filled na

        # create events and event-profile
        events = find_crossing_threshold_events(data, threshold=5)
        eventprofiler(events, {'close': data}, i_lookback=20, i_lookforward=20, s_filename = join(rootDir, symbolsListName + '.pdf'),
                      b_market_neutral=True, b_errorbars=True, s_market_sym='SPY')


def question_2():
    startDate = datetime(2008, 1, 1)
    endDate = datetime(2009, 12, 31)
    timeStamps = getNYSEdays(startDate, endDate, timedelta(hours=16))
    dataReader = DataAccess('Yahoo')

    symbolsListName = 'sp5002008'
    symbols = dataReader.get_symbols_from_list(symbolsListName)
    symbols.append('SPY')
    data = fillNA(dataReader.get_data(timeStamps, symbols, 'actual_close')) # read data and filled na

    # create events and event-profile
    events = find_crossing_threshold_events(data, threshold=8)
    eventprofiler(events, {'close': data}, i_lookback=20, i_lookforward=20, s_filename = join(rootDir, symbolsListName + '_threshold8.pdf'),
                  b_market_neutral=True, b_errorbars=True, s_market_sym='SPY')


def question_3():
    startDate = datetime(2008, 1, 1)
    endDate = datetime(2009, 12, 31)
    timeStamps = getNYSEdays(startDate, endDate, timedelta(hours=16))
    dataReader = DataAccess('Yahoo')

    symbolsListName = 'sp5002012'
    symbols = dataReader.get_symbols_from_list(symbolsListName)
    symbols.append('SPY')
    data = fillNA(dataReader.get_data(timeStamps, symbols, 'actual_close')) # read data and filled na

    # create events and event-profile
    events = find_crossing_threshold_events(data, threshold=7)
    eventprofiler(events, {'close': data}, i_lookback=20, i_lookforward=20, s_filename = join(rootDir, symbolsListName + '_threshold7.pdf'),
                  b_market_neutral=True, b_errorbars=True, s_market_sym='SPY')

if __name__ == '__main__':
    question_1()