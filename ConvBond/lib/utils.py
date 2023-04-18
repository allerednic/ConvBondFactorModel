# -*- coding: utf-8 -*-
'''
Utility function:
    author: cs-yang
    date:   2022-08-07
'''
import numpy as np
import pandas as pd
import pandas_bokeh
import seaborn as sns
import matplotlib.pyplot as plt
from typing import List

def Singleton(cls):
    _instances = {}  
    def getinstance(*args, **kwargs):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]
    return getinstance

def filtTopQuantile(factor: pd.DataFrame,q: float=0.5) ->pd.DataFrame:
    return factor.apply(lambda x:x<=x.quantile(q) ,axis=1)

def merge_force_suffix(left, right, **kwargs):
    '''
    Function:
        Merge two dataframes where the column name suffix is forced
    '''
    on_col = kwargs['on']
    suffix_tupple = kwargs['suffixes']

    def suffix_col(col, suffix):
        if col != on_col:
            return str(col) + suffix
        else:
            return col

    left_suffixed = left.rename(columns=lambda x: suffix_col(x, suffix_tupple[0]))
    right_suffixed = right.rename(columns=lambda x: suffix_col(x, suffix_tupple[1]))
    del kwargs['suffixes']
    return pd.merge(left_suffixed, right_suffixed, **kwargs)


# 取排名最小的N个标的，用bool值表示
def filtTopN(factor: pd.DataFrame, N: int=20)->pd.DataFrame:
    return factor.apply(lambda x:x.rank(method='first')<=N,axis=1)

def action_above_k(factor: pd.DataFrame,N: int,k: float):
    def calc_numpy(matrix,N,k):
        holding=[]
        signal=np.zeros_like(matrix)
        for i in range(matrix.shape[0]):
            row=matrix[i]
            _N=min(len(row)-np.isnan(row).sum(),N)
            row[holding]=row[holding] - k
            holding=row.argsort()[:_N]
            signal[i][holding]=1
        return signal
    signal=calc_numpy(factor.copy().to_numpy(),N,k)
    return pd.DataFrame(signal,index=factor.index,columns=factor.columns).astype(bool)


maxdd = lambda pnl: (1-(1+pnl).cumprod()/(1+pnl).cumprod().expanding().max()).max()
sharpe=lambda pnl:(pnl.mean() / pnl.std()) * (243**0.5)
gain_total=lambda pnl:(1+pnl).prod()-1
gain_yearly=lambda pnl:(1+pnl).prod()**(243/len(pnl))-1
calmar=lambda pnl:gain_yearly(pnl)/maxdd(pnl)

def scut(row: pd.Series, num: int=5, groups:List[int]=[i for i in range(1,6)]) -> pd.Series:
    '''
    Function:
        Self defined cut function.
    Input:
        :row: pd.Series, the value to be cut,
        :num: int, the number of groups,
    Output:
        :groups: pd.Series, the grouped
    '''

    assert(len(groups) == num), 'The symbols are not matched'
    result = pd.Series(data=np.nan, index=row.index)
    ranked = row.rank(method='first')
    length = len(ranked[~ranked.isna()]) // num
    residue = len(ranked[~ranked.isna()]) % num
    edge = 0
    bins = [edge]
    if  length > 0:
        for i in range(num):
            edge += length + 1 if residue > 0 else length
            bins.append(edge)
            residue -= 1
        result = pd.cut(ranked, bins, labels=groups)
    return result
    