__author__ = 'jjin'

from pprint import pprint
import numpy as np
from pandas import *

randn = np.random.randn

# ------- series --------
s = Series(randn(5), index=['a', 'b', 'c', 'd', 'e'])

d = {'a' : 0., 'b' : 1., 'c' : 2.}
Series(d)
Series(d, index=['c','a','b', 'f'])

Series(5., index=['a', 'b', 'c', 'd', 'e'])

s = Series(np.random.randn(5), name='something')

# ------- dataframe --------
d = {'one': Series(range(3), index = ['a','b','c']), 'two': Series(range(4), index=['a', 'b', 'c', 'd'])}
df = DataFrame(d)
DataFrame(d, index=['d','b','a'])

d = {'one': range(3), 'two': range(3)}
DataFrame(d)

data = np.zeros((2,),dtype=[('A', 'i4'),('B', 'f4'),('C', 'a10')])
data[:] = [(1,2.,'Hello'),(2,3.,"World")]
d = DataFrame(data)

data2 = [{'a': 1, 'b': 2}, {'a': 5, 'b': 10, 'c': 20}]
d = DataFrame(data2)

d.sum