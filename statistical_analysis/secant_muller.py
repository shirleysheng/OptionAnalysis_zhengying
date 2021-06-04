# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 11:22:38 2021

@author: shen
"""
import numpy as np


#====================================secant method=========================
def secant(fun,x0,x1,tolerance):
    if(abs(fun(x0)) < tolerance):
        return x0
    if (abs(fun(x1)) < tolerance):
        return x1    
    result = x1
    while (abs(fun(result)) > tolerance):
        result = x1 - (x1-x0)*fun(x1)/(fun(x1)-fun(x0))
        x0 = x1
        x1 = result
    return result


#====================================muller method=========================
def muller(func,x0,x1,x2,tolerance):
    def slope(a,b):
        x = (func(b)-func(a))/(b-a)
        return x
    def sl2(a,b,c):
        sl2 = (slope(a,b) - slope(b,c))/(b-c)
        return sl2
    def w(a,b,c):
        w = slope(a,b) + slope(a,c) - slope(b,c)
        return w    
    if(abs(func(x0)) < tolerance):
        return x0
    if(abs(func(x1)) < tolerance):
        return x1
    if(abs(func(x2)) < tolerance):
        return x2
    new = x2
    while (abs(func(new)) > tolerance):
        delta = w(x0,x1,x2) * w(x0,x1,x2) - 4.0*func(x2)*sl2(x0,x1,x2)
        if(delta<0):
            return np.nan
        result1 = 2.0*func(x2)/(w(x0,x1,x2) + math.sqrt(w(x0,x1,x2) * w(x0,x1,x2) - 4.0*func(x2)*sl2(x0,x1,x2)))
        result2 = 2.0*func(x2)/(w(x0,x1,x2) - math.sqrt(w(x0,x1,x2) * w(x0,x1,x2) - 4.0*func(x2)*sl2(x0,x1,x2)))
        if (abs(result1)<abs(result2)):
            new = x2-result1
        else:
            new = x2-result2
        x0 = x1
        x1 = x2
        x2 = new
    return new

