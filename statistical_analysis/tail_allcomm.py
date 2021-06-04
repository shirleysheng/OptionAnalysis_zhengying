# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 17:01:23 2021

@author: shen
"""

import datetime
from datetime import timedelta
import pandas as pd
import numpy as np
import pymysql
import pymssql
import os
import time
from scipy.stats import norm
import matplotlib.pyplot as plt
pd.set_option('display.float_format',lambda x : '%.3f' % x)
os.chdir(r"Z:\SHEN\CostMargin")
from margin import calculate_margin, get_marginfactor


#
product_list = ['PG','V','M','PP','L','I','C']#,'CF','SR','M','C','CU','RU']  #['MA','PG','TA','ZC','CF','SR','RM','V','M','PP','L','I','C','AU','CU','ZN','AL','RU']
#郑商所：'MA','TA','ZC','CF','SR','RM'     大连交易所：'PG','V','M','PP','L','I','C' 上交所： 'AU','CU','ZN','AL','RU'
conn_ssql=pymssql.connect(host="192.168.10.6",user="shengshen",password="shengshen",database="Option")  
Tlist = {}
profit_P_list = {}
profit_C_list = {}
profit_P_adj_list = {}
profit_C_adj_list = {}
#minivlist = {}
targetsimga = 2
minsigma = 1.5
plt.figure()


for product in product_list:
    print(product)
    today = datetime.datetime.today()
    now = (today.replace(today.year,today.month,today.day,21,0,0,0)).strftime('%Y-%m-%d %H:%M:%S')
    #找到距离目前最近的上一时刻
    sql_lasttime = "Select TOP 1 systemDate from %s_future_option_detail " \
                "where SystemDate<='%s' " \
                "and (datepart(hour,Systemdate)*100+datepart(minute,Systemdate) between 905 and 1010 "\
                "or datepart(hour,Systemdate)*100+datepart(minute,Systemdate) between 1035 and 1125 " \
                "or datepart(hour,Systemdate)*100+datepart(minute,Systemdate) between 1335 and 1455 " \
                "or datepart(hour,Systemdate)*100+datepart(minute,Systemdate)<100 " \
                "or datepart(hour,Systemdate)*100+datepart(minute,Systemdate) between 2105 and 2255) order by SystemDate desc"%(product,now) # and halfSpreadIndex is not NULL 流动性指标
    lasttime = pd.read_sql(sql_lasttime, conn_ssql)
    
      #load opt curve
    sql_opt = "Select dueTime*250 as T, StrikePrice as K, forwardprice as F , UnderlyingPrice as S," \
            "(case when StrikePrice>=forwardprice then callmidprice else putmidprice end) as Optprice," \
            "(case when StrikePrice>=forwardprice then callImpv else putImpv end) as OTMIV " \
            " FROM [Option]..[%s_future_option_detail] WHERE SystemDate='%s' " \
            "and (case when StrikePrice>=forwardprice then callAskPrice1-CallBidPrice1 else PutAskPrice1-PutBidPrice1 end)<=20" \
            " order by dueTime,StrikePrice" %(product,lasttime['systemDate'][0])
    opt_data = pd.read_sql(sql_opt,conn_ssql)#得到的是一个品种下 目前时刻所有合约数据
    firstT = np.sort(opt_data['T'].unique())[0] #取最近的时间
    Tlist[product] = firstT
    opt_nearby = opt_data[opt_data['T'] == firstT]  #取最近合约的数据
    opt_nearby['K'] = pd.to_numeric(opt_nearby['K'])
    opt_nearby = opt_nearby.sort_values(by="K")  #按K排序
    minprice = np.min(opt_nearby['Optprice'])#取最小price
    putdata = opt_nearby[opt_nearby['K']< opt_nearby['F']]#将数据分开成call put的虚值数据
    #l_p = len(putdata)
    calldata = opt_nearby[opt_nearby['K'] > opt_nearby['F']]
    #l_c = len(calldata)
    #分别遍历call put数据，去除错误数据
    used_p = 1
    if(len(putdata) > 2):
        for i in range(1,len(putdata))[::-1]:
            if(putdata['Optprice'].iloc[i]<putdata['Optprice'].iloc[i-1]):
                used_p = i
                break
    
    used_c = len(calldata)
    if(len(calldata) > 2):
        for i in range(len(calldata)-1):
            if(calldata['Optprice'].iloc[i] < calldata['Optprice'].iloc[i+1]):
                used_c = i    
                break
    putdata_f = putdata.iloc[used_p:]
    putdata_f = putdata_f[putdata_f['Optprice']>minprice]
    calldata_f = calldata.iloc[:used_c]
    calldata_f = calldata_f[calldata_f['Optprice']>minprice]
    
    whole_data = putdata_f.append(calldata_f)
    whole_data = whole_data[whole_data['OTMIV'] > 0]
    if whole_data.empty == True:
        print(f"{product}_Impv 为 0")
        continue
    else:
        sigmalist = np.log(whole_data['K']/whole_data['F']) / (whole_data['OTMIV'] / np.sqrt(250) *np.sqrt(whole_data['T']))#计算sigma
        ATMIV = float(np.array(whole_data['OTMIV'])[np.where(abs(sigmalist)== min(abs(sigmalist)))])
        
        matchp = np.where(abs(sigmalist + targetsimga) == min(abs(sigmalist + targetsimga))) #离targetsigma最近的位置的put
        matchc = np.where(abs(sigmalist - targetsimga) == min(abs(sigmalist - targetsimga)))
    
        IV_P = float(np.array(whole_data['OTMIV'])[matchp])
        IV_C = float(np.array(whole_data['OTMIV'])[matchc])
        K_P = float(np.array(whole_data['K'])[matchp])
        K_C = float(np.array(whole_data['K'])[matchc])
        price_p = float(np.array(whole_data['Optprice'])[matchp])
        price_c = float(np.array(whole_data['Optprice'])[matchc])
        minprice = min(whole_data['Optprice'])
        minIV = min(whole_data['OTMIV'])  #可删
        maxIV = max(whole_data['OTMIV'])
        S = whole_data['S'].iloc[0]
        T = whole_data['T'].iloc[0]
        
        sigma_p = np.array(sigmalist)[matchp][0]
        sigma_c = np.array(sigmalist)[matchc][0]
        
        plt.plot(sigmalist,whole_data['OTMIV'],linestyle='-',marker='o',markersize = 3,label=f'{product}_ATMIV:{ATMIV}')
        plt.xlabel('sigma')
        plt.ylabel('IV')
        plt.legend(bbox_to_anchor=(1.05, 0), loc=3, borderaxespad=0)


plt.show()    
    
    
    