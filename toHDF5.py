#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 15:11:56 2020

@author: duxing
"""

import pandas as pd

from config import *

# from dateutil.parser import parse
symbol_list = ["btc"]
for symbol in symbol_list:
	new = pd.read_csv("adjusted_BTC_5m.csv")
	# print(df)
	
	# new['ts'] = new["ts"].apply(parse)
	new["ts"] = pd.to_datetime(new["ts"])
	# print(new["ts"])
	new = new.set_index("ts").sort_index()
	# ohlc_dict = {
	#             'Open': 'first',
	#             'High': 'max',
	#             'Low': 'min',
	#             'Close': 'last',
	#             'Vol': 'sum'
	#             }
	# new=dff.resample('24H', how=ohlc_dict, closed='left', label='left')
	new = new.fillna(method='ffill')
	new.rename(columns={"close": "Close", "high": "High", "low": "Low", "open": "Open", "volume": "Volume"},
	           inplace=True)
	
	df = new.resample("15T").last()
	df["Open"] = new.resample("15T").first()["Open"]
	df["High"] = new.resample("15T").max()["High"]
	df["Low"] = new.resample("15T").min()["Low"]
	df["Volume"] = new.resample("15T").sum()["Volume"]
	# yesterday=pd.DataFrame()
	# # LC=new.resample("1D").last()["Close"]
	# yesterday["C"]=new.resample("1D").last()["Close"]
	# LC=yesterday["C"].shift().values
	# # print(LC)
	# yesterday["LC"]=LC
	# yesterday["L"]=new.resample("1D").min()["Low"]
	# LL = yesterday["L"].shift().values
	# yesterday["LL"] = LL
	# yesterday["H"] = new.resample("1D").max()["High"]
	# LH = yesterday["H"].shift().values
	# yesterday["LH"] = LH
	#
	# print(yesterday)
	# print(yesterday.resample("5T").ffill()["LC"])
	# print()
	# df["LC"] = yesterday.resample("5T").ffill()["LC"]
	# df["LL"] = yesterday.resample("5T").ffill()["LL"]
	# df["LH"] = yesterday.resample("5T").ffill()["LH"]
	# df = df.fillna(method='ffill')
	H = df["High"].values
	L = df["Low"].values
	C = df["Close"].shift().values
	temp = pd.DataFrame()
	temp["H-L"] = abs(H - L)
	temp["H-C"] = abs(H - C)
	temp["L-C"] = abs(L - C)
	TR = temp.max(axis=1)
	df["TR"] = TR.values
	period_list = [30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 110, 120, 130, 140,
	               150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900,
	               1000, 1500, 2000, 3000]
	ATR_period = [3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
	for period in period_list:
		df['max_' + str(period)] = df["Close"].rolling(period).max()
		df["min_" + str(period)] = df["Close"].rolling(period).min()
		df["ma_" + str(period)] = df["Close"].rolling(period).mean()
		# df["std_" + str(period)] = df["Close"].rolling(period).std()
	
	for ATR in ATR_period:
		df[timePeriod + "ATR" + str(ATR)] = df["TR"].rolling(ATR).mean()
	# print(df)
	df.to_csv(symbol + "-CQ_15min.csv")
	
	# df.to_hdf(h5_address, key=symbol)
