# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 10:29:53 2021

@author: shen
"""

import pandas as pd
import numpy as np
import os
os.chdir("C:/Users/shen/Desktop/code/爬虫")
from margin import calculate_margin, get_marginfactor
import re
import datetime
from datetime import timedelta
import pymysql
import pymssql
pd.set_option('mode.chained_assignment', None)
os.chdir(r"Z:\SHEN\CostMargin\ErrorReport")

underlying_settle = {'50':3.471,'300':5.098}
accountlist = ['001080006976','0185666077089','0158120302706','0185666077111','011380006795'] #0185666077111
#find last workday
def prev_weekday(adate):
    adate -= timedelta(days=1)
    while adate.weekday() > 4: # Mon-Fri are 0-4
        adate -= timedelta(days=1)
    return adate
#now = datetime.datetime.today()+ timedelta(-3)
today = prev_weekday(datetime.datetime.today()).strftime('%Y-%m-%d')
margin_result = pd.ExcelWriter(f'margin_{today}.xlsx')#,engine='openpyxl')
cost_result = pd.ExcelWriter(f'cost_{today}.xlsx')
conn = pymysql.connect("192.168.10.6", "cta-reader", "cta-reader","datacenter_futures")
conn_ssql=pymssql.connect(host="192.168.10.6",user="shengshen",password="shengshen",database="realtime_data")  
cost_record = pd.read_excel(r'Z:\SHEN\CostMargin\Record\cost_summary.xlsx')



for account in accountlist:
    #read cost excel
    columns = ['合约','symbol','期权类型','执行价','买/卖','权利金单价','成交量','权利金','是否备兑','手续费','保证金','编码']
    os.chdir(r"Z:\SHEN\CostMargin")
    data = pd.read_excel(f'Z:/SHEN/CostMargin/{account}_{today}.xls',names = columns)
    cost_start = data[data['合约'] == '品种合约'].index[0]
    data_temp = data[cost_start:]
    cost_end = data_temp[data_temp['合约'] == '合计'].index[0]
    cost_data = data[cost_start+1:cost_end].reset_index(drop = True)
    #cost_data['cost_today'] = round(cost_data['手续费'].astype(float)/cost_data['成交量'].astype(float),2)
    cost_data['cost_today'] = [round(cost_data['手续费'][i]/cost_data['成交量'][i],2) for i in range(len(cost_data))]
    cost_data = cost_data[cost_data['cost_today'] !=0].reset_index(drop = True)#DROP BUY 
    cost_data['Product'] = [re.findall('[a-zA-Z]+|\d+',cost_data['symbol'][i])[0] for i in range(len(cost_data))]
    cost_today = cost_data.drop_duplicates(subset=['Product']).reset_index(drop = True)#drop duplicate
    cost_today = cost_today[['symbol','cost_today','Product']]
    
    productlilst = ["M","I","RU","C","SR",
        "CF","CU","TA","MA","AU",
        "RM","PG","ZC","PP","V",
        "L","AL","ZN","IO"]
    
    cost_standard = cost_record[['Product',account]]
    
    result = pd.merge(cost_today,cost_standard, on = 'Product')
    error_cost = result[result['cost_today'] != result[account]]
    #print(result)
    if(error_cost.empty == True):
            print(f"{account} cost 无误")
    else:
        print(f"{account}: \n"
              f"{error_cost}")                 
    #write multi dataframe into one excel
        error_cost.to_excel(excel_writer=cost_result,sheet_name=f'{account}')

    
    
    #get margin data
    margin_start = data[data['合约'] == '期权持仓汇总'].index[0]
    
    margin_temp = data[margin_start:]
    margin_end = margin_temp[margin_temp['合约'] == '合计'].index[0]
    
    margin_data = data[margin_start+2:margin_end].reset_index(drop = True)
    new_col = ['品种合约','symbol','期权类型','执行价','买持仓','买均价','卖持仓','卖均价','昨结算价','今结算价','交易保证金','id']
    margin_data.columns = new_col
    margin_data = margin_data.dropna(subset=['卖持仓']).reset_index(drop = True)
    margin_data['Product'] = [re.findall('[a-zA-Z]+|\d+',margin_data['symbol'][i])[0] for i in range(len(margin_data))]
    #margin_data = margin_data[~margin_data.Product.isin(['50','300'])].reset_index(drop = True) #去除50 300 etf数据
    margin_data.loc[margin_data.期权类型 == '看跌期权', 'type'] = 0
    margin_data.loc[margin_data.期权类型 == '看涨期权', 'type'] = 1
    margin_today = margin_data[['品种合约','Product','卖持仓','交易保证金']].copy()
    margin_today['official'] = margin_today['交易保证金']/margin_today['卖持仓']
    margin_today['formula'] = 0.0*len(margin_today)

    
    id_mysql = np.sort(margin_data["symbol"].unique()).tolist()
    #处理郑商所id
    margin_data['id_match'] = [0]*len(margin_data)
    for i in range(len(margin_data)):
        if (margin_data['Product'][i] in ['MA','TA','ZC','CF','RM','SR']):
            temp = re.findall('[a-zA-Z]+|\d+',margin_data['symbol'][i])[1]
            margin_data['id_match'][i] = margin_data['Product'][i] + '2' + temp
        else:
            margin_data['id_match'][i] = margin_data['symbol'][i]


    for i in range(len(margin_today)):
        
        if margin_data['Product'][i] != "50" and margin_data['Product'][i] != "300":
            mysql = "select Settle from futures_eod_patch where InstrumentID = '%s' order by Time DESC LIMIT 1"%(margin_data['id_match'][i])
            settle_data = pd.read_sql(mysql, conn)
            S = float(settle_data.iloc[0])
        elif margin_data['Product'][i] == "50":
            mssql = "SELECT Top 1 [close] FROM [realtime_data].[dbo].[market_daily] where Symbol='510050.xshg' order by Datetime desc"
            #settle_data = pd.read_sql(mssql, conn_ssql)   #['000016.XSHG','000300.XSHG']
            S = underlying_settle[margin_data['Product'][i]]
        elif margin_data['Product'][i] == "300":
            mssql = "SELECT Top 1 [close] FROM [realtime_data].[dbo].[market_daily] where Symbol='510300.xshg' order by Datetime desc"
            #settle_data = pd.read_sql(mssql, conn_ssql)
            S = underlying_settle[margin_data['Product'][i]]
        else:
            mssql = "SELECT Top 1 [close] FROM [realtime_data].[dbo].[market_daily] where Symbol='000300.XSHG' order by Datetime desc"
            settle_data = pd.read_sql(mssql, conn_ssql)
    
            S = float(settle_data.iloc[0])
        #S = float(settle_data.iloc[0])
        #S = underlying_settle[margin_data['Product'][i]]
        K = margin_data['执行价'][i]
        PC = margin_data['type'][i]
        optprice = margin_data['今结算价'][i]
        margin_today.loc[:,'formula'][i]  = calculate_margin(margin_data['Product'][i],S,K,PC,optprice)
        
    error_margin = margin_today[abs(margin_today['official'] - margin_today['formula']) > 0.1]
    error_margin['diff'] = abs(error_margin['official'] - error_margin['formula'])
    
    SumOfficial = pd.DataFrame({'option_off':margin_today.groupby('Product')['交易保证金'].apply(lambda x: sum(x))})
    SumFormula = pd.DataFrame({'option_for':margin_today.groupby('Product').apply(lambda x: x['formula'].dot(x['卖持仓']))})
    #print(error_margin)   
    if(error_margin.empty == True):
            print(f"{account} margin 无误")
    else:
        error_margin.to_excel(margin_result, sheet_name=f'{account}')


    #calculate futures margin
    
    if '期货持仓汇总' in data['合约'].values:
        future_start = data[data['合约'] == '期货持仓汇总'].index[0]
        future_temp = data[future_start:]
        future_end = future_temp[future_temp['合约'] == '合计'].index[0]
        
        future_data = data[future_start+2:future_end].reset_index(drop = True)
        new_col = ['symbol','买持仓','买均价','卖持仓','卖均价','昨结算价','今结算价','浮动盈亏','Official','投机/套保','Formula','Product']
        future_data.columns = new_col
        future_data['Product'] =  [re.findall('[a-zA-Z]+|\d+',future_data['symbol'][i])[0] for i in range(len(future_data))]
        
        for i in range(len(future_data)):
            size = get_marginfactor(future_data['Product'][i])[2]
            factor = get_marginfactor(future_data['Product'][i])[0]
            future_data['Formula'][i] = future_data['买持仓'][i] * future_data['今结算价'][i] * size * factor
        
        future_margin = future_data[['symbol','今结算价','Official','Formula']]
        future_data.to_excel(margin_result,startcol=10,sheet_name=f'{account}')    
        
        total_margin = future_data.merge(SumOfficial, on = 'Product', how='outer').copy()
        total_margin = total_margin.merge(SumFormula, on = 'Product',how='outer')
        total_margin = total_margin.fillna(0)
        
        #split future include and exclude
        future_include = total_margin[total_margin['symbol'] != 0]
        future_exclude = total_margin[total_margin['symbol'] == 0]
        future_include_error = future_include[future_include['Formula'] + future_include['option_for'] < 
                                              future_include['Official'] + future_include['option_off']]
        future_exclude_error = future_exclude[round(future_exclude['option_for'],2) != round(future_exclude['option_off'],2)]
        total_error = future_include_error.append(future_exclude_error)
        
    else:
        total_error = error_margin.copy()
    
    if(total_error.empty == True):
        print(f"{account} margin 无误")
    else:
        print(f"{account} \033[1;41m margin error \033[0m") #change the color
        total_error.to_excel(margin_result, startrow = len(error_margin)+4,sheet_name=f'{account}')
        
    
    
    print("-----------------------------------------------------------------")
#cost_result.save()
#cost_result.close()   # workbook.create_sheet（str）##
 
margin_result.save()
margin_result.close()
    
    



