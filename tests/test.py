import numpy as np
import pandas as pd
import os, sys
sys.path.append('C:\\users\\yangc\\Downloads\\ConvBond')
import bondtest
from bondtest.dataloader import  DataLoader
import unittest

data = DataLoader(fields='*')
data.set_database( database='ConvBond.pkl')
raw_df = data.get_data(date=None)
print(raw_df.columns)

clas TestConvBond(unittest.TestCase):
    def test_DataLoader(self):
        '''
        Function:
        '''
        