# -*- coding: utf-8 -*-

"""
Creator: C-S Yang
Update Time: 2023-03-26
Function:
    Data handling class.

Descritpion
Data should be stored in the form ConvBond.Daily.[Open,High,Low...]
""" 
import os
import pandas as pd
import tushare as ts
from typing import Union, List
from abc import abstractclassmethod
from sqlalchemy import create_engine
from datetime import date, datetime, timedelta
from ._data_config import _data_path

trade_dates = ts.pro_api().trade_cal()
trade_dates.set_index('cal_date', inplace=True)
trade_dates.to_csv(f'{_data_path}/trading_calendar.csv')

# def is_business_day(date):
#     '''
#     Function:
#         Check if the given date is business date
#     date: str, '20230101'
#     '''
#     return trade_dates.loc[date, 'is_open']

class Data:

    def __init__(self, data_type:str) -> None:
        '''
        Function:  
            Initialize the system.
        data_type:   stock, future, convbond
        
        '''
        self.data_type =  data_type
        self.data_fields = []
        self.dataframe = pd.DataFrame() 
        self.database = f'{_data_path}/{self.data_type}.db'

    @abstractclassmethod
    def get_data(self, fields, *args, **kwargs):
        '''
        Function::
            Get data for specific date range
        '''
        ### connect to the database
        pass
    
class CBData(Data):
    
    def __init__(self, ** kwargs) -> None:
        super().__init__(data_type='convbond')
        self.api = ts.pro_api()

    def get_data(self, table, fields, start_date, end_date):
        '''
        Function:
            Get data from the local database.
        '''
        engine = create_engine(f'sqlite:///{self.database}',echo=False)
        data_fields = ','.join(fields)
        df = pd.read_sql(f'select {data_fields} from {table}', engine)
        return df
    
    def cb_daily(self, start_date:str, end_date:str = f'{date.today():%Y%m%d}'):
        '''
        Function:
            Download daily data using pro_api. The data should be stored in format feather.
        DataFields:
            ts_code:	    转债代码
            trade_date:     交易日期
            pre_close:      昨收盘价(元)
            open:   	    开盘价(元)
            high:           最高价(元)
            low:            最低价(元)
            close:          收盘价(元)
            change:         涨跌(元)
            pct_chg:        涨跌幅(%)
            vol:            成交量(手)
            amount:         成交金额(万元)
            bond_value:     纯债价值
            bond_over_rate: 纯债溢价率(%)
            cb_value:       转股价值
            cb_over_rate:   转股溢价率(%)
            
        '''

        tmp_date = datetime(start_date, '%Y%m%d').date()
        start_date = datetime(end_date, '%Y%m%d').date()

        day = timedelta(days=1)
        df_list = []
        data_fields = ['ts_coode', 'trade_date', 'pre_close', 'open','high',
                        'low', 'close','change', 'pct_chg', 'vol', 'amount',
                        'bond_value', 'bond_over_rate', 'cb_value', 'cb_over_rate']
        while tmp_date <= end_date:
            if trade_dates.loc[tmp_date.strftime('%Y%m%d'),'is_open']:
                tmp_df = self.api.cb_daily(trade_date=tmp_date.strftime('%Y%m%d'), fields=data_fields)
                df_list.append(tmp_df)
            
            tmp_date += day

        df = pd.concat(df_list, ignore_index=True)
        df.set_index(keys=['ts_code','trade_date'], inplace=True)
        ### save to feathers
        file_name = f'{_data_path}/{self.data_type}/cb_daily.feather'
        if os.path.exists(file_name):
            #### check if the old_df already exists, if does, update the data
            old_df = pd.read_feather(file_name)
            old_df.set_index(keys=['ts_code','trade_date'], inplace=True)
            index_duplicate = old_df.index.intersection(df.index)
            old_df.drop(index=index_duplicate, inplace=True, errors='ignore')
            pd.concat([old_df,df]).reset_index().to
        else: 
            df.to_feather(file_name)
        
        return df

    def cb_basic(self, *args, **kwargs):
        '''
        Function:
            Get the basic information of the convbond.
        DataField:
            ts_code	str	Y	转债代码
            bond_full_name	str	Y	转债名称
            bond_short_name	str	Y	转债简称
            cb_code	str	Y	转股申报代码
            stk_code	str	Y	正股代码
            stk_short_name	str	Y	正股简称
            maturity	float	Y	发行期限（年）
            par	float	Y	面值
            issue_price	float	Y	发行价格
            issue_size	float	Y	发行总额（元）
            remain_size	float	Y	债券余额（元）
            value_date	str	Y	起息日期
            maturity_date	str	Y	到期日期
            rate_type	str	Y	利率类型
            coupon_rate	float	Y	票面利率（%）
            add_rate	float	Y	补偿利率（%）
            pay_per_year	int	Y	年付息次数
            list_date	str	Y	上市日期
            delist_date	str	Y	摘牌日
            exchange	str	Y	上市地点
            conv_start_date	str	Y	转股起始日
            conv_end_date	str	Y	转股截止日
            conv_stop_date	str	Y	停止转股日(提前到期)
            first_conv_price	float	Y	初始转股价
            conv_price	float	Y	最新转股价
            rate_clause	str	Y	利率说明
            put_clause	str	N	赎回条款
            maturity_put_price	str	N	到期赎回价格(含税)
            call_clause	str	N	回售条款
            reset_clause	str	N	特别向下修正条款
            conv_clause	str	N	转股条款
            guarantor	str	N	担保人
            guarantee_type	str	N	担保方式
            issue_rating	str	N	发行信用等级
            newest_rating	str	N	最新信用等级
            rating_comp	str	N	最新评级机构
        '''
        ts_code = kwargs.get('ts_code', None)
        list_date = kwargs.get('list_date', None)
        exchange = kwargs.get('exchange', None)
        data_fields = kwargs.get('fields', ["ts_code", "bond_full_name",  "bond_short_name",
                                       "cb_code", "stk_code", "stk_short_name", "maturity",
                                       "par", "issue_price", "issue_size", "remain_size",
                                       "value_date", "maturity_date", "rate_type", "coupon_rate",
                                       "add_rate", "pay_per_year","list_date","delist_date",
                                       "exchange","conv_start_date","conv_end_date","conv_stop_date",
                                       "first_conv_price","conv_price","rate_clause","put_clause",
                                       "maturity_put_price","call_clause","reset_clause","conv_clause",
                                       "guarantor","guarantee_type","issue_rating","newest_rating", 
                                       "rating_comp"])
        df = self.api.cb_basic(ts_code=ts_code, list_date=list_date, exchange=exchange, fields=data_fields)

        df.set_index(keys=['ts_code'], inplace=True)
        ### save to feathers
        file_name = f'{_data_path}/{self.data_type}/cb_basic.feather'
        if os.path.exists(file_name):
            #### check if the old_df already exists, if does, update the data
            old_df = pd.read_feather(file_name)
            old_df.set_index(keys=['ts_code'], inplace=True)
            index_duplicate = old_df.index.intersection(df.index)
            old_df.drop(index=index_duplicate, inplace=True, errors='ignore')
            pd.concat([old_df,df]).to_feather(file_name)
        else: 
            df.to_feather(file_name)
        
        return df
        

    def cb_issue(self, *args, **kwargs):
        '''
        '''
        pass

    def cb_call(self, *args, **kwargs):
        '''
        '''
        pass

    def cb_rate(self, *args, **kwargs):
        '''
        '''
        pass

    def cb_cpx_chg(self, *args, **kwargs):
        '''
        '''
        ts_codes = kwargs.get('ts_code', [])
        data_fields = kwargs.get('fields', [
                        "ts_code",
                        "bond_short_name",
                        "publish_date",
                        "change_date",
                        "convert_price_initial",
                        "convertprice_bef",
                        "convertprice_aft"
                            ])
        df = self.api.cb_cpx_chg(ts_code=ts_codes, list_date=list_date, exchange=exchange, fields=data_fields)
    
    def cb_share(self, *args, **kwargs):
        '''
        '''
        pass
