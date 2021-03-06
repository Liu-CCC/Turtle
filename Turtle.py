#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 01:04:58 2020

@author: Liu-CCC
"""

import datetime

import pandas as pd

import TradeSimulation
from config import *

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

# period_list = [50, 55, 60, 65, 70, 75, 80, 85]
# period_list = [90, 95, 100, 110, 120, 130, 140, 150]
period_list = [160, 170, 180, 190, 200, 210, 220, 230]
# period_list=[240, 250, 300, 350, 400, 450, 500, 600]
# period_list=[700, 800, 900, 1000, 1500, 2000, 3000]
# period_list = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
# period_list = [2,3,4,5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
ATR_period = [3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]

Stop = [0.5, 1, 1.5, 2, 2.5, 3]
# N_list = [0.05, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5,0.6]
# N_list= [0.7,0.8, 0.9, 1, 1.1, 1.2,1.3, 1.4]
N_list = [1.5, 1.6, 1.7, 1.8, 1.9, 2, 2.5]

# N_list = [0.5,1,1.5,2,2.5]
# M_list = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
h5 = pd.HDFStore(h5_address)
print(u"生成交易列表")
Time1 = datetime.datetime.now()
# print(h5, h5.items())
df = h5[symbol]
TradeList = pd.DataFrame(
		columns=[TRDLIST_NO, TRDLIST_ITEM, TRDLIST_INTIME, TRDLIST_OUTTIME, TRDLIST_TIMEFRAME, TRDLIST_STRATEGY,
		         TRDLIST_SIGNAL, TRDLIST_INPRICE, TRDLIST_OUTPRICE, TRDLIST_PAIRSITEM, TRDLIST_PAIRSPOSRATIO,
		         TRDLIST_PAIRSMARKNUM, TRDLIST_PAIRSAB])
Trade = {}
df["state"] = 0
df["stop"] = 0
TS = df.index.values
C = df["Close"].values
# OPEN1 = df["Open"].shift().values
# C1 = df["Close"].shift().values

# LC = df["LC"].values
# LL = df["LL"].values
# LH = df["LH"].values
# ATR = df[timePeriod + "ATR" + str(ATR_period)].values

for period in period_list:
	for N in N_list:
		for ATR_window in ATR_period:
			for stop_N in Stop:
				# OS=LH+N*(LC-LL)
				# OB=LL-N*(LH-LC)
				ATR = df[timePeriod + "ATR" + str(ATR_window)].values
				UP = df["max_" + str(period)].shift().values
				# print(UP)
				DOWN = df["min_" + str(period)].shift().values
				# print(DOWN)
				# print(C)
				# UP=MAX+N*ATR
				# DOWN=MIN-N*ATR
				STATE = df["state"].values
				STOP = df["stop"].values
				# ATR = df[timePeriod + "ATR" + str(ATR_window)].values
				# STD = df["std_" + str(open_window)].values
				temp = []
				
				row = 0
				for i in range(len(C)):
					if i == 0:
						# print(UP[i] + N * ATR[i],C[i],DOWN[i] - N * ATR[i])
						if C[i] > UP[i] + N * ATR[i]:
							STATE[i] = 2
							STOP[i] = C[i] - stop_N * ATR[i]
						if C[i] < DOWN[i] - N * ATR[i]:
							STATE[i] = -2
							STOP[i] = C[i] + stop_N * ATR[i]
					else:
						STATE[i] = STATE[i - 1]
						STOP[i] = STOP[i - 1]
						# print(UP[i] + N * ATR[i], C[i], DOWN[i] - N * ATR[i])
						if STATE[i] == 2:
							STOP[i] = max(C[i] - stop_N * ATR[i], STOP[i])
							if C[i] < STOP[i]:
								STATE[i] = 0
						elif STATE[i] == -2:
							STOP[i] = min(C[i] + stop_N * ATR[i], STOP[i])
							if C[i] > STOP[i]:
								STATE[i] = 0
						if STATE[i] == 0:
							if C[i] > UP[i] + N * ATR[i]:
								STATE[i] = 2
								STOP[i] = C[i] - stop_N * ATR[i]
							elif C[i] < DOWN[i] - N * ATR[i]:
								STATE[i] = -2
								STOP[i] = C[i] + stop_N * ATR[i]
						if STATE[i - 1] != STATE[i]:
							if STATE[i - 1] == 0:
								Trade = {}
								row += 1
								Trade[TRDLIST_NO] = row
								Trade[TRDLIST_ITEM] = symbol
								Trade[TRDLIST_INTIME] = TS[i]
								Trade[TRDLIST_TIMEFRAME] = timePeriod
								Trade[TRDLIST_STRATEGY] = arrStrategy
								Trade[TRDLIST_INPRICE] = C[i]
								if STATE[i] == 2:
									Trade[TRDLIST_SIGNAL] = "buy"
								elif STATE[i] == -2:
									Trade[TRDLIST_SIGNAL] = "sell"
								temp.append(Trade)
							elif STATE[i] == 0:
								temp[row - 1][TRDLIST_OUTTIME] = TS[i]
								temp[row - 1][TRDLIST_OUTPRICE] = C[i]
							elif STATE[i - 1] != 0 and STATE[i] != 0:
								Trade = {}
								row += 1
								Trade[TRDLIST_NO] = row
								Trade[TRDLIST_ITEM] = symbol
								Trade[TRDLIST_INTIME] = TS[i]
								Trade[TRDLIST_TIMEFRAME] = timePeriod
								Trade[TRDLIST_STRATEGY] = arrStrategy
								Trade[TRDLIST_INPRICE] = C[i]
								if STATE[i] == 2:
									Trade[TRDLIST_SIGNAL] = "buy"
								elif STATE[i] == -2:
									Trade[TRDLIST_SIGNAL] = "sell"
								temp.append(Trade)
								temp[-2][TRDLIST_OUTTIME] = TS[i]
								temp[-2][TRDLIST_OUTPRICE] = C[i]
				# print(temp[-1])
				if len(temp) > 5 and TRDLIST_OUTTIME not in temp[-1].keys():
					temp[-1][TRDLIST_OUTTIME] = TS[-1]
					temp[-1][TRDLIST_OUTPRICE] = C[-1]
				# df["state"] = STATE
				# df["stop"] = STOP
				TradeList = pd.DataFrame(data=temp, index=range(len(temp)),
				                         columns=[TRDLIST_NO, TRDLIST_ITEM, TRDLIST_INTIME, TRDLIST_OUTTIME,
				                                  TRDLIST_TIMEFRAME,
				                                  TRDLIST_STRATEGY, TRDLIST_SIGNAL, TRDLIST_INPRICE,
				                                  TRDLIST_OUTPRICE,
				                                  TRDLIST_PAIRSITEM, TRDLIST_PAIRSPOSRATIO, TRDLIST_PAIRSMARKNUM,
				                                  TRDLIST_PAIRSAB])
				# print (TradeList)
				if len(TradeList) > 10:
					# df.to_csv(arrStrategy + "_15.csv")
					# tradelistfile = "/Users/duxing/PycharmProjects/backtester_only_for_contract/BOLL/" + symbol + "_" + arrStrategy + "(" + str(
					# 		open_window) + "+" + str(N) + "," + str(
					# 		ATR_window) + "," + str(
					# 		stop_N) + ")_TradeList.xlsx"  # str型，交易列表地址
					tradelistfile = "/Users/duxing/PycharmProjects/backtester_only_for_contract/results/" + arrStrategy + "/" + timePeriod + "/" + symbol + "_" + arrStrategy + "(" + str(
							period) + "," + str(N) + "," + str(ATR_window) + "," + str(
							stop_N) + ")_TradeList.xlsx"  # str型，交易列表地址
					TradeList.to_excel(tradelistfile, sheet_name=u"交易列表")
					
					Time2 = datetime.datetime.now()
					print(u'生成交易列表完成。用时：', Time2 - Time1)
					# TradeList=pd.read_excel(tradelistfile, sheet_name=u"交易列表")
					
					TradeSimulation.TradeSimMain(df, TradeList, tradelistfile)
Time2 = datetime.datetime.now()
print(u"全部完成，用时：", Time2 - Time1)
