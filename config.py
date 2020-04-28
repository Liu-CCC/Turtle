#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 17:44:12 2020

@author: LC
"""
# open_window = 1000
# stop_N = 1.5
# ATR_window = 50
# N = 1.5
h5_address = "adjusted_BTC_15M_new.h5"
symbol = "btc"
timePeriod = "15M"
# timePeriod = "DAY"
arrStrategy = "Turtle"  # str型，交易系统

# tradelistfile = symbol + "_" + arrStrategy + "(" + str(open_window) + "+" + str(N) + "," + str(ATR_window) + "," + str(
# 		stop_N) + ")_TradeList.xlsx"  # str型，交易列表地址
# tradelistfile="BTC_CQ_60min_370.xlsx"
StartBalance = 100  # int型，账户初始权益
MaxTotalMargin = 1  # float型，账户最大持仓上限
arrSamePROPORTION = 0.5  # float型，等ATR头寸

# ==========================读取结算设置文件中的信息==========================
iSpreadNum = 0  # float型，结算价差
MultiConFee = 1  # float型，结算手续费倍数
MinMove = 1  # MinMove
TPH = 100  # 合约面值
ConFee = 0.002  # 手续费
MarginRatio = 1  # 杠杆倍数
