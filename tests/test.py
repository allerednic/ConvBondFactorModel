import os, sys
import numpy as np
import pandas as pd
import unittest

from pathlib import Path
proj_path = Path(__file__).parent.parent
sys.path.insert(0, str(proj_path))
from ConvBond.data import CBData




class TestConvBond(unittest.TestCase):
    def test_DataLoader(self):
        '''
        Function:
        '''
        data = CBData()
        # data.cb_basic()
        df = data.cb_daily(start_date='20190101')
    