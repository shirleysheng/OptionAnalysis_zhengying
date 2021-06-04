# -*- coding: utf-8 -*-
"""
Created on Fri May 28 10:37:00 2021

@author: shen
"""

import datetime
import pandas as pd
import numpy as np
import pymssql
import os
import re
os.chdir(r"C:\Users\shen\Desktop\code\simple statistical analysis")
from implied_vol import implied_v
from datetime import timedelta


path = r"Z:\SHEN\DailyReport"
dirs = os.listdir(path)
columns = ['contract','direction','price','nums','cost','time','code1','code2']
all_trades = pd.DataFrame()
for file in dirs:
    if 'trades' in os.path.splitext(file)[0]:
        date = os.path.splitext(file)[0].split("_")[0]
        temp_trades = pd.read_csv(f"Z:/SHEN/DailyReport/{file}",encoding='gbk')
        temp_trades['date'] = date
        all_trades = all_trades.append(temp_trades)

all_trades = all_trades.reset_index(drop = True)
#drop future data and buy data   
all_contract = all_trades['成交合约']
contract_length = [len(re.findall('[a-zA-Z]+|\d+',all_trades['成交合约'][i])) for i in range(len(all_trades))]
all_trades['len'] = contract_length
all_trades = all_trades[all_trades['len'] == 4].reset_index(drop = True)
#re.findall('[\u4e00-\u9fa5]',all_trades['买卖'][0])
all_trades = all_trades[all_trades['买卖'] == '\u3000卖'].reset_index(drop = True)

#get detail trade info
all_symbol = [re.findall('[a-zA-Z]+|\d+',all_trades['成交合约'][i])[0] + re.findall('[a-zA-Z]+|\d+',all_trades['成交合约'][i])[1] 
              for i in range(len(all_trades))]        
all_trades['symbol'] = all_symbol
all_strike = [re.findall('[a-zA-Z]+|\d+',all_trades['成交合约'][i])[3] for i in range(len(all_trades))]
all_type = [re.findall('[a-zA-Z]+|\d+',all_trades['成交合约'][i])[2] for i in range(len(all_trades))]        
all_trades['strike'] = all_strike
all_trades['type'] = all_type
#all_trades['成交时间'] = [datetime.datetime.strptime(all_trades['成交时间'][i], "%H:%M:%S").strftime("%H:%M:%S") for i in range(len(all_trades))]
all_trades['成交时间']  = pd.to_datetime(all_trades['成交时间']).dt.time

def prev_weekday(adate):
    adate -= timedelta(days=1)
    while adate.weekday() > 4: # Mon-Fri are 0-4
        adate -= timedelta(days=1)
    return adate

for i in range(len(all_trades)):
    print(i)
    if all_trades['成交时间'][i] < datetime.time(21,00,00):
        all_trades['date'][i] = datetime.datetime.strptime(all_trades['date'][i], "%Y%m%d").strftime("%Y-%m-%d")+ " "+ all_trades['成交时间'][i]
    else:
        all_trades['date'][i] = (prev_weekday(datetime.datetime.strptime(all_trades['date'][i], "%Y%m%d"))).strftime("%Y-%m-%d")+ " "+ all_trades['成交时间'][i]
                              
all_trades['product'] = [re.findall('[a-zA-Z]+|\d+',all_trades['symbol'][i])[0] for i in range(len(all_trades))]
#date --- datetime + time
pd.to_datetime
#
conn_ssql=pymssql.connect(host="192.168.10.6",user="shengshen",password="shengshen",database="realtime_data")  
sql_data = pd.DataFrame()

for i in range(len(all_trades)):
    if all_trades['product'][i] == 'IO':
        sql_ssql =  "select top 1 systemDate, monthSymbol, dueTime, underlyingPrice from [Option].[dbo].[index_000300_option_detail]" \
                    " where systemDate<='%s' and monthSymbol = '000300.SH-%s' and strikePrice = '%s'" \
                    " order by systemDate desc"%(all_trades['date'][i],
                                                 re.findall('[a-zA-Z]+|\d+',all_trades['symbol'][i])[1],all_trades['strike'][i]) #
                    
    else:
        sql_ssql = "select top 1 systemDate, monthSymbol, dueTime, underlyingPrice from [Option].[dbo].[%s_future_option_detail]" \
                    " where systemDate<='%s' and monthSymbol = '%s' and strikePrice = '%s'" \
                    " order by systemDate desc"%(all_trades['product'][i],all_trades['date'][i],
                                            all_trades['symbol'][i],all_trades['strike'][i]) #
    temp_sql = pd.read_sql(sql_ssql, conn_ssql)
    sql_data = sql_data.append(temp_sql)

whole_data = pd.concat([sql_data.reset_index(drop = True),all_trades.iloc[:,[9,3,4,5,12,13,14]]],axis = 1)
whole_data = whole_data[whole_data['dueTime'] < 30/250] #drop close trade
whole_data.rename(columns={"成交价格":"cost","手数":"pos","手续费":"commission"}, inplace=True)
whole_data['strike'] = whole_data['strike'].astype(float)
whole_data['OTM'] = whole_data['strike']/whole_data['underlyingPrice']-1
whole_data = whole_data[abs(whole_data['OTM']) >0.03].reset_index(drop = True)
whole_data['IV'] = [0.0] * len(whole_data)
for i in range(len(whole_data)):
    print(i)
    whole_data['IV'][i] = implied_v(whole_data['type'][i],whole_data['underlyingPrice'][i],whole_data['strike'][i],
                                    0,whole_data['dueTime'][i],100,0.001,0.0001,whole_data['cost'][i])
    
whole_data['sigma'] = np.log(whole_data['strike']/whole_data['underlyingPrice']) / (whole_data['IV'] *np.sqrt(whole_data['dueTime']))

whole_data = whole_data.sort_values(by="systemDate")  #按K排序

path = r'C:/Users/shen/Desktop'
os.chdir(path)
whole_data.to_excel("trade_record.xlsx")






