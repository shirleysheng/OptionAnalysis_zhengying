# -*- coding: utf-8 -*-
"""
Created on Mon May 31 14:06:22 2021

@author: shen
"""


import numpy as np
import os
os.chdir(r"C:\Users\shen\Desktop\code\simple statistical analysis")
from bs import black_S


def bisection(f, left, right, tolerance):
    if ( np.sign(f(left)) * np.sign(f(right)) > 0 ):
        return np.nan
    if ( abs(f(left)) < tolerance ):
        return left
    if ( abs(f(right)) < tolerance ):
        return right
    mid = (left + right)/2.0
    while ( abs(f(mid)) > tolerance ):
        if ( np.sign(f(left)) * np.sign(f(mid)) < 0 ):
            right = mid
        else:
            left = mid
        mid = (left + right)/2.0
    return mid

def implied_v(ot,sp,sk,r,mt,left,right,tolerance,option_price):
    def recall(x):
        return black_S(ot,sp,sk,x,r,mt,0) - option_price #regard divid as 0 
    return bisection(recall, left, right, tolerance)





