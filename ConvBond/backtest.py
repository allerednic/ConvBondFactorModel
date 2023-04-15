import time
import os, sys
sys.path.append('/media/Data/Programs/ConvBond')
import utility.utils as utils
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import pdb


def backtest(start_date='20200101', end_date=date.today().strftime('%Y%m%d'), **config):
    
    ### parse extra parameters for backtesting
    initial_cash = config.get('initial_cash', 1000000)
    num_holding_stock = config.get('num_holding_stock', 5)
    holding_days = config.get('holding_days', 1)
    running_days = config.get('running_days', 1)
    commission_rate = config.get('commission_rate', 0.0001)
    
    
    stock     = pd.DataFrame(data=None, index=None, columns=['secID', 'qty', 'cost_price', 'amount', 'pre_close'])
    #### log file for  trading history 
    trade_log = pd.DataFrame(data=None, index=None, columns=['date', 'secID', 'qty', 'price', 'amount', 'profit','cash'])
    #### log file for net value
    stock_log = pd.DataFrame(data=None, index=None, columns=['date', 'stock_amount', 'cash' , 'float_pnl', 'asset', 'float_ret', 'turnover'])
    #### log file for data error
    debug_log = pd.DataFrame(data=None, index=None, columns=['date', 'secID', 'qty', 'price', 'amount', 'profit','cash'])

    # 交易起止日期
    begin = pd.to_datetime(start_date)
    end   = pd.to_datetime(end_date)
    print('Backtest starts from %s, and ends on %s.' % ( start_date , end_date))
    print ('Starting backtest at ' + time.strftime("%Y-%m-%d %H:%M:%S,", time.localtime()))
    cash_in_account = initial_cash ### usable cash left in account
    days = 0
    
    run_date = begin
    pre_asset = initial_cash
    while run_date <= end:
        print('正在计算:', run_date.strftime("%Y-%m-%d") , end = '' )
        print('\r',end='')
        days = days+1  ### 交易天数加1

        # 获取当天转债低溢价因子排名列表
        # 以收盘价格计算  ----这里可能会产生较大的滑点
        cvt_bond_list = utils.get_listed_convbonds(run_date.strftime('%Y%m%d'))
        pdb.set_trace()
        if cvt_bond_list is None:
            # 节假日无可转债数据
            # 当日非交易日，日期加一天
            run_date=run_date + timedelta(days=1)
            # 跳出今日交易
            continue  
            
        cvt_bond_list.sort_values(by='bondPremRatio', ascending=True, inplace=True)
        cvt_bond_list = cvt_bond_list[cvt_bond_list['openPrice'] > 0]
        
        ###
        # tmp_df = cvt_bond_list.iloc[0:2*num_holding_stock].sort_values(by='dl_value', ascending=True)
        # tmp_df = tmp_df
        ###
        
        hold_df          = cvt_bond_list.iloc[0:num_holding_stock]
        
        # 开盘卖出非目标可转债
        traded_cap = 0
        float_pnl = 0
        for code in stock['secID']:
            if code not in list(hold_df['secID']):
                stock_code = code
                cost_price = float(stock[stock['secID']==code]['cost_price'])
                pre_close = float(stock[stock['secID'] == code]['pre_close'])
                stock_qty  = float(stock[stock['secID']==code]['qty'])

                sell_temp  = cvt_bond_list[cvt_bond_list['secID']==code]
                if not sell_temp.empty:
                    sell_price = float(cvt_bond_list[cvt_bond_list['secID']==code]['closePriceBond'])
                else:
                    sell_price = pre_close
                    debug_log.loc[len(debug_log)] =[run_date, stock_code, -1 * stock_qty, sell_price,
                                                 amount, float_pnl, cash_in_account]
                amount =  sell_price * stock_qty * (1-commission_rate)
                #### total sold assets 
                traded_cap += sell_price * stock_qty
                #### total float_pnl for sold assets
                float_pnl += amount - pre_close * stock_qty
                cash_in_account = cash_in_account + amount
                #  删除已经卖出的债券
                stock = stock.drop(stock[stock['secID'] == code].index)
                # 重置持仓索引
                stock = stock.reset_index(drop=True)
                trade_log.loc[len(trade_log)] = [run_date, stock_code, -1 * stock_qty, sell_price,
                                                 amount, float_pnl, cash_in_account]

        # 拟加仓的可转债数量
        buy_num=num_holding_stock-len(stock)
        # 拟购买转债的金额
        if buy_num>0:
            buy_cash= cash_in_account/buy_num
    #         print(buy_cash)
        else:
            buy_cash=0

        # 买入目标可转债并更新持仓股票的每日收盘价
        for code in hold_df['secID']:
            cost_price = float(hold_df[hold_df['secID']==code]['closePriceBond'])
            
            if code not in list(stock['secID']):
                stock_code = code
                # 转债收盘价买入
                stock_qty  = round(buy_cash/cost_price/10,0)*10
                pre_close = cost_price
                amount     = cost_price * stock_qty  * (1+commission_rate)
                float_pnl -= cost_price * stock_qty * commission_rate
                traded_cap += cost_price * stock_qty
                cash_in_account = cash_in_account - amount            

                stock.loc[len(stock)]=[stock_code,stock_qty,cost_price,amount,pre_close]

                # 添加交易记录
                trade_log.loc[len(trade_log)] = [run_date, stock_code, stock_qty * 1, pre_close,
                                                 amount * (-1), float_pnl ,cash_in_account]
            else:
                float_pnl += float(stock[stock['secID']==code]['qty']) * (cost_price - float(stock[stock['secID']==code]['pre_close']) )
                stock[stock['secID']==code]['pre_close'] = cost_price
            
            float_ret = float_pnl / pre_asset
            asset = (stock['qty'] * stock['pre_close']).sum() + cash_in_account
            turn_over = traded_cap / asset
            pre_asset = asset
                

        # 记录每日持仓市值和收益，方便画图
        sum_amount =  round(stock['amount'].sum(), 2)
        stock_log.loc[len(stock_log)] = [run_date, sum_amount, cash_in_account , float_pnl, asset, float_ret, turn_over]
        run_date = run_date + timedelta(days=1)
        
        # run_date += pd.DateOffset(1)
    trade_log.to_csv("trade_log.csv")
    stock_log.to_csv("stock_log.csv")
    debug_log.to_csv("debug_log.csv")
    stock.to_csv("stock.csv")
    print('==============代码运行结束===============')
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    
    # 计算最终持仓市值
    last_amount = round(stock['amount'].sum(), 2)

    profit = round(cash_in_account + last_amount, 2)
    print('总天数:', days)
    print('初始资产:', initial_cash)
    print('最终资产:', profit)
    print('总收益率:%.2f%%' % ((profit - initial_cash) / initial_cash * 100))

    yy = days / 365.0
    year_profit = ((profit / initial_cash) ** (1 / yy) - 1) * 100
    # print(':%.2f%%' % year_profit)

    mdd, mdd_start_date, mdd_end_date = utils.max_drawdown(stock_log)
    print('最大回撤: %.2f%%' %(-100*mdd))
    print('最大回撤起止日期: %s -- %s' %(mdd_start_date.strftime('%Y%m%d'), mdd_end_date.strftime('%Y%m%d')))
    
    # print('夏普比率:%.2f' % utils.sharpe_ratio(stock_log))
    # print('卡尔玛比率:%.2f' % (- year_profit / mdd /100 ))
    sharpe = utils.sharpe_ratio(stock_log)
    calmar = - year_profit / mdd /100
    turnover = stock_log['turnover'].mean()
    
    print ("{:<15} {:<8} {:<8} {:<8} {:<8} {:<15} {:<15}".format( 'annual_ret',  'Sharpe',  'Calmar', 'Turnover',  'MDD', 'MDD_s', 'MDD_e'  ))
    print ("{:<15.2f} {:<8.2f} {:<8.2f} {:<8.2f} {:<8.2f} {:<15} {:<15}".format( year_profit,  sharpe,  calmar, turnover,  mdd, mdd_start_date.strftime('%Y%m%d'), mdd_end_date.strftime('%Y%m%d')  ))

    #设置画布大小,默认画布序号为零
    sns.set_context('paper')
    sns.set_style('whitegrid')
    fig, ax= plt.subplots(figsize=(15, 7))
    ax.plot(stock_log['date'], stock_log['asset']/initial_cash -1)
    ax.tick_params(labelsize=14)
    ax.set_xlabel('date', fontsize=16)
    ax.set_ylabel('yield', fontsize=16)
    ax.set_title('PremBondRatio', fontsize=16)
    plt.show()
    return (stock, stock_log)


if __name__ == '__main__':
    config = {'initial_cash': 1000000, 'num_holding_stock':5, 'commission_rate':0.0003}
    stock, stock_log = backtest(start_date='20190101', end_date='20210331', **config)