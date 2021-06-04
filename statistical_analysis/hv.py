# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 14:05:09 2021

@author: shen
"""
import datetime

product_list = ['PP']
start_date = str((datetime.datetime.today() - datetime.timedelta(days=1)).date())

"""
1.5min 滚动
2.1d HV
"""
#HV
import pandas as pd
import numpy as np
import pymysql
import pymssql
import os
import time
from scipy.stats import norm
import matplotlib.pyplot as plt
pd.set_option('display.float_format',lambda x : '%.3f' % x)

trading_day = 252


conn_ssql=pymssql.connect(host="192.168.10.6",user="shengshen",password="shengshen",database="Option")  
for product in product_list:
    sql_ssql = "select systemDate, monthSymbol, underlyingPrice " \
                "from %s_future_option where systemDate>='%s' order by systemDate"%(product,start_date) # and halfSpreadIndex is not NULL 流动性指标
    ssql_pre = pd.read_sql(sql_ssql, conn_ssql)






