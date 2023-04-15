import copy
import numpy as np
import pandas as pd
from datetime import date, datetime
from ..signal import Signal

class ChgPct(Signal):
    def __init__(self, database, period:int=1):
        super().__init__(database)
        self.period = period

    def gen_sig(self, start: datetime, end: datetime=None):
        field = 'closePriceBond'
        assert(field in self.data.columns), 'Field Not in the Data.'
        sig_df = copy.deepcopy(self.data[['secID', 'tradeDate', field]])
        sig_df = sig_df.set_index('tradeDate')[start:end]
        sig_df = sig_df.set_index(['secID'], append=True).unstack()[field]
        self.factor = sig_df.pct_change(self.period)
        return self.factor