__author__ = 'jjin'

# computational investing homework 3

from subprocess import call
import sys

if __name__ == '__main__':
    sys.argv = [1000000, 'orders2.csv', 'values2.csv']
    execfile('marketsim.py')

    sys.argv = ['values2.csv', '$SPX']
    execfile('analyze.py')