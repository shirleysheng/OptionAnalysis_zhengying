#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 14:21:11 2021

@author: shensheng
"""
import numpy as np
from scipy.stats import norm


## bs 公式

def black_S(ot,sp,sk,vol,r,mt,divd):
    if(mt == 0):
        if(ot == 'C'):
            bs_pri = max(0,sk - sp)
        else:
            bs_pri = max(0,sp - sk)
    else:
        d1 = (1.0/(vol * np.sqrt(mt))) * (np.log(sp/sk) + (r-divd + vol*vol/2.0)*mt)
        d2 = d1 - vol * np.sqrt(mt)
        if ot == 'C':
            bs_pri = norm.cdf(d1) * sp * np.exp(-mt*divd) - norm.cdf(d2) * sk * np.exp(-r * mt)
        else:
            bs_pri = norm.cdf(-d2) * sk * np.exp(-r * mt) - norm.cdf(-d1) * sp * np.exp(-mt*divd)
    
    return bs_pri


black_S('put',100,100,0.2,0,1,0)

# =============================================================================
# 
# import matplotlib.pyplot as plt
# S = np.arange(50,200,1)
# #delta call/ put
# bs_put = [0]*len(S)
# bs_2 = [0]*len(S)
# bs_1 = [0]*len(S)
# for i in range(len(S)):
#     bs_put[i] = black_S('put',S[i],100,0.2,0,1,0)
#     bs_2[i] = black_S('put',S[i],90,0.2,0,1,0)
#     bs_1[i] = black_S('put',S[i],70,0.2,0,1,0)
# 
# plt.plot(S,bs_put,'-r')
# plt.plot(S,bs_2,'-b')
# plt.plot(S,bs_1,'-g')  #--------越虚值 delta越小
# #put s0价格上涨 p价格下降   
# #s0下跌 价格上涨 
# 
# bs_call = [0]*len(S)
# for i in range(len(S)):
#     bs_call[i] = black_S('call',S[i],100,0.2,0,1,0)
#     
# plt.plot(S,bs_call)
# 
# #call s0价格上涨 c价格上涨
# =============================================================================
    
    
    
