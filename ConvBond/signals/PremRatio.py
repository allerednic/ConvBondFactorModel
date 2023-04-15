# import sys
# sys.path.append('C:\\Users\\yangc\\Downloads\\ConvBond')
import copy
import numpy as np
import pandas as pd
from datetime import date, datetime
from ..signal import Signal

class PremRatio(Signal):    
    def gen_sig(self, start: datetime, end: datetime=None):
        field = 'bondPremRatio'
        assert(field in self.data.columns), 'Field Not in the Data.'
        sig_df = copy.deepcopy(self.data[['secID', 'tradeDate', field]])
        sig_df = sig_df.set_index('tradeDate')[start:end]
        sig_df = sig_df.set_index(['secID'], append=True).unstack()[field]
        self.factor = sig_df
        return self.factor
