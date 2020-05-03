#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 17:44:12 2020

@author: LC
"""

import config
# from TradeSim_ClassITS import *
# from TradeSim_ClassServerDB import *
# from TradeSim_ClassTradeSim import *
from Summary import *
# from TradeSim_Constant import *
from TradeSim_Constant import *


class classItem(object):
	
	# 初始化
	def __init__(self, tradesim1, Name, h5):
		# 传入参数：结算设置文件,品种
		
		# 该品种的基本信息
		self.Name = Name  # str型，品种名
		
		# ==========================读取结算设置文件中的信息==========================
		self.iSpreadNum = 0  # float型，结算价差
		self.MultiConFee = 1  # float型，结算手续费倍数
		self.CloseToday = 0  # Boolean型，平今手续费
		
		Data = h5  # df型，从数据库读取数据全部数据
		#		print(Data)
		# 把Item的数据，转成np.array
		# print(type(Data.index.values),Data.index.values)
		self.arrDateTime = Data.index.values.astype(np.int64)  # 日期时间
		# print(self.arrDateTime)
		self.arrClose = Data['Close'].values  # 收盘价
		self.arrMinMove = np.array([1] * len(Data))  # MinMove
		self.arrTPH = np.array([config.TPH] * len(Data))  # 每手吨
		self.arrConFee = np.array([config.ConFee] * len(Data))  # 手续费
		# print(self.arrConFee)
		self.arrConFeeToday = np.array([0] * len(Data))  # 平今手续费
		self.arrMarginRatio = np.array([config.MarginRatio] * len(Data))  # 保证金
		
		self.Data = Data
		self.rRow = 0  # 已经遍历的数据位置


# 策略周期类，例如TG1H的资金管理
class classTS(object):
	# 初始化
	# sjr,这里的变量名应该叫StrategyName
	def __init__(self, tradesim1, Name):
		# 传入参数：结算的对象，Strategy_Info页的第i行
		
		tem = Name.split(' ')  # ['15M','TG']
		self.TimeFrame = tem[0]  # 周期
		self.Strategy = tem[1]  # 策略
		
		if self.Strategy not in tradesim1.arrStrategy:
			print(self.Strategy + u' 策略头寸不存在！')
		for i in range(len(tradesim1.arrStrategy)):  # 遍历交易系统
			if tradesim1.arrStrategy[i] == self.Strategy:
				break
		
		self.ManageMode = tradesim1.arrManageMode  # str型，资金管理方式
		self.Ratio = tradesim1.arrSamePROPORTION  # float型，当前资金管理方式的数值


# ITS类，记录每个合约+周期+策略
class classITS(object):
	
	# 初始化
	def __init__(self, tradesim1, Name, objItem, objTS, ):
		self.Item = objItem  # obj型，传入合约的对象
		self.TS = objTS  # obj型，传入周期+策略的对象
		# 多单持仓部分
		self.LongOpenPrice = {}  # dict型，开仓价格
		self.LongOpenTime = {}  # dict型，开仓时间
		self.LongOpenBalance = {}  # dict型，开仓权益
		self.LongPos = {}  # dict型，持多单手数
		self.LongUsedMargin = {}  # dict型，已占用保证金
		self.LongLastPrice = {}  # dict型，上结算周期价格
		# 空单持仓部分
		self.ShortOpenPrice = {}  # dict型，开仓价格
		self.ShortOpenTime = {}  # dict型，开仓时间
		self.ShortOpenBalance = {}  # dict型，开仓权益
		self.ShortPos = {}  # dict型，持空单手数
		self.ShortUsedMargin = {}  # dict型，已占用保证金
		self.ShortLastPrice = {}  # dict型，上结算周期价格


def SearchDate(arr, rRow, Time):
	for i in range(rRow, len(arr)):
		if arr[i] >= Time:  # 将品种数据位置，更新到Time时间
			break
	return i


# 品种类
class classTradeSim(object):
	
	# 初始化
	def __init__(self, TradeList, tradelistfile):
		# 传入参数：结算设置文件地址
		# ==========================读取结算设置文件中的信息==========================
		# SetupSheet = pd.read_excel(SetupFile, EXCEL_SETUPSHEET, index_col=0)  # df型，设置页，A列为索引，第1行为表头
		self.TradeListFile = tradelistfile  # str型，交易列表地址
		# self.SummaryFile = SummaryFile
		self.Col = [TRDLIST_NO, TRDLIST_ITEM, TRDLIST_TIME, TRDLIST_TIMEFRAME, TRDLIST_STRATEGY, TRDLIST_HOLDDAY,
		            TRDLIST_SIGNAL, TRDLIST_PRICE, TRDLIST_POS, TRDLIST_CONFEE, TRDLIST_RETURN0, TRDLIST_RRETURN,
		            TRDLIST_R2RETURN, TRDLIST_OPENBALANCE, TRDLIST_OPENPRICE, '-', '--', TRDLIST_PAIRSITEM,
		            TRDLIST_PAIRSPOSRATIO, TRDLIST_PAIRSMARKNUM, TRDLIST_PAIRSAB, '---', '----', '-----']
		self.TradeList3 = pd.DataFrame(columns=self.Col)  # df型，按开仓时间列升序排序
		# self.ItemInfoSheet = pd.read_excel(ccc, EXCEL_ITEMINFOSHEET, index_col=0)  # df型，品种页，A列为索引，第1行为表头
		# self.TimeFrameInfoSheet = pd.read_excel(SetupFile, EXCEL_TIMEFRAMEINFOSHEET)  # df型，周期页
		self.StartBalance = config.StartBalance  # int型，账户初始权益
		self.MaxTotalMargin = config.MaxTotalMargin  # float型，账户最大持仓上限
		self.SaveMode = EXCEL_OLD  # str型，保存模式
		self.ReSummary = False  # Boolean型，反向结算
		TradeSim_Period = config.timePeriod  # str型，指定结算周期
		
		self.Balance = self.StartBalance  # int型，账户权益
		self.MaxBalance = self.StartBalance  # int型，账户高点权益
		self.TotalMargin = 0  # int型，账户持仓比例
		self.TotalNetMargin = 0  # int型，账户持仓比例，轧差
		
		self.arrStrategy = config.arrStrategy  # str型，交易系统
		self.arrManageMode = EXCEL_SAMEPROPORTION  # str型，头寸管理方式
		self.arrSamePROPORTION = config.arrSamePROPORTION  # float型，等比例头寸
		self.arrRiskMode = "None"  # str型，风险模型
		
		# ==========================读取交易列表文件中的信息==========================
		# 判断 传入的参数
		Time1 = datetime.datetime.now()
		
		self.TradeSheet = TradeList  # df型，交易列表页
		Time2 = datetime.datetime.now()
		#		print(self.TradeListFile)
		# print(u'读取交易列表，用时：', Time2 - Time1)
		
		# 交易列表行列
		self.MaxRow = len(self.TradeSheet.index)  # int型，交易列表页最大行
		self.MaxCol = len(self.TradeSheet.columns)  # int型，交易列表页最大列
		
		# ser前缀是pandas.Series类型的意思
		serItem = self.TradeSheet[TRDLIST_ITEM]  # ser型，统计交易列表内有交易的合约
		serTimeFrame = self.TradeSheet[TRDLIST_TIMEFRAME]  # ser型，统计交易列表内有交易的周期
		serStrategy = self.TradeSheet[TRDLIST_STRATEGY]  # ser型，统计交易列表内有交易的策略
		
		# 统计交易列表内的全部ITS
		# ITS名字，用空格做分隔符
		serTS = serTimeFrame + ' ' + serStrategy  # ser型，统计交易列表内有交易的策略+周期
		serITS = serItem + ' ' + serTimeFrame + ' ' + serStrategy  # ser型，统计交易列表内有交易的的合约+周期+策略
		
		self.arrItemName = serItem.drop_duplicates().values  # arr型，self.serItemNameList去重
		self.arrTSName = serTS.drop_duplicates().values  # arr型，self.serTSNameList去重
		self.arrITSName = serITS.drop_duplicates().values  # arr型，self.ITSList去重
		
		# ============================创建TradeList3==================================
		Time1 = datetime.datetime.now()
		self.CreateTradeList3()  # 交易列表3，新格式的交易列表
		Time2 = datetime.datetime.now()
		# print(u'转交易列表3。用时：', Time2 - Time1)
		
		self.arrTL3No = self.TradeList3[TRDLIST_NO].values  # 交易编号
		self.arrTL3Time = self.TradeList3[TRDLIST_TIME].values.astype(np.int64)  # 时间
		self.arrTL3Time2 = np.array(self.TradeList3[TRDLIST_TIME].tolist())  # 时间
		self.arrTL3Signal = self.TradeList3[TRDLIST_SIGNAL].values  # 方向
		self.arrTL3Price = self.TradeList3[TRDLIST_PRICE].values  # 价格
		self.arrTL3Pos = self.TradeList3[TRDLIST_POS].values  # 手数
		self.arrTL3ITS = self.TradeList3['ITS'].values  # ITS
		
		self.TL3_Len = len(self.TradeList3)
		
		self.arrTL3HoldDay = np.array([0.] * self.TL3_Len)
		self.arrTL3Confee = np.array([0.] * self.TL3_Len)
		self.arrTL3Return0 = np.array([0.] * self.TL3_Len)
		self.arrTL3RReturn = np.array([0.] * self.TL3_Len)
		self.arrTL3R2Return = np.array([0.] * self.TL3_Len)
		self.arrTL3OpenBalance = np.array([0.] * self.TL3_Len)
		self.arrTL3OpenPrice = np.array([0.] * self.TL3_Len)
		
		self.listBalance = []
		self.listTotalMargin = []
		self.listTotalNetMargin = []
		self.listWithDraw = []  # list型，权益表中的权益、保证金、轧差保证金、回撤
		
		# ============================结束============================================
		
		dtFirstDate = pd.to_datetime(self.arrTL3Time[0]).date()  # dt64型，第一笔交易的日期时间
		# print (dtFirstDate, type(dtFirstDate))
		dtLastDate = pd.to_datetime(self.arrTL3Time[-1]).date()  # dt64型，最后一笔交易的日期时间
		Days = dtFirstDate  # dt64型，第一笔交易的日期
		
		# serStrTimeList = "23:59:59"  # ser型，TimFrame_Info页中，最小周期各个时间点存入Ser型的数组
		
		# 循环，在第一笔交易日和最后一笔交易日之间，每一日+每一时间点(时间列表)，存入TimeList中
		TimeList = []
		# TradeSim_Period == "DAY":
		while Days <= dtLastDate:  # dt64型
			Days += datetime.timedelta(days=1)
			TimeList.append(str(Days))
		# elif TradeSim_Period[-3:] == "min":
		# 	while Days <= dtLastDate:  # dt64型
		# 		Days += datetime.timedelta(minutes=60)
		# 		TimeList.append(str(Days))
		self.arrDtTime = pd.to_datetime(TimeList).values.astype(np.int64)  # arr型，df时间列表[日期+时间]
		
		# 其他参数
		self.WithDraw = 0  # float型，账户回撤
	
	# ============================================================================
	# 交易列表3，改变交易列表格式，每1行表示1个交易动作，1开1平写成2行
	def CreateTradeList3(self):
		# 交易列表内的交易，拆分，存入self.TradeList3中
		InTradeList = self.TradeSheet.copy()  # df型，复制交易列表
		InTradeList['Mark'] = pd.Series(1, index=InTradeList.index)  # 开仓交易，编号1
		OutTradeList = self.TradeSheet.copy()  # df型，复制交易列表
		if self.ReSummary:  # 反向结算
			InTradeList = InTradeList.replace('buy', 'short')  # 信号buy改为short
			InTradeList = InTradeList.replace('sell', 'buy')  # sell改buy
			OutTradeList = OutTradeList.replace('buy', 'cover')  # 信号buy改为short改为cover
		else:  # 正向结算
			InTradeList = InTradeList.replace('sell', 'short')  # 信号sell改为short
			OutTradeList = OutTradeList.replace('sell', 'cover')  # 信号sell改为cover
			OutTradeList = OutTradeList.replace('buy', 'sell')  # 信号buy改为sell
		OutTradeList[TRDLIST_INTIME] = OutTradeList[TRDLIST_OUTTIME]  # 开仓时间改为平仓时间
		OutTradeList[TRDLIST_INPRICE] = OutTradeList[TRDLIST_OUTPRICE]  # 开仓价格改为平仓价格
		OutTradeList['Mark'] = pd.Series(2, index=OutTradeList.index)  # 平仓交易，编号2
		TradeList3 = InTradeList.append(OutTradeList)  # df型，合成后的TradeList3
		TradeList3 = TradeList3.sort_values([TRDLIST_INTIME, 'Mark'])  # 按开仓时间升序、编号升序排序，默认 kind=quicksort
		TradeList3 = TradeList3.drop(TRDLIST_OUTTIME, axis=1)
		TradeList3 = TradeList3.drop(TRDLIST_OUTPRICE, axis=1)
		TradeList3 = TradeList3.drop('Mark', axis=1)  # 删除序号列 和 平仓时间列 和 平仓价格 和 编号
		self.TradeList3[TRDLIST_NO] = TradeList3[TRDLIST_NO]
		self.TradeList3[TRDLIST_ITEM] = TradeList3[TRDLIST_ITEM]
		self.TradeList3[TRDLIST_TIME] = TradeList3[TRDLIST_INTIME]
		self.TradeList3[TRDLIST_TIMEFRAME] = TradeList3[TRDLIST_TIMEFRAME]
		self.TradeList3[TRDLIST_STRATEGY] = TradeList3[TRDLIST_STRATEGY]
		self.TradeList3[TRDLIST_SIGNAL] = TradeList3[TRDLIST_SIGNAL]
		self.TradeList3[TRDLIST_PAIRSMARKNUM] = TradeList3[TRDLIST_PAIRSMARKNUM]
		self.TradeList3[TRDLIST_PRICE] = TradeList3[TRDLIST_INPRICE]
		self.TradeList3[TRDLIST_PAIRSAB] = TradeList3[TRDLIST_PAIRSAB]
		
		self.TradeList3[TRDLIST_TIME] = pd.to_datetime(self.TradeList3[TRDLIST_TIME])  # 'Time'时间列，改为dt64型
		self.TradeList3['ITS'] = np.nan  # 增加ITS列
	
	# ============================================================================
	# 将ITSP插入TradeList3中相应的位置
	def InsertITStoTradeList3(self, ITS):
		# 将ITSP填入TradeList3中
		# 找相同的品种、周期、策略
		cond1 = self.TradeList3[TRDLIST_ITEM] == ITS.Item.Name  # bool型
		cond2 = self.TradeList3[TRDLIST_TIMEFRAME] == ITS.TS.TimeFrame  # bool型
		cond3 = self.TradeList3[TRDLIST_STRATEGY] == ITS.TS.Strategy  # bool型
		tem = self.TradeList3[(cond1 == True) & (cond2 == True) & (cond3 == True)]  # df型
		self.TradeList3.loc[tem.index, 'ITS'] = ITS
		self.arrTL3ITS = self.TradeList3['ITS'].values
	
	# ============================================================================
	# 对一笔持仓结算，权益变化
	def SettlementCurTime(self, Time, ITS):
		# 传入参数：ITS
		try:
			ITS.Item.rRow = SearchDate(ITS.Item.arrDateTime, ITS.Item.rRow + 1, Time) - 1
		except:
			pass
		
		Close = ITS.Item.arrClose[ITS.Item.rRow]  # 当前周期价格
		TPH = ITS.Item.arrTPH[ITS.Item.rRow]
		MarginRatio = ITS.Item.arrMarginRatio[ITS.Item.rRow]
		# if side == "long":
		# 	asset = (1 / price["open"] - 1 / price["close"]) * pos * self.symbol_value
		# elif side == "short":
		# 	asset = (1 / price["close"] - 1 / price["open"]) * pos * self.symbol_value
		if ITS.LongPos != {}:
			for i in ITS.LongPos.keys():
				LongProfit = MarginRatio * (
						(1 / ITS.LongLastPrice[i] - 1 / Close) * TPH * ITS.LongPos[i])  # 截止当前周期的多单总盈利
				# LongProfit = (Close - ITS.LongLastPrice[i]) * TPH * ITS.LongPos[i]  # 截止当前周期的多单总盈利
				self.Balance = self.Balance + LongProfit  # 账户权益变化
				ITS.LongLastPrice[i] = Close
		
		if ITS.ShortPos != {}:
			for i in ITS.ShortPos.keys():
				ShortProfit = MarginRatio * (
						(1 / ITS.ShortLastPrice[i] - 1 / Close) * TPH * ITS.ShortPos[i])  # 截止当前周期的多单总盈利
				# ShortProfit = (Close - ITS.ShortLastPrice[i]) * TPH * ITS.ShortPos[i]  # 截止当前周期的空单总盈利
				self.Balance = self.Balance + ShortProfit  # 账户权益变化
				ITS.ShortLastPrice[i] = Close
	
	# ============================================================================
	# 对总体交易结算，持仓比例的变化
	def Total(self, Time):
		
		if self.Balance > self.MaxBalance:
			self.MaxBalance = self.Balance  # 账户高点权益
		self.WithDraw = round(1 - float(self.Balance) / self.MaxBalance, 4)  # 账户回撤，加入float有小数，python中整数/整数=整数
		
		self.listBalance.append(self.Balance)
		self.listTotalMargin.append(self.TotalMargin)
		self.listTotalNetMargin.append(abs(self.TotalNetMargin))
		self.listWithDraw.append(self.WithDraw)
	
	# ============================================================================
	# 风险管理
	def RiskM(self, ITS, i, ITSList):
		# 传入参数：Its，当前判断的周期Time
		try:
			result = ITS.TS.RiskMode(ITS, self.arrDtTime[i], self.Balance, ITSList)  # ITS持仓过风险模型
		except:
			return  # 如果ITS没有指定风险模型，则返回
		
		if result:  # 如果，风险模型返回了新交易，存在result中
			for l in result:  # 遍历 result中的每一笔交易，list型
				dfRiskModeTrade = pd.DataFrame(l).T  # 转成df型
				dfRiskModeTrade.columns = self.Col[0:len(l)]  # 表头 = 交易列表3的表头
				dfRiskModeTrade['ITS'] = ITS  # 加入ITSP列
				self.TradeList3 = self.TradeList3.append(dfRiskModeTrade, ignore_index=True)  # 整合进原先交易列表3中
			
			for k in range(self.TL3_Len, len(self.TradeList3)):  # 遍历原交易列表3长度以后的交易，即新整合进的交易
				self.FixPos(k, ITSList)  # 改持仓，算收益
	
	# ============================================================================
	# 有交易，修改持仓
	def FixPos(self, k, ITSList):
		# 传入参数：Trade,Its_List
		#       表头 = [TRDLIST_NO,TRDLIST_ITEM,TRDLIST_TIME,TRDLIST_TIMEFRAME,TRDLIST_STRATEGY,TRDLIST_HOLDDAY,TRDLIST_SIGNAL,TRDLIST_PRICE,TRDLIST_POS,TRDLIST_CONFEE,
		#              TRDLIST_RETURN0,TRDLIST_RRETURN,TRDLIST_R2RETURN,TRDLIST_OPENBALANCE,TRDLIST_OPENPRICE,'-','--',TRDLIST_PAIRSITEM,TRDLIST_PAIRSPOSRATIO,
		#              TRDLIST_PAIRSMARKNUM,TRDLIST_PAIRSAB]                        #品种
		
		No = self.arrTL3No[k]  # int型，交易编号
		Time = self.arrTL3Time[k]  # dt64型，时间
		Signal = self.arrTL3Signal[k]  # str型，方向
		Price = self.arrTL3Price[k]  # float型，价格
		Pos = self.arrTL3Pos[k]  # int型，手数
		ITS = self.arrTL3ITS[k]  # obj型，ITS
		#		print("ITS.Item.arrDateTime",ITS.Item.arrDateTime,"ITS.Item.rRow",ITS.Item.rRow,"Time",Time)
		ITS.Item.rRow = SearchDate(ITS.Item.arrDateTime, ITS.Item.rRow, Time)  # 将品种数据位置，更新到Time时间
		#		print("ITS.Item.arrMinMove",ITS.Item.arrMinMove)
		MinMove = ITS.Item.arrMinMove[ITS.Item.rRow]  # float型，MinMove
		TPH = ITS.Item.arrTPH[ITS.Item.rRow]  # float型，每手吨
		Fee = ITS.Item.arrConFee[ITS.Item.rRow]  # float型，手续费
		ConFeeToday = ITS.Item.arrConFeeToday[ITS.Item.rRow]  # float型，平今手续费
		MarginRatio = ITS.Item.arrMarginRatio[ITS.Item.rRow]  # float型，保证金
		iSpreadNum = ITS.Item.iSpreadNum  # 结算价差
		MultiConFee = ITS.Item.MultiConFee  # 手续费倍数
		
		if Signal == 'buy':
			if pd.isnull(Pos):  # 开多单
				Pos = self.CalHold(k, ITS)  # int型，计算手数
			# print("POSSL", Pos)
			ITS.LongOpenTime[No] = self.arrTL3Time2[k]
			ITS.LongOpenBalance[No] = self.Balance
			ITS.LongOpenPrice[No] = Price
			try:
				ITS.LongPos[No] += Pos
			except:
				ITS.LongPos[No] = Pos
			ITS.LongLastPrice[No] = Price
		elif Signal == 'short':
			if pd.isnull(Pos):  # 开空单
				Pos = -self.CalHold(k, ITS)  # 计算手数
			# print("POSSS", Pos)
			ITS.ShortOpenTime[No] = self.arrTL3Time2[k]
			ITS.ShortOpenBalance[No] = self.Balance
			ITS.ShortOpenPrice[No] = Price
			try:
				ITS.ShortPos[No] += Pos
			except:
				ITS.ShortPos[No] = Pos
			
			ITS.ShortLastPrice[No] = Price
		elif Signal == 'sell':  # 平多单
			if pd.isnull(Pos):
				Pos = ITS.LongPos[No]  # 平仓手数
			OpenTime = ITS.LongOpenTime[No]  # dt64型，开仓时间
			OpenPrice = ITS.LongOpenPrice[No]  # float型，开仓价格
			OpenBalance = ITS.LongOpenBalance[No]  # float型，开仓时的权益
			ITS.LongPos[No] -= Pos  # int型，剩余持仓
		
		elif Signal == 'cover':  # 平空单
			if pd.isnull(Pos):
				Pos = ITS.ShortPos[No]  # 平仓手数
			OpenTime = ITS.ShortOpenTime[No]  # dt64型，开仓时间
			OpenPrice = ITS.ShortOpenPrice[No]  # float型，开仓价格
			OpenBalance = ITS.ShortOpenBalance[No]  # float型，开仓时的权益
			ITS.ShortPos[No] -= Pos  # int型，剩余持仓
		
		if Signal == 'buy' or Signal == 'short':  # 开仓，计手续费
			self.arrTL3Pos[k] = Pos  # 交易手数
			self.arrTL3OpenBalance[k] = self.Balance  # 开仓权益
			self.arrTL3OpenPrice[k] = Price  # 开仓价格
		
		elif Signal == 'sell' or Signal == 'cover':  # 平仓，计手续费、计价差
			# 判断 如果平仓日期 = 开仓日期，则平仓部分的手续费按平今手续费计算
			# (成交合约张数 * 合约面值 / 成交均价) * 费率
			ConFee = MultiConFee * (Fee * (TPH * (1 / Price + 1 / OpenPrice)) * abs(Pos))  # 手续费=手续费倍数*（手续费*手数）
			# print(ConFee, MultiConFee ,Fee, Price, OpenPrice, abs(Pos))
			iSpreadNumFee = iSpreadNum * MinMove * TPH * abs(Pos)  # 价差费用=价差*MinMove*TPH*手数
			# （1/持仓均价 - 1/平仓成交均价）* 平多仓合约张数 * 合约面值
			TotalProfit = MarginRatio * ((1 / OpenPrice - 1 / Price) * TPH * Pos - ConFee - iSpreadNumFee)  # 这笔交易的盈利
			
			self.arrTL3Pos[k] = Pos  # 交易手数
			self.arrTL3HoldDay[k] = (self.arrTL3Time2[k] - OpenTime).days  # 持仓天数
			self.arrTL3Confee[k] = ConFee  # 手续费，开仓的手续费也算到平仓这笔交易中
			self.arrTL3Return0[k] = TotalProfit  # 收益
			self.arrTL3RReturn[k] = float(TotalProfit) / OpenBalance  # 总盈利%=总盈利/开仓时权益
			self.arrTL3OpenBalance[k] = OpenBalance  # 开仓权益
			self.arrTL3OpenPrice[k] = OpenPrice  # 开仓价格
			
			if Signal == 'sell':
				self.arrTL3R2Return[k] = float((Price - OpenPrice)) / float(OpenPrice)  # R2=(平-开)/开
				Profit = MarginRatio * ((1 / ITS.LongLastPrice[No] - 1 / Price) * TPH * Pos)  # 当前周期的盈利
			else:
				self.arrTL3R2Return[k] = -1 * float((Price - OpenPrice)) / float(OpenPrice)  # R2=(平-开)/开
				Profit = MarginRatio * ((1 / ITS.ShortLastPrice[No] - 1 / Price) * TPH * Pos)  # 当前周期的盈利
			self.Balance = self.Balance + Profit - ConFee - iSpreadNumFee  # 平仓后，减去价差和手续费
		
		try:
			if ITS.LongPos[No] != 0:  # 有多单持仓
				if Signal == 'buy' or Signal == 'sell':
					# 持仓保证金=（合约面值*持仓合约数量）/最新成交价/杠杆倍数
					Margin = (TPH * abs(ITS.LongPos[No]) / Price / MarginRatio) / self.Balance
					# Margin = Price * abs(ITS.LongPos[No]) * MarginRatio * TPH / self.Balance  # 持仓比例=价格*手数*保证金*每手吨/总权益
					try:
						self.TotalMargin = round(self.TotalMargin - ITS.LongUsedMargin[No] + Margin,
						                         4)  # 账户持仓比例=持仓比例-上周期已用持仓比例+当前周期持仓比例
						self.TotalNetMargin = round(self.TotalNetMargin - ITS.LongUsedMargin[No] + Margin, 4)  # 轧差
					except:
						self.TotalMargin = round(self.TotalMargin + Margin, 4)  # 账户持仓比例=持仓比例+当前周期持仓比例
						self.TotalNetMargin = round(self.TotalNetMargin + Margin, 4)  # 轧差
					ITS.LongUsedMargin[No] = Margin  # 记录当前周期的已用持仓比例
			else:
				self.TotalMargin = round(self.TotalMargin - ITS.LongUsedMargin[No], 4)  # 账户持仓比例=持仓比例-上周期已用持仓比例
				self.TotalNetMargin = round(self.TotalNetMargin - ITS.LongUsedMargin[No], 4)  # 轧差
				ITS.LongUsedMargin[No] = 0  # 记录当前周期的已用持仓比例
				ITS.LongPos.pop(No)
		except:
			pass
		
		try:
			if ITS.ShortPos[No] != 0:  # 有空单持仓
				if Signal == 'short' or Signal == 'cover':
					Margin = (TPH * abs(ITS.LongPos[No]) / Price / MarginRatio) / self.Balance
					# Margin = Price * abs(ITS.ShortPos[No]) * MarginRatio * TPH / self.Balance  # 持仓比例=价格*手数*保证金*每手吨/总权益
					try:
						self.TotalMargin = round(self.TotalMargin - ITS.ShortUsedMargin[No] + Margin,
						                         4)  # 账户持仓比例=持仓比例-上周期已用持仓比例+当前周期持仓比例
						self.TotalNetMargin = round(self.TotalNetMargin + ITS.ShortUsedMargin[No] - Margin, 4)  # 轧差
					except:
						self.TotalMargin = round(self.TotalMargin + Margin, 4)  # 账户持仓比例=持仓比例+当前周期持仓比例
						self.TotalNetMargin = round(self.TotalNetMargin - Margin, 4)  # 轧差
					ITS.ShortUsedMargin[No] = Margin  # 记录当前周期的已用持仓比例
			else:
				self.TotalMargin = round(self.TotalMargin - ITS.ShortUsedMargin[No], 4)  # 账户持仓比例=持仓比例-上周期已用持仓比例
				self.TotalNetMargin = round(self.TotalNetMargin + ITS.ShortUsedMargin[No], 4)  # 轧差
				ITS.ShortUsedMargin[No] = 0  # 记录当前周期的已用持仓比例
				ITS.ShortPos.pop(No)
		except:
			pass
	
	# ============================================================================
	# 计算开仓手数
	def CalHold(self, i, ITS):
		# 传入参数：TradeList3中的第i笔交易，Its，ItsList用于找配对交易
		
		Time = self.arrTL3Time[i]
		Signal = self.arrTL3Signal[i]
		Price = self.arrTL3Price[i]
		
		if self.Balance < 0:
			return 0
		
		ITS.Item.rRow = SearchDate(ITS.Item.arrDateTime, ITS.Item.rRow, Time)  # 将品种数据位置，更新到Time时间
		TPH = ITS.Item.arrTPH[ITS.Item.rRow]  # float型，每手吨
		MarginRatio = ITS.Item.arrMarginRatio[ITS.Item.rRow]  # float型，杠杆倍数
		# 计算手数
		result = float((self.Balance) * ITS.TS.Ratio / (TPH / Price))  # 权益*等资金比例/(价格*每手吨*保证金)
		# print("POS", result)
		return max(int(result), 0)


def get_data_from_DB():
	# h5 = pd.read_hdf(config.h5_address, config.symbol)
	myh5 = pd.HDFStore(config.h5_address)
	h5 = myh5[config.symbol]
	myh5.close()
	return h5


def TradeSimMain(h5, TradeList, tradelistfile):
	# h5 = get_data_from_DB()
	Time1 = datetime.datetime.now()  # debug
	tradesim1 = classTradeSim(TradeList, tradelistfile)  # obj型，tradesim1 = TradeSim对象,这对象只有1个。
	Time3 = datetime.datetime.now()  # debug
	Time2 = datetime.datetime.now()
	# print(u'读取H5数据。用时：', Time2 - Time3)
	
	# ========================合约========================================
	# 建立"品种"的对象数组，如BTC, ETH
	# 每个品种的对象内，是关于品种的基础属性，例如保证金、手续费、数据
	dictItem = {}
	for x in range(len(tradesim1.arrItemName)):  # 循环，每一个合约
		Name = tradesim1.arrItemName[x]
		dictItem[Name] = classItem(tradesim1, Name, h5)  # value值是obj
	Time3 = datetime.datetime.now()
	# print(u'建立Item，读数据。用时：', Time3 - Time2)
	
	# =========================策略+周期==================================
	# 建立"周期+策略"的对象数组，如TG1H, X15M
	# 每个"周期+策略"的对象内，有关于头寸管理的属性
	# 周期+策略，是为了以后可以出现TG1H和TG15M的情况，同样是TG,但周期不同，头寸管理方式也可以不同
	dictTS = {}
	for x in range(len(tradesim1.arrTSName)):  # 循环，交易列表内每个策略+周期
		Name = tradesim1.arrTSName[x]
		dictTS[Name] = classTS(tradesim1, Name)
	
	# ============================ITS====================================
	# 建立"合约+周期+策略"(ITS)的对象的数组，如BTC_15M_X
	# 与交易列表完全对应，如BTC_15M_X，则交易列表内一定有交易
	objITSList = []  # list型，保存交易列表内每个合约+周期+策略的对象
	for x in range(len(tradesim1.arrITSName)):  # 循环，交易列表内每一个ITS
		Name = tradesim1.arrITSName[x]
		tem = Name.split(' ')
		objItem = dictItem[tem[0]]
		objTS = dictTS[tem[1] + ' ' + tem[2]]
		objITSList.append(classITS(tradesim1, Name, objItem, objTS))  # 元素是obj型
	
	arrObjITS = np.array(objITSList)  # list转arr
	
	# ========================插入ITS====================================
	# 将ITS插入TradeList3中相应的位置
	for x in range(len(objITSList)):
		tradesim1.InsertITStoTradeList3(objITSList[x])
	Time2 = datetime.datetime.now()
	# print(u'初始化完成。用时：', Time2 - Time1)
	
	rRowTrade = 0  # 标记位置，用于主循环中读取交易列表3的各个交易
	
	for x in range(len(tradesim1.arrDtTime)):  # 遍历每一个结算时间点
		Time = tradesim1.arrDtTime[x]
		
		# 1 每一个ITS，有开平仓要做，计算手数、改持仓 ‘== dt64 比 == str 快’
		# 每次循环k值不会清0，每次从上次位置继续往下找，效率最高
		
		for i in range(rRowTrade, tradesim1.TL3_Len):
			if x >= 1:  # 第二个结算周期以后，上一周期结算时间点 < 当前交易 <= 当前周期结算时间点
				# 这里能把i到i-1之间的交易一次都切片出来成一个list，然后处理这个list么？可以，但是测试过结果更慢。
				if tradesim1.arrDtTime[x - 1] < tradesim1.arrTL3Time[i] <= Time:
					tradesim1.FixPos(i, arrObjITS)  # 改持仓，包括开仓
				else:
					break
			else:  # 第一个结算周期，当前交易 <= 当前周期结算时间点
				# print(tradesim1.arrTL3Time, Time)
				if tradesim1.arrTL3Time[i] <= Time:
					tradesim1.FixPos(i, arrObjITS)  # 改持仓，包括开仓
				else:
					break
		rRowTrade = i
		
		# 2 每一个ITS，有持仓，则计算盈亏
		# 建立一个ITSHoldingList，即有持仓的ITS列表，随着开仓平仓不断drop和append更新，而这里这里循环这个ITSHoldingList
		for i in range(len(arrObjITS)):  # obj型，遍历每一个ITS
			ITS = arrObjITS[i]
			if ITS.LongPos != {} or ITS.ShortPos != {}:  # ITS.LongPos<>0 or ITS.ShortPos<>0表示有持仓
				tradesim1.SettlementCurTime(Time, ITS)  # 计算当前周期的权益
				tradesim1.RiskM(ITS, x, arrObjITS)  # 风险管理，是否需要部分平仓
		
		# 3 计算账户权益、持仓、回撤的变化
		tradesim1.Total(Time)  # 计算当前周期的持仓比例等
	
	Time3 = datetime.datetime.now()
	# print(u'结算主体完成。用时：', Time3 - Time2)
	Summary(tradesim1, u'汇总')
	Time2 = datetime.datetime.now()


# print(u'Summary汇总完成。用时：', Time2 - Time3)
# print(u'结算全部完成。用时：', Time2 - Time1)


if __name__ == '__main__':
	TradeSimMain()
