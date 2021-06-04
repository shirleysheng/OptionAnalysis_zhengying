# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 14:05:07 2021

@author: shen
"""
import datetime
import pandas as pd
import pymysql
import pymssql
import numpy as np
####mssql 
##商品提取数据
product_list = ['V']#['MA','PG','TA','ZC','CF','SR','RM','V','M','PP','L','I','C','AU','CU','ZN','AL','RU']
#郑商所：'MA','TA','ZC','CF','SR','RM'     大连交易所：'PG','V','M','PP','L','I','C' 上交所： 'AU','CU','ZN','AL','RU'
#['etf_510050, 'etf_510300', 'etf_159919', 'index_000300']        sql语句改成 #from %s_option

start_date = datetime.datetime(2021, 1, 1)
end_date = datetime.datetime(2021, 3, 1)

def processor_mssql(df):
    df["systemDate"] = df['systemDate'].astype(str).tolist()
    df.rename(columns={"time":"systemDate"}, inplace=True)  #systemdate 2020-02-24 09:05:00      df["date"] = df["systemdate"].apply(lambda x:x.split(" ")[0]) #date 2020-02-24
    df["day"] = df["systemDate"].apply(lambda x:x.split(" ")[0]) #time 09:05:00 09:10:00  
    df["time"] = df["systemDate"].apply(lambda x:x.split(" ")[1]) #time 09:05:00 09:10:00
        #df["minite"] = df["systemDate"].apply(lambda x:int(x.split(" ")[1].split(":")[1]))#5 10 15...
    return df


def get_eod(df):
   df_eod = df[df["time"]=="14:55:00"].copy()
   df_eod["1d_ret"] = np.log(df_eod["close_adj"]/df_eod["close_adj"].shift(1))
   
   return df_eod

conn_ssql=pymssql.connect(host="192.168.10.6",user="shengshen",password="shengshen",database="Option")  

list_of_dfs = {}
for product in product_list:
    sql = "select systemDate, monthSymbol, monthDueTime, callVolume, putVolume,callPosition,putPosition " \
                 "from %s_future_option where systemDate>='%s' and systemDate<'%s' order by systemDate"%(product,start_date,end_date) #
    ssql_pre = pd.read_sql(sql, conn_ssql)
    mssql_df = processor_mssql(ssql_pre)
    
    list_of_dfs[product] = mssql_df



####  mysql-------------------------------------------------------------------------------------
product_list = ['PP','PG']
start_date = datetime.datetime(2020, 1, 1)
def processor_mysql(df):
    df.rename(columns={"time":"systemdate"}, inplace=True)  #systemdate 2020-02-24 09:05:00
    df["close_adj"] = df["close"] * df["multiplier"]  #multiplier 
    df["date"] = df["systemdate"].apply(lambda x:x.split(" ")[0]) #date 2020-02-24
    df["time"] = df["systemdate"].apply(lambda x:x.split(" ")[1]) #time 09:05:00 09:10:00
    df["minite"] = df["systemdate"].apply(lambda x:int(x.split(" ")[1].split(":")[1]))#5 10 15...
    return df

def end_of_day(df):
    df_5m = df[(df["time"]>"09:35:00") & (df["time"]<="23:00:00")].copy() #去掉开盘第一个时刻
    df_5m = df_5m[df_5m["minite"]%5==0].copy()

    df_eod = df_5m[df_5m["time"]=="14:55:00"].copy()
    df_eod['year'] = df_eod["date"].apply(lambda x:x.split("-")[0])

    return df_eod


list_of_dfs = {}
conn = pymysql.connect("192.168.10.6", "cta-reader", "cta-reader","datacenter_futures")
for product in product_list:
    sql = "select time,close,multiplier,instrumentid from futures_5m_continuing2 where productid='%s' and time>='%s' order by time"%(product, start_date)
    df = pd.read_sql(sql, conn)
    list_of_dfs[product]  = processor_mysql(df)



#realtime 库--------------------------------------------------------------------------------------
conn_ssql=pymssql.connect(host="192.168.10.6",user="shengshen",password="shengshen",database="realtime_data")  
sql_ssql = "select distinct symbol from market where period = '5m'"
all_symbol = pd.read_sql(sql_ssql, conn_ssql)   #['000016.XSHG','000300.XSHG']
list_of_dfs = {}
for symbol in all_symbol:
    sql = "select datetime, symbol, [close], volume from market  where period = '5m' and symbol = '%s' order by datetime"%(symbol)
    list_of_dfs[symbol] = pd.read_sql(sql, conn_ssql)
    