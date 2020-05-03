# encoding: UTF-8

'''
本文件仅用于存放对于事件类型常量的定义。

由于python中不存在真正的常量概念，因此选择使用全大写的变量名来代替常量。
这里设计的命名规则以EVENT_前缀开头。

常量的内容通常选择一个能够代表真实意义的字符串（便于理解）。

建议将所有的常量定义放在该文件中，便于检查是否存在重复的现象。
'''
import pandas as pd
import numpy as np
import datetime
import os
from numba import jit
from scipy import stats
# import matplotlib.pyplot as plt  #画图用的，太慢

# SetupFile = '/Users/duxing/Desktop/交易系统开发/BackTester/TradeSim/TradeSim_Setup_v5.5.xlsx'                        #str型，结算时需要的各种设置

# Excel页名
EXCEL_SETUPSHEET = u'设置页'
EXCEL_ITEMINFOSHEET = u'单品种信息'
EXCEL_TIMEFRAMEINFOSHEET = u'周期信息'

#Excel设置页
EXCEL_SETUP = u'设置项'
EXCEL_VALUE = u'数值'
EXCEL_TRADELISTFILE = u'交易列表地址'
EXCEL_BALANCE = u'初始权益'
EXCEL_MAXTOTALMARGIN = u'最大保证金'
EXCEL_TRADESIMPERIOD = u'结算周期'
EXCEL_SAVEMODE = u'保存模式'
EXCEL_RESUMMARY = u'反向结算'
EXCEL_DATABASETYPE = u'数据库类型'
EXCEL_H5FILE = u'H5数据库地址'
EXCEL_SQLSERVER = u'SQL服务器地址'
EXCEL_SQLFUTURE = u'期货数据库'

#Excel保存模式
EXCEL_SIMPLE = u'简洁版'
EXCEL_DETAIL = u'详细版'
EXCEL_OLD = u'旧版'

#Excel策略头寸信息页
EXCEL_STRATEGY = u'交易系统'
EXCEL_MANAGEMODE = u'头寸管理'
EXCEL_SAMEATR = u'等ATR头寸'
EXCEL_SAMEPROPORTION = u'等比例头寸'
EXCEL_PAIRSPOSRATIO = u'配对手数比'
EXCEL_PAIRSSAMETON = u'配对等吨数'
EXCEL_REVERSEATR = u'反转ATR'
EXCEL_RISKMODE = u'风险模型'
EXCEL_TRADESIMATR = u'结算ATR'

#风险模型
RM_INANDOUT = u'双向调整'
RM_ONLYIN = u'向上调整'
RM_ONLYOUT = u'向下调整'

#Excel单品种信息页
EXCEL_ITEM = u'品种'
EXCEL_TYPE = u'类型'
EXCEL_ISPREADNUM = u'结算价差'
EXCEL_MULTICONFEE = u'结算手续费倍数'
EXCEL_CLOSETODAY = u'手续费平今'
EXCEL_CONFEE = u'Commission'
EXCEL_CONFEETODAY = u'CloseToday'
EXCEL_TPH = u'Contract Size'
EXCEL_MINMOVE = u'MinMove'
EXCEL_MARGIN = u'Margin'
EXCEL_RATIO = u'AdjustNumProduct'

#交易列表文件中 保存交易列表的sheet名
TRDLIST_TRDLIST = u'交易列表'
TRDLIST_TRDLIST3 = u'交易列表3'

#交易列表1表头
TRDLIST_NO = u'交易列表汇总'
TRDLIST_ITEM = u'品种'
TRDLIST_INTIME = u'开仓时间'
TRDLIST_OUTTIME = u'平仓时间'
TRDLIST_TIMEFRAME = u'交易周期'
TRDLIST_STRATEGY = u'交易系统'
TRDLIST_SIGNAL = u'买/卖'
TRDLIST_INPRICE = u'开仓价格'
TRDLIST_OUTPRICE = u'平仓价格'
TRDLIST_PAIRSITEM = u'配对名'
TRDLIST_PAIRSPOSRATIO = u'头寸比'
TRDLIST_PAIRSMARKNUM = u'识别码'
TRDLIST_PAIRSAB = u'配对位置'

#交易列表3表头
TRDLIST_TIME = u'时间'
TRDLIST_HOLDDAY = u'持仓长度'
TRDLIST_PRICE = u'价格'
TRDLIST_POS = u'手数'
TRDLIST_CONFEE = u'手续费'
TRDLIST_RETURN0 = u'盈亏'
TRDLIST_RRETURN = u'R比'
TRDLIST_R2RETURN = u'单笔盈亏'
TRDLIST_OPENBALANCE = u'开仓时权益'
TRDLIST_OPENPRICE = u'开仓价格'

#权益表表头
TRDLIST_BALANCE = u'权益'
TRDLIST_BALANCEDAY = u'权益Day'
TRDLIST_MARGIN = u'保证金'
TRDLIST_NETMARGIN = u'轧差保证金'
TRDLIST_WITHDRAW = u'回撤'
TRDLIST_DISTOP = u'高点间隔'
TRDLIST_LEN = u'长度'

#汇总页面
TRDLIST_ITEM = u'品种'
TRDLIST_TOTALTRADE = u'交易数量'
TRDLIST_ODDS = u'胜率'
TRDLIST_AVGRETURN = u'平均盈利'
TRDLIST_AVGLOSS = u'平均亏损'
TRDLIST_R = u'R'
TRDLIST_R2 = u'R2'
TRDLIST_TOTALWIN = u'盈利交易'
TRDLIST_TOTALLOSS = u'亏损交易'

TRDLIST_TOTAL = u'汇总'
TRDLIST_START = u'期初权益'
TRDLIST_END = u'期末权益'
TRDLIST_MAXTOTALMARGIN = u'持仓上限'
TRDLIST_SYS1RISKPERATR = u'系统1_每ATR风险'
TRDLIST_SYS2RISKPERATR = u'系统2_每ATR风险'
TRDLIST_SYS3RISKPERATR = u'系统3_每ATR风险'
TRDLIST_MAXMARGIN = u'持仓比例_最大值'
TRDLIST_TRADETIMEFRAME = u'交易周期'
TRDLIST_RETURN = u'收益率'
TRDLIST_RETURNPERYEAR = u'年化收益率'
TRDLIST_MONRETURN = u'收益一元线性回归'
TRDLIST_MAXWITHDRAWDATE = u'最大回撤_周期_日期'
TRDLIST_MAXWITHDRAW = u'最大回撤_周期_比例'
TRDLIST_MAXWITHDRAWSINGLEDATE = u'最大回撤_分笔_日期'
TRDLIST_MAXWITHDRAWSINGLE = u'最大回撤_分笔_比例'
TRDLIST_TOTALSIGNAL = u'信号次数'
TRDLIST_TOTALTRADE = u'交易次数'
TRDLIST_DISTOP = u'回撤天数_最大值'
TRDLIST_DISTOPDATE = u'最大高点间隔日期'
TRDLIST_MAXCONLOSS = u'最大连续亏损次数'
TRDLIST_MAXSINGLELOSS = u'最大单笔亏损'
TRDLIST_AVGSINGLELOSS = u'平均单笔亏损'
TRDLIST_MAXSINGLEWIN = u'最大单笔盈利'
TRDLIST_AVGSINGLEWIN = u'平均单笔盈利'
TRDLIST_RW = u'Rw'
TRDLIST_R2W = u'R2w'
TRDLIST_TOTALWITHDRAW = u'回撤次数'
TRDLIST_AVGWITHDRAW = u'回撤均值'
TRDLIST_STDWITHDRAW = u'回撤标准差'
TRDLIST_AVG2STD = u'回撤avg+2*std'
TRDLIST_PAVG2STD = u'P/(回撤avg+2*std)'
TRDLIST_GEOAVGRETURN = u'几何平均收益'
TRDLIST_PMD2B = u'P/MD2b'
TRDLIST_AVGCONWITHDRAWDAY = u'连续回撤天数_平均值'
TRDLIST_STDCONWITHDRAWDAY = u'连续回撤天数_标准差'
TRDLIST_MAXCONRISEDAY = u'连续上涨天数_最大值'
TRDLIST_AVGCONRISEDAY = u'连续上涨天数_平均值'
TRDLIST_STDCONRISEDAY = u'连续上涨天数_标准差'
TRDLIST_AVGWITHDRAWDAY = u'回撤天数_平均值'
TRDLIST_STDWITHDRAWDAY = u'回撤天数_标准差'
# TRDLIST_AVGMARGIN = u'持仓均值'
TRDLIST_STDMARGIN = u'持仓标准差'
TRDLIST_REPLACETRADE = u'被替换的交易数'
TRDLIST_MAXCONWITHDRAWDAY = u'连续回撤天数_最大值'
TRDLIST_CONFEEBOOKRETURN = u'手续费/净利润'
TRDLIST_SYS4RISKPERATR = u'系统4_每ATR风险'
TRDLIST_SYS5RISKPERATR = u'系统5_每ATR风险'
TRDLIST_SYS6RISKPERATR = u'系统6_每ATR风险'
TRDLIST_OVERRISKABANDONED = u'风险过大而放弃'
TRDLIST_OVERMARGINABANDONED = u'超持仓比例而放弃'
TRDLIST_AVGMARGINWIN = u'盈利交易平均持仓'
TRDLIST_PMD = u'P/MD'
TRDLIST_AVGMARGIN = u'持仓均值'
TRDLIST_AVGHOLD = u'平均持仓'
