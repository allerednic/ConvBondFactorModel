#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Author: c.s.yang
Updated : 20220724
Function:
    define the signal class
    and the signal test methods
'''

import numbers
import pandas_bokeh
import numpy as np
import pandas as pd
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
from copy import deepcopy
from abc import ABC, abstractmethod

from .data import Data
from .lib.utils import *

from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.layouts import  column
from bokeh.io import output_notebook
from bokeh.resources import  INLINE
output_notebook(INLINE)



class Signal:


    def __init__(self, database):
        self.database = database
        Signal.data.set_database(database)
        self.data = Signal.data.get_data()
        self.factor = pd.DataFrame()
    
    @abstractmethod
    def gen_sig(self, start: dt.datetime, end:dt.datetime=None):
        '''
        generate dataframe of signals
        '''
        pass
    
    def _bin_op(op, first_, second_):
        '''
        Function:
            Decrator for binary operands operator,
        Input:
            op: operator,
            first: the first operand, should be Signal
            second: the second operand.
        '''
        assert (first_.data is not None), 'The signal has not generated'
        pass

    def __add__(self, other):
        ''' 
        Function:
            Adding another signal or float number.
        '''
        assert(isinstance(other, (numbers.Real, Signal))), 'TypeError for "+" operands.'

        return self.factor.fillna(0.0) + other.factor.fillna(0.0) if isinstance(other, Signal) else self.factor.fillna(0.0) + other

    def __radd__(self, other):
        '''
        Function:
            Adding another signal or float number.
        '''
        assert(isinstance(other, (numbers.Real, Signal))), 'TypeError for "+" operands.'

        return self.factor.fillna(0.0) + other.factor.fillna(0.0) if isinstance(other, Signal) else self.factor.fillna(0.0) + other


    def __mul__(self, multiplier):
        '''
        signal value multiplied by a scaler or a 
        '''
        assert(isinstance(multiplier, (numbers.Real, Signal))), 'TypeError for "*" operands.'
        if isinstance(multiplier, numbers.Real):
            return self.factor * multiplier
        elif isinstance(multiplier, Signal):
            return self.factor.mul(multiplier.factor, fill_value=0.0)

    def __rmul__(self, multiplier):
        '''
        signal value multiplied by a scaler or a 
        '''
        assert(isinstance(multiplier, (numbers.Real, Signal))), 'TypeError for "*" operands.'
        if isinstance(multiplier, numbers.Real):
            return self.factor * multiplier
        elif isinstance(multiplier, Signal):
            return self.factor.mul(multiplier.factor, fill_value=0.0)        

    def __truediv__(self, devider):
        '''
        Function:
            Devidef the signal by another signal value or some read numbers
        Input:
            :devider: Signal or Real, the other operands.
        '''
        assert(isinstance(devider, (numbers.Real, Signal))), 'TypeError for "*" operands.'
        if isinstance(devider, numbers.Real):
            return self.factor / devider
        elif isinstance(devider, Signal):
            return self.factor.div(devider.factor, fill_value=0.0)
    def __pow__(self, index):
        '''
        Function:

        '''
        pass
    
    def __hash__():
        '''
        Function:
            Give the hash value of the signal
        '''
        return hash(__class__.__name__)

    def corr(self, ret: pd.DataFrame=pd.DataFrame(), shift:int = 1):
        '''
        Function:
            Check the correl
        '''
        pass

    def group_analysis(self, start:dt.datetime, end:dt.datetime=None,  num: int=5, chg='close', title:str="") -> pd.DataFrame:
        '''
        group analysis of the factor
        :num: number of groups.
        '''
        
        ret = deepcopy(self.data[['secID','tradeDate', 'chgPct']])
        ret = ret.set_index(['tradeDate', 'secID']).unstack()['chgPct'].shift(-1)
        sig_df = self.gen_sig(start=start, end=end)

        cutfactor=sig_df.apply(lambda x:scut(x,num,range(1,num+1)),axis=1)
        result=pd.DataFrame()
        tmpdf_list = []
        result['base']=(ret[~sig_df.isna()]).mean(axis=1, skipna=True)   #sum(axis=1)/(~sig_df.isna()).sum(axis=1)
        for group in range(1,1+num):
            group_return=ret[cutfactor==group].mean(axis=1, skipna=True)   #.sum(axis=1)/(cutfactor==group).sum(axis=1)
            result[group]=group_return.fillna(0.0)
        for column in result.columns:
            backtest_result_dict = {
            'Group': column,
            'Start': '2019-01-01',
            'End'  : '2022-06-30',
            'Total Yield':    gain_total(result[column]),
            'Yield': gain_yearly(result[column]),
            'Sharpe': sharpe(result[column]),
            'Calmar': calmar(result[column]),
            'MDD': maxdd(result[column])}
            tmpdf = pd.DataFrame(backtest_result_dict, index=[0])
            tmpdf_list.append(tmpdf)

        backtest_result_df = pd.concat(tmpdf_list, ignore_index=True)
        backtest_result_df.set_index('Group', inplace=True)
        (result+1).cumprod().plot_bokeh.line(figsize=(800,600), title=title)
        return result

    def IC_IR(self, start:dt.datetime, end:dt.datetime=None) -> pd.DataFrame:
        '''
        Function:
            Calculate the information ratio and information coefficient of 
            the signal for the given time.
        :return: IC for each period and the entire IR.
        '''

        pass


    def longshort_analysis(self, start:dt.datetime, end:dt.datetime=None,  num: int=5,  title: str='') -> pd.DataFrame:
        '''
        Group the bonds according to the signal value, Long the top and Short 
        the lowest level, and get the performance of the portfolio.
        :title: The title of the output form
        :return:  the daily_pnl dataframe.
        '''
        ret = deepcopy(self.data[['secID','tradeDate', 'chgPct']])
        ret = ret.set_index(['tradeDate', 'secID']).unstack()['chgPct'].shift(-1)
        sig_df = self.gen_sig(start=start, end=end)
        cutfactor=sig_df.rank(axis=1).apply(lambda x:scut(x,num,range(1,num+1)),axis=1)
        result=pd.DataFrame()
        long_return=ret[cutfactor==1].mean(axis=1, skipna=True)  
        short_return=ret[cutfactor==num].mean(axis=1, skipna=True) 
        result['long_short']=long_return - short_return 
        result['base'] = (ret[~sig_df.isna()]).mean(axis=1, skipna=True)
        (result+1).cumprod().plot_bokeh(figsize=(800,600), title=title)

        tmpdf_list = []
        for column in result.columns:
            backtest_result_dict = {
            'Group': column,
            'Start': '2019-01-01',
            'End'  : '2022-06-30',
            'Total Yield':    gain_total(result[column]),
            'Yield': gain_yearly(result[column]),
            'Sharpe': sharpe(result[column]),
            'Calmar': calmar(result[column]),
            'MDD': maxdd(result[column])}
            tmpdf = pd.DataFrame(backtest_result_dict, index=[0])
            tmpdf_list.append(tmpdf)

        backtest_result_df = pd.concat(tmpdf_list, ignore_index=True)
        backtest_result_df.set_index('Group', inplace=True)
        display(backtest_result_df)
        return result

    def top_N_portfolio(self, start:dt.datetime, end:dt.datetime=None,  N:int=10, freq:int=1,  title :str='') -> pd.DataFrame:
        '''
        '''
        ret_df = deepcopy(self.data[['secID','tradeDate', 'chgPct']])
        ret_df = ret_df.set_index(['tradeDate', 'secID']).unstack()['chgPct'].shift(-1)

        sig_df = self.gen_sig(start=start, end=end)

        result = calc_pnl(filtTopN(sig_df, N=N), ret_df,  freq=freq)
        ret = pd.DataFrame(result*100, columns=['ret'])
        ret.index = pd.to_datetime(ret.index)
        cum_ret = (1+result).cumprod()
        cum_ret.index = pd.to_datetime(cum_ret.index)
        backtest_result_dict = {
                'Params': 'Value',
                'Start': start,
                'End'  : end,
                'Total Yield':    gain_total(result),
                'Yield': gain_yearly(result),
                'Sharpe': sharpe(result),
                'Calmar': calmar(result),
                'MDD': maxdd(result)}
        df = pd.DataFrame(backtest_result_dict, index=[0])
        df.set_index('Params', inplace=True)
        display(df)
        p = figure(x_range = [dt.datetime(2019,1,1), dt.datetime(2022,6,30)], x_axis_type='datetime', plot_width=1000, plot_height=400, title='30 lowest price bonds')
        source = ColumnDataSource(dict(
                x=cum_ret.index,
                y=cum_ret.values,
                trade_date = cum_ret.index.strftime('%Y-%m-%d'),
        ))

        p_line = p.line(x = 'x', y='y', source=source, line_alpha=0.8, line_color='blue', line_width=2)
        hover_tool = HoverTool(tooltips=[
                ('CumRet', '@y'),
                ('Date', '@trade_date'),
                ], 
                formatters={'$x':'datetime'},
                renderers=[p_line])
        p.tools.append(hover_tool)


        p.yaxis.axis_label = 'cum ret'
        p.axis.axis_label_text_font_size= '15pt'
        # p.title.text_font_size = '15pt'

        p2 = figure(x_range = p.x_range, x_axis_type='datetime', plot_height=200, plot_width=1000)
        positive_ret = ret[ret>=0]
        negative_ret = ret[ret<0]
        source2 = ColumnDataSource(dict(
                x1 = positive_ret.index,
                x2 = negative_ret.index,
                top1 = positive_ret.values,
                top2 = negative_ret.values,
                tradedate1 = positive_ret.index.strftime('%Y-%m-%d'),
                tradedate2 = negative_ret.index.strftime('%Y-%m-%d'),
        ))
        p2.vbar( x= 'x1', top='top1', bottom=0, width=0.5, fill_color="#b3de69", fill_alpha=0.4, source=source2 )
        p2.vbar( x= 'x2', top='top2', bottom=0, width=0.5, fill_color="green" , fill_alpha=0.4, source=source2 )

        p2.xaxis.axis_label = 'Trade Date'
        p2.axis.axis_label_text_font_size= '15pt'
        p2.yaxis.axis_label = 'daily ret'
        show(column([p,p2]))
        return
