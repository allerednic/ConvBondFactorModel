# -*- coding:utf-8 -*-
import tushare as ts
import pandas as pd
import numpy as np 
import datetime as dt
from .._config import _data_path


try:
    trade_dates = ts.pro_api().trade_cal()
    trade_dates.set_index('cal_date', inplace=True)
    trade_dates.to_csv(f'{_data_path}/trading_calendar.csv')
except:
    trade_dates = pd.read_csv(f'{_data_path}/trading_calendar.csv', 
                              dtype={'cal_date':str, 'pretrade_date':str}, 
                              parse_dates=['cal_date', 'pretrade_date'])

def is_trading_day(date):
    """
    Function:
        check the input date is trading day or not.
    Args:
        date (str): input date, '20230505'
    """ 
    return trade_dates.loc[pd.to_datetime(date), 'is_open']
    
    

def api_checker(func):
    '''
    Function:
        Check if the api has responded successfully.
    '''
    def inner(*args, ** kwargs):
            