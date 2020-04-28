#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 17:44:12 2020

@author: LC
"""

from scipy import stats

from TradeSim_Constant import *


def Summary(tradesim1, nickname=None):
	if nickname is None: nickname = u'汇总'
	Time2 = datetime.datetime.now()
	# print(tradesim1.arrTL3Pos)
	tradesim1.arrTL3Pos = tradesim1.arrTL3Pos.astype(np.int64)
	tradesim1.TradeList3[TRDLIST_POS] = tradesim1.arrTL3Pos
	tradesim1.TradeList3[TRDLIST_HOLDDAY] = tradesim1.arrTL3HoldDay
	tradesim1.TradeList3[TRDLIST_CONFEE] = tradesim1.arrTL3Confee
	tradesim1.TradeList3[TRDLIST_RETURN0] = tradesim1.arrTL3Return0
	tradesim1.TradeList3[TRDLIST_RRETURN] = tradesim1.arrTL3RReturn
	tradesim1.TradeList3[TRDLIST_R2RETURN] = tradesim1.arrTL3R2Return
	tradesim1.TradeList3[TRDLIST_OPENBALANCE] = tradesim1.arrTL3OpenBalance
	tradesim1.TradeList3[TRDLIST_OPENPRICE] = tradesim1.arrTL3OpenPrice
	del tradesim1.TradeList3['ITS']  # 交易列表3删掉‘ITSP’列
	
	cond1 = tradesim1.TradeList3[TRDLIST_SIGNAL] == 'sell'
	cond2 = tradesim1.TradeList3[TRDLIST_SIGNAL] == 'cover'
	cond3 = tradesim1.TradeList3[TRDLIST_POS] != 0
	OpenTradeCount = len(tradesim1.TradeList3[((cond1 == True) | (cond2 == True)) & cond3 == True])
	
	arrDate = tradesim1.arrDtTime
	arrBalance = np.array(tradesim1.listBalance, dtype=np.float64)
	arrTotalMargin = np.array(tradesim1.listTotalMargin, dtype=np.float64)
	arrTotalNetMargin = np.array(tradesim1.listTotalNetMargin, dtype=np.float64)
	arrWithDraw = np.array(tradesim1.listWithDraw, dtype=np.float64)
	
	# 权益表 df
	Balance_df = pd.DataFrame([], index=range(len(arrDate)))
	Balance_df[TRDLIST_TIME] = pd.to_datetime(arrDate)
	Balance_df[TRDLIST_BALANCE] = arrBalance
	Balance_df[TRDLIST_MARGIN] = arrTotalMargin
	Balance_df[TRDLIST_NETMARGIN] = arrTotalNetMargin
	Balance_df[TRDLIST_WITHDRAW] = arrWithDraw
	
	# 权益表Day的日期、权益、保证金、轧差保证金、回撤、高点间隔，回撤表的回撤、回撤长度
	BDarrDate, BDarrBalance, BDarrTotalMargin, BDarrTotalNetMargin, BDarrWithDraw, BDarrDisTop, WDlistWithDraw, WDlistWithDrawLen, TradeTimeFrame = ToBalanceDay(
			arrDate, arrBalance, arrTotalMargin, arrTotalNetMargin, arrWithDraw)
	
	# 权益表Day df
	BalanceDay_df = pd.DataFrame([], index=range(len(BDarrDate)))
	BalanceDay_df[TRDLIST_TIME] = BDarrDate
	BalanceDay_df[TRDLIST_BALANCE] = BDarrBalance
	BalanceDay_df[TRDLIST_MARGIN] = BDarrTotalMargin
	BalanceDay_df[TRDLIST_NETMARGIN] = BDarrTotalNetMargin
	BalanceDay_df[TRDLIST_WITHDRAW] = BDarrWithDraw
	BalanceDay_df[TRDLIST_DISTOP] = BDarrDisTop
	
	# 回撤列表，df
	WithDraw_df = pd.DataFrame([], index=range(len(WDlistWithDraw)))
	WithDraw_df[TRDLIST_WITHDRAW] = WDlistWithDraw
	WithDraw_df[TRDLIST_LEN] = WDlistWithDrawLen
	
	# 回撤均值、标准差
	AvgWithDraw, StdWithDraw = AboutWithDraw(WDlistWithDraw)
	
	# 最大回撤_每日、回撤次数
	rRow, WithDraw_Times = AboutWithDraw_Date(BDarrWithDraw)
	maxWithDraw = BDarrWithDraw[rRow]  # 最大回撤 幅度
	maxWithDraw_Date = BDarrDate[rRow]  # 最大回撤 日期
	
	#    #最大高点间隔
	#    rRow = AboutDisTop_Date(WDlistWithDraw)
	#    maxDisTop = WDlistWithDraw[rRow]                                    #最大高点间隔 幅度
	#    maxDisTop_Len = WDlistWithDrawLen[rRow]                             #最大高点间隔 长度
	
	# 连续亏损交易次数，R，盈利交易持仓均值，胜率，交易持仓均值
	maxConLoss, R, AvgHoldWin, Odds_Win, AvgHold = AboutR(tradesim1.arrTL3Pos, tradesim1.arrTL3RReturn,
	                                                      tradesim1.arrTL3HoldDay, OpenTradeCount)
	
	# 连续权益上涨天数 最大值、均值、标准差，连续权益下跌天数 最大值、均值、标准差
	maxConBDWin_Day, avgConBDWin_Day, stdConBDWin_Day, maxConBDLoss_Day, avgConBDLoss_Day, stdConBDLoss_Day = ConWithDrawOrRise(
		BDarrBalance)
	
	# R2，交易次数
	R2 = AboutR2(tradesim1.arrTL3R2Return, tradesim1.arrTL3Pos, OpenTradeCount)
	
	# 最大单笔盈利、平均单笔盈利，最大单笔亏损、平均单笔亏损
	maxWin_Trade, avgWin_Trade, maxLoss_Trade, avgLoss_Trade = AboutWinAndLoss(tradesim1.arrTL3Pos,
	                                                                           tradesim1.arrTL3Return0,
	                                                                           tradesim1.arrTL3Signal,
	                                                                           tradesim1.arrTL3OpenBalance)
	
	# 保证金均、标准差
	avgMargin, stdMargin = AboutMargin(BDarrTotalMargin)
	
	# 单品种结算
	ItemSummary_df = ItemSummary(tradesim1)
	
	listSummary, listSummaryValue = SummaryList()
	
	listSummaryValue[1] = Start(tradesim1)  # 期初权益,int
	listSummaryValue[2] = End(BDarrBalance)  # 期末权益，int
	listSummaryValue[3] = '%.4f%%' % (tradesim1.MaxTotalMargin * 100)
	listSummaryValue[7] = '%.4f%%' % (MaxMargin(BDarrTotalMargin) * 100)  # 最大持仓，从权益表中取，str%
	listSummaryValue[8] = '%.4f%%' % (MaxMargin(BDarrTotalNetMargin) * 100)  # 最大轧差
	listSummaryValue[9] = TradeTimeFrame  # 交易周期，从权益表Day长度，str
	listSummaryValue[10] = '%.4f%%' % (Return(listSummaryValue[1], listSummaryValue[2]) * 100)  # 收益率，str%
	listSummaryValue[11] = '%.4f%%' % (
			ReturnPerYear(listSummaryValue[1], listSummaryValue[2], TradeTimeFrame) * 100)  # 年化收益率，str%
	listSummaryValue[13] = maxWithDraw_Date.strftime('%Y-%m-%d')  # 最大回撤_周期_日期，从权益表Day中取，str
	listSummaryValue[14] = '%.4f%%' % (maxWithDraw * 100)  # 最大回撤_周期_比例，从权益表Day中取，str%
	listSummaryValue[17] = OpenTradeCount  # 信号次数，int
	listSummaryValue[18] = OpenTradeCount * 2  # 交易次数，int
	listSummaryValue[19] = '%.4f%%' % (Odds_Win * 100)  # 胜率，str%
	listSummaryValue[20] = MaxMargin(WDlistWithDrawLen)  # 高点间隔，int
	listSummaryValue[23] = '%.4f%%' % (maxLoss_Trade * 100)  # 最大单笔亏损，str%
	listSummaryValue[24] = '%.4f%%' % (avgLoss_Trade * 100)  # 平均单笔亏损，str%
	listSummaryValue[25] = '%.4f%%' % (maxWin_Trade * 100)  # 最大单笔盈利，str%
	listSummaryValue[26] = '%.4f%%' % (avgWin_Trade * 100)  # 平均单笔盈利，str%
	listSummaryValue[27] = '{:.4f}'.format(R)  # R，str
	listSummaryValue[29] = '{:.4f}'.format(R2)  # R2，str
	listSummaryValue[31] = WithDraw_Times  # 回撤次数，int
	listSummaryValue[32] = '%.4f%%' % (AvgWithDraw * 100)  # 回撤均值，str%
	listSummaryValue[33] = '%.4f%%' % (StdWithDraw * 100)  # 回撤标准差，str%
	listSummaryValue[34] = '%.4f%%' % ((AvgWithDraw + 2 * StdWithDraw) * 100)  # Avg+2Std，str%
	listSummaryValue[37] = '{:.4f}'.format(PMD2b(listSummaryValue[1], WithDraw_Times, TradeTimeFrame, BDarrBalance,
	                                             AvgWithDraw + 2 * StdWithDraw))  # P/MD2b，str
	listSummaryValue[38] = '{:.4f}'.format(
		PMD(listSummaryValue[1], listSummaryValue[2], TradeTimeFrame, maxWithDraw))  # P/MD，str
	listSummaryValue[45] = '%.4f%%' % (avgMargin * 100)  # 持仓均值，从权益表Day中取，str%
	listSummaryValue[46] = '%.4f%%' % (stdMargin * 100)  # 持仓标准差，从权益表Day中取，str%
	listSummaryValue[48] = maxConBDLoss_Day  # 连续回撤天数_最大值，int
	listSummaryValue[49] = '%.4f%%' % (ConFeeBookReturn(listSummaryValue[1], listSummaryValue[2],
	                                                    tradesim1.arrTL3Confee) * 100)  # 手续费/净利润，str%
	listSummaryValue[57] = '{:.4f}'.format(AvgHoldWin)  # 盈利交易平均持仓，str
	listSummaryValue[59] = '{:.4f}'.format(AvgHold)  # 平均持仓，str
	
	Time1 = datetime.datetime.now()
	print(u'Summary计算用时：', Time1 - Time2)
	
	tem_df = pd.DataFrame(listSummary)
	tem_df[1] = listSummaryValue
	
	Summary_df = pd.DataFrame([], index=range(len(BDarrDate)))  # 汇总页，df
	Summary_df['Item'] = tem_df[0]
	Summary_df[nickname] = tem_df[1]
	Summary_df['-'] = np.nan
	Summary_df['--'] = np.nan
	Summary_df['---'] = np.nan
	Summary_df[TRDLIST_TIME] = BDarrDate
	Summary_df[TRDLIST_BALANCE] = BDarrBalance
	Summary_df[TRDLIST_MARGIN] = BDarrTotalMargin
	Summary_df[TRDLIST_NETMARGIN] = BDarrTotalNetMargin
	Summary_df[TRDLIST_WITHDRAW] = BDarrWithDraw
	Summary_df[TRDLIST_DISTOP] = BDarrDisTop
	
	summary2csv(tradesim1, Summary_df, Balance_df, BalanceDay_df, WithDraw_df, ItemSummary_df)
	
	Time2 = datetime.datetime.now()
	print(u'保存csv', Time2 - Time1)


# 权益表转权益表Day
# @jit(nopython=True)
def ToBalanceDay(arrDate, arrBalance, arrTotalMargin, arrTotalNetMargin, arrWithDraw):
	arrDate2 = pd.to_datetime(arrDate)
	BDarrDate = []
	BDarrBalance = []
	BDarrTotalMargin = []
	BDarrTotalNetMargin = []
	BDarrWithDraw = []
	BDarrDisTop = []
	
	# 权益表转权益表Day
	rRow = 0
	for i in range(len(arrDate2) - 1):  # 循环权益表
		if i == 0:
			if arrDate2[0].date() != arrDate2[1].date():  # 前2行不是同一天
				BDarrDate.append(arrDate2[0].date())
				BDarrBalance.append(arrBalance[0])
				BDarrTotalMargin.append(arrTotalMargin[0])
				BDarrTotalNetMargin.append(arrTotalNetMargin[0])
				BDarrWithDraw.append(arrWithDraw[0])
				BDarrDisTop.append(0)
		
		elif arrDate2[i].date() != arrDate2[i + 1].date():
			BDarrDate.append(arrDate2[i].date())
			BDarrBalance.append(arrBalance[i])
			BDarrTotalMargin.append(arrTotalMargin[i])
			BDarrTotalNetMargin.append(arrTotalNetMargin[i])
			BDarrWithDraw.append(abs(BDarrBalance[-1] / max(BDarrBalance) - 1))  # 回撤
			
			if BDarrBalance[-1] == max(BDarrBalance):
				rRow = len(BDarrBalance) - 1
			DisTopTimeDelta = BDarrDate[-1] - BDarrDate[rRow]
			BDarrDisTop.append(DisTopTimeDelta.total_seconds() / 86400)  # 重写高点间距,TimeDelta格式转为秒数，然后除以一天86400秒
	
	BDarrDate.append(arrDate2[i + 1].date())
	BDarrBalance.append(arrBalance[i + 1])
	BDarrTotalMargin.append(arrTotalMargin[i + 1])
	BDarrTotalNetMargin.append(arrTotalNetMargin[i + 1])
	BDarrWithDraw.append(abs(BDarrBalance[-1] / max(BDarrBalance) - 1))  # 回撤
	
	if BDarrBalance[-1] == max(BDarrBalance):
		rRow = len(BDarrBalance) - 1
	DisTopTimeDelta = BDarrDate[-1] - BDarrDate[rRow]
	BDarrDisTop.append(DisTopTimeDelta.total_seconds() / 86400)  # 重写高点间距,TimeDelta格式转为秒数，然后除以一天86400秒
	
	BDarrDate = np.array(BDarrDate)
	BDarrWithDraw = np.array(BDarrWithDraw, dtype=np.float64)
	BDarrDisTop = np.array(BDarrDisTop, dtype=np.int64)
	WDlistWithDraw = []
	WDlistWithDrawLen = []
	# 回撤表
	rRow = 0
	for i in range(len(BDarrWithDraw)):
		if BDarrWithDraw[i] == 0:
			rRow = i
		
		if i < len(BDarrWithDraw) - 1:  # 不是最后一天
			if BDarrWithDraw[i + 1] == 0 and BDarrWithDraw[i] != 0:  # 回撤的最后一天，当天有回撤，但是下一天创新高
				WDlistWithDraw.append(max(BDarrWithDraw[rRow:i + 1]))  # 最大回撤
				TimeDelta = BDarrDate[i] - BDarrDate[rRow]  # 记录回撤长度，回撤最后一天到最后一次新高的日期差，自然日
				WDlistWithDrawLen.append(TimeDelta.total_seconds() / 86400)  # 秒数，转成天数，一天86400秒
		
		elif i == len(BDarrWithDraw) - 1:  # 最后一天
			if BDarrWithDraw[i] != 0:  # 最后一天有回撤
				WDlistWithDraw.append(max(BDarrWithDraw[rRow:i + 1]))  # 最大回撤
				TimeDelta = BDarrDate[i] - BDarrDate[rRow]  # 记录回撤长度，回撤最后一天到最后一次新高的日期差，自然日
				WDlistWithDrawLen.append(TimeDelta.total_seconds() / 86400)  # 秒数，转成天数，一天86400秒
	
	return BDarrDate, BDarrBalance, BDarrTotalMargin, BDarrTotalNetMargin, BDarrWithDraw, BDarrDisTop, WDlistWithDraw, WDlistWithDrawLen, len(
		BDarrDate)


# 计算回撤的均值和标准差，每次回撤记为1次
def AboutWithDraw(WDlistWithDraw):
	avg = np.average(WDlistWithDraw)  # 回撤均值
	
	if len(WDlistWithDraw) <= 1:  # 只有一次回撤，则标准差为0
		std = 0
	else:
		std = np.std(WDlistWithDraw)  # 回撤标准差
	
	return avg, std


# 计算每日的最大回撤，每日回撤记为1次
# @jit(nopython=True)
def AboutWithDraw_Date(BDarrWithDraw):
	rRow = 0
	Times = 1
	
	for i in range(1, len(BDarrWithDraw)):  # 循环，遍历每一次回撤_每日
		if BDarrWithDraw[i] > BDarrWithDraw[rRow]:  # 最大回撤的位置，返回的是字符串格式
			rRow = i
		if BDarrWithDraw[i - 1] == 0 and BDarrWithDraw[i] != 0:  # 当前回撤<>0 上周期回撤==0，记1次
			Times += 1
	
	return rRow, Times


##计算每日的高点间隔
# @jit(nopython=True)
# def AboutDisTop_Date(BDarrDisTop):
#    rRow = 0
#    for i in range(len(BDarrDisTop)):
#        if BDarrDisTop[i] > BDarrDisTop[rRow]:                          #最长的一次高点间隔
#            rRow = i
#
#    return rRow

# 计算R，参数：交易列表3的RReturn列，开仓交易数量
# @jit(nopython=True)
def AboutR(arrTL3Pos, arrTL3RReturn, arrTL3HoldDay, OpenTradeCount):
	maxConLoss = 0  # 连续亏损次数
	result = 0
	Win = 0  # 盈利交易次数
	R_Sum = arrTL3RReturn.sum()
	arrLoss = arrTL3RReturn[arrTL3RReturn < 0]
	LossSum = arrLoss.sum()  # 总亏损
	Loss = len(arrLoss)  # 亏损交易次数
	HoldWinSum = 0
	
	for i in range(len(arrTL3Pos)):
		if arrTL3Pos[i] == 0:  # 判断成交手数是否不等于0，否则无效
			continue
		
		if arrTL3RReturn[i] < 0:
			maxConLoss += 1  # 连续亏损次数
		elif arrTL3RReturn[i] > 0:
			result = max(result, maxConLoss)
			maxConLoss = 0  # 连续亏损次数清0
			Win += 1  # 盈利次数
			HoldWinSum += arrTL3HoldDay[i]  # 盈利交易持仓长度
	
	result = max(result, maxConLoss)
	Odds_Win = float(Win) / OpenTradeCount  # 盈利>0交易/平仓数，float，胜率
	if Win == 0:
		R = -999
		result2 = -999
	elif Loss == 0:
		R = 999
		result2 = 999
	else:
		R = (float(R_Sum) / OpenTradeCount) / abs(LossSum / Loss)  # (盈利总额/盈利次数*胜率-亏损总额/亏损次数*(1-胜率))/(亏损总额/亏损次数)
		result2 = float(HoldWinSum) / Win
	result3 = arrTL3HoldDay.mean()
	
	return result, R, result2, Odds_Win, result3


# 计算R2
# @jit(nopython=True)
def AboutR2(arrTL3R2Return, arrTL3Pos, OpenTradeCount):  # R2
	result = arrTL3R2Return.sum()  # 总收益
	arrLoss = arrTL3R2Return[
		arrTL3R2Return < 0]  # 亏损交易,开仓交易的R2_Return都是0，不会被选进LossList里，所以LossList里选的都是R2_Return<0的平仓交易
	LossSum = arrLoss.sum()  # 总亏损
	Loss = len(arrLoss)  # 亏损交易次数
	
	for i in range(len(arrTL3Pos)):
		if arrTL3Pos[i] == 0:  # 判断成交手数是否不等于0，否则无效
			continue
	
	if LossSum == 0 or Loss == 0:
		R2 = 999
	else:
		R2 = (float(result) / OpenTradeCount) / abs(LossSum / Loss)  # (总收益/平仓次数)/(亏损总额/亏损次数)
	return R2


# 计算最大盈利、平均盈利，最大亏损、平均亏损
# @jit(nopython=True)
def AboutWinAndLoss(arrTL3Pos, arrTL3Return0, arrTL3Signal, arrTL3OpenBalance):
	LossTrade = []
	WinTrade = []
	
	for i in range(len(arrTL3Pos)):
		if arrTL3Pos[i] == 0:  # 判断成交手数是否不等于0，否则无效
			continue
		if arrTL3Signal[i] == 'buy' or arrTL3Signal[i] == 'short':  # 开仓交易，无效
			continue
		tem = float(arrTL3Return0[i]) / arrTL3OpenBalance[i]  # 平仓交易单笔盈亏/开仓时权益
		if tem < 0:  # 若小于0
			LossTrade.append(tem)
		if tem > 0:  # 若大于0
			WinTrade.append(tem)
		if len(LossTrade)==0:
			LossTrade.append(tem)
		if len(WinTrade)==0:
			WinTrade.append(tem)
	return np.max(WinTrade), np.average(WinTrade), np.min(LossTrade), np.average(LossTrade)


# 连续回撤、上涨天数
# @jit(nopython=True)
def ConWithDrawOrRise(BDarrBalance):
	Win = 0  # 连续上涨天数
	Loss = 0  # 连续下跌天数
	WinList = []
	LossList = []
	
	for i in range(1, len(BDarrBalance)):
		if BDarrBalance[i] > BDarrBalance[i - 1]:  # 权益上涨
			Win += 1  # 连续上涨天数+1
			LossList.append(Loss)  # 连续下跌天数结束，保存
			Loss = 0  # 连续下跌天数清0
		elif BDarrBalance[i] < BDarrBalance[i - 1]:  # 权益下跌
			Loss += 1  # 连续下跌天数+1
			WinList.append(Win)  # 连续上涨天数结束，保存
			Win = 0  # 连续上涨天数清0
		if len(WinList)==0:
			WinList.append(Win)
		if len(LossList)==0:
			LossList.append(Loss)
	return np.max(WinList), np.average(WinList), np.std(WinList), np.max(LossList), np.average(LossList), np.std(
			LossList)


def SummaryList():
	listSummary = ['', TRDLIST_START, TRDLIST_END, TRDLIST_MAXTOTALMARGIN, TRDLIST_SYS1RISKPERATR,
	               TRDLIST_SYS2RISKPERATR,
	               TRDLIST_SYS3RISKPERATR, TRDLIST_MAXMARGIN, TRDLIST_NETMARGIN, TRDLIST_TRADETIMEFRAME, TRDLIST_RETURN,
	               TRDLIST_RETURNPERYEAR, TRDLIST_MONRETURN,
	               TRDLIST_MAXWITHDRAWDATE, TRDLIST_MAXWITHDRAW, TRDLIST_MAXWITHDRAWSINGLEDATE,
	               TRDLIST_MAXWITHDRAWSINGLE, TRDLIST_TOTALSIGNAL, TRDLIST_TOTALTRADE, TRDLIST_ODDS,
	               TRDLIST_DISTOP, TRDLIST_DISTOPDATE, TRDLIST_MAXCONLOSS, TRDLIST_MAXSINGLELOSS, TRDLIST_AVGSINGLELOSS,
	               TRDLIST_MAXSINGLEWIN, TRDLIST_AVGSINGLEWIN, TRDLIST_R,
	               TRDLIST_RW, TRDLIST_R2, TRDLIST_R2W, TRDLIST_TOTALWITHDRAW, TRDLIST_AVGWITHDRAW, TRDLIST_STDWITHDRAW,
	               TRDLIST_AVG2STD, TRDLIST_PAVG2STD, TRDLIST_GEOAVGRETURN,
	               TRDLIST_PMD2B, TRDLIST_PMD, TRDLIST_STDCONWITHDRAWDAY, TRDLIST_MAXCONRISEDAY, TRDLIST_AVGCONRISEDAY,
	               TRDLIST_STDCONRISEDAY, TRDLIST_AVGWITHDRAWDAY,
	               TRDLIST_STDWITHDRAWDAY, TRDLIST_AVGMARGIN, TRDLIST_STDMARGIN, TRDLIST_REPLACETRADE,
	               TRDLIST_MAXCONWITHDRAWDAY, TRDLIST_CONFEEBOOKRETURN, TRDLIST_SYS4RISKPERATR,
	               TRDLIST_SYS5RISKPERATR, '', TRDLIST_SYS6RISKPERATR, '', TRDLIST_OVERRISKABANDONED,
	               TRDLIST_OVERMARGINABANDONED, TRDLIST_AVGMARGINWIN, TRDLIST_AVGCONWITHDRAWDAY, TRDLIST_AVGHOLD]
	listSummaryValue = [''] * len(listSummary)
	
	return listSummary, listSummaryValue


def Start(tradesim1):  # 期初权益
	result = tradesim1.StartBalance
	return result


def End(BDarrBalance):  # 期末权益
	result = BDarrBalance[-1]
	return result


def MaxMargin(arr):
	result = np.max(arr)  # 最大持仓，从权益表中取
	return result


def Return(StartBalance, EndBalance):  # 收益率
	result = EndBalance / StartBalance - 1  # 期末权益/期初权益-1
	return result


def ReturnPerYear(StartBalance, EndBalance, daydelta):  # 年化收益率
	result = (EndBalance / StartBalance) ** (365.0 / daydelta) - 1  # 总收益率**(1年261天/总天数)
	return result


def ExpectReturn(BDarrBalance, TradeTimeFrame, StartBalance):  # 期望收益率，pd.series
	y_value = BDarrBalance  # y值，各时间点权益，从权益表Day中取
	x_value = range(TradeTimeFrame)  # x值，[1,2,3,4……]
	slope = stats.linregress(x_value, y_value)[0]  # 斜率，一元回归
	result = slope * x_value[-1] + StartBalance  # 期望收益=斜率*x+截距
	return result


def GeoAvgReturn(WithDraw_Times, TradeTimeFrame, StartBalance, BDarrBalance):  # 几何平均收益
	expectReturn = ExpectReturn(BDarrBalance, TradeTimeFrame, StartBalance)  # 期望收益率
	result = (expectReturn / StartBalance) ** (1.0 / WithDraw_Times) - 1  # 期望收益率^(1/回撤次数)-1
	return result


def PMD2b(StartBalance, WithDraw_Times, TradeTimeFrame, BDarrBalance, avg_2std):  # P/MD2b
	result2 = GeoAvgReturn(WithDraw_Times, TradeTimeFrame, StartBalance, BDarrBalance)  # 几何平均收益
	WithDrawPerYear = WithDraw_Times * (365.0 / TradeTimeFrame)  # 年回撤次数=总回撤*(1年261天/总天数)
	result = result2 * WithDrawPerYear / avg_2std  # 几何平均收益*年回撤次数/(回撤Avg+2Std)
	return result


def PMD(StartBalance, EndBalance, TradeTimeFrame, maxWithDraw):  # P/MD
	ReturnPY = ReturnPerYear(StartBalance, EndBalance, TradeTimeFrame)
	result = ReturnPY / maxWithDraw  # 年化收益率/最大回撤_周期，从权益表Day中取
	return result


def AboutMargin(BDarrMargin):  # 保证金均值、标准差
	avg = np.average(BDarrMargin)
	std = np.std(BDarrMargin)
	return avg, std


def ConFeeBookReturn(StartBalance, EndBalance, arrTL3Confee):  # 手续费/净利润
	TotalConFee = arrTL3Confee.sum()  # 总手续费
	result = TotalConFee / (EndBalance - StartBalance)  # 手续费/(最终权益-期初权益)
	return result


# ============================================================================
# 单品种结算
def ItemSummary(tradesim1):
	listItemTotalTrade = []  # 单品种交易笔数
	listItemOdds = []  # 单品种胜率
	listItemAvgReturn = []  # 单品种平均盈利
	listItemAvgLoss = []  # 单品种平均亏损
	listItemR = []  # 单品种R
	listItemR2 = []  # 单品种R2
	listItemWin = []  # 单品种盈利持仓
	listItemLoss = []  # 单品种亏损持仓
	
	arrTL3Item = tradesim1.TradeList3[TRDLIST_ITEM].values  # 交易列表中的品种
	arrItem = np.unique(arrTL3Item)  # 去重
	
	for i in range(len(arrItem)):
		Item = arrItem[i]
		listItemSignal = []
		listItemPos = []
		listItemRReturn = []
		listItemR2Return = []
		for j in range(len(arrTL3Item)):
			if arrTL3Item[j] != Item:
				continue
			listItemSignal.append(tradesim1.arrTL3Signal[j])
			listItemPos.append(tradesim1.arrTL3Pos[j])
			listItemRReturn.append(tradesim1.arrTL3RReturn[j])
			listItemR2Return.append(tradesim1.arrTL3R2Return[j])
		
		arrItemSignal = np.array(listItemSignal)
		arrItemPos = np.array(listItemPos)
		arrItemRReturn = np.array(listItemRReturn)
		arrItemR2Return = np.array(listItemR2Return)
		
		# 单品种的胜率，平均盈利，平均亏损，R，平仓交易数量
		odds, avgWin, avgLoss, R, CloseTrade = ItemAboutR(arrItemSignal, arrItemPos, arrItemRReturn)
		listItemTotalTrade.append(len(arrItemSignal))
		listItemOdds.append('%.4f%%' % (odds * 100))
		listItemAvgReturn.append('%.4f%%' % (avgWin * 100))
		listItemAvgLoss.append('%.4f%%' % (avgLoss * 100))
		listItemR.append('{:.4f}'.format(R))
		listItemR2.append('{:.4f}'.format(ItemR2(arrItemR2Return, CloseTrade)))
	
	Item_df = pd.DataFrame([], index=range(len(listItemTotalTrade)))  # 单品种汇总表，df
	
	Item_df[TRDLIST_ITEM] = arrItem.tolist()
	
	Item_df[TRDLIST_TOTALTRADE] = listItemTotalTrade  # 交易次数
	Item_df[TRDLIST_ODDS] = listItemOdds  # 胜率
	Item_df[TRDLIST_AVGRETURN] = listItemAvgReturn  # 平均盈利
	Item_df[TRDLIST_AVGLOSS] = listItemAvgLoss  # 平均亏损
	Item_df[TRDLIST_R] = listItemR  # 单品种R
	Item_df[TRDLIST_R2] = listItemR2  # 单品种R2
	
	return Item_df


# @jit(nopython=True)
def ItemAboutR(arrItemSignal, arrItemPos, arrItemRReturn):
	CloseTrade = 0  # 平仓数量
	Win = 0  # 盈利交易数量
	WinSum = 0  # 盈利总额
	Loss = 0  # 亏损交易数量
	LossSum = 0  # 亏损总额
	
	for i in range(len(arrItemRReturn)):
		if arrItemPos[i] == 0:
			continue
		if arrItemRReturn[i] > 0:  # 盈利的交易
			Win += 1
			WinSum += arrItemRReturn[i]
		elif arrItemRReturn[i] < 0:  # 亏损的交易
			Loss += 1
			LossSum += arrItemRReturn[i]
		
		if arrItemSignal[i] == 'sell' or arrItemSignal[i] == 'cover':  # 平仓交易
			CloseTrade += 1
	
	if CloseTrade == 0:
		odds = -999
	else:
		odds = float(Win) / CloseTrade
	
	if WinSum == 0:
		avgWin = 0
	else:
		avgWin = float(WinSum) / Win  # 盈利>0交易/盈利交易数
	
	if LossSum == 0:
		avgLoss = 0
	else:
		avgLoss = float(LossSum) / Loss  # 盈利<0交易/亏损交易数
	
	if LossSum == 0 or Loss == 0:
		R = 999
	elif Win == 0:
		R = -999
	else:
		R = (float(WinSum) / Win * odds - abs(float(LossSum) / Loss) * (1 - odds)) / abs(
				float(LossSum) / Loss)  # (盈利总额/盈利次数*胜率-亏损总额/亏损次数*(1-胜率))/(亏损总额/亏损次数)
	
	return odds, avgWin, avgLoss, R, CloseTrade


def ItemR2(arrItemR2Return, CloseTrade):  # R2
	Return = arrItemR2Return.sum()  # 总收益
	Loss = 0
	TotalLoss = 0
	for i in range(len(arrItemR2Return)):
		if arrItemR2Return[i] < 0:
			Loss += arrItemR2Return[i]  # 总亏损
			TotalLoss += 1  # 亏损交易次数
	
	if Loss == 0 or TotalLoss == 0:
		R2 = 999
	elif CloseTrade == 0:
		R2 = 0
	else:
		R2 = (float(Return) / CloseTrade) / abs(float(Loss) / TotalLoss)  # (总收益/平仓次数)/(亏损总额/亏损次数)
	return R2


def summary2csv(tradesim1, Summary_df, Balance_df, BalanceDay_df, WithDraw_df, ItemSummary_df):
	pn = os.path.dirname(tradesim1.TradeListFile)  # 路径
	fn = os.path.basename(tradesim1.TradeListFile)  # 文件名，无路径的
	fn1 = os.path.splitext(fn)[0]  # 无路径文件名的第一部分，即无后缀的纯文件名，用做文件夹名
	
	if tradesim1.SaveMode == EXCEL_OLD:
		if pn:
			writer = pd.ExcelWriter(pn + '/' + fn1 + '.xlsx')  # 路径
		else:
			writer = pd.ExcelWriter(fn1 + '.xlsx')  # 路径
		Summary_df.to_excel(writer, TRDLIST_TOTAL, index=False)  # 汇总页保存成excel
		tradesim1.TradeSheet.to_excel(writer, TRDLIST_TRDLIST, index=False)  # 交易列表1保存成excel
		tradesim1.TradeList3.to_excel(writer, TRDLIST_TRDLIST3, index=False)  # 交易列表3保存成excel
		Balance_df.to_excel(writer, TRDLIST_BALANCE, index=False)  # 权益表保存成excel
		BalanceDay_df.to_excel(writer, TRDLIST_BALANCEDAY, index=False)  # 权益表Day保存成excel
		WithDraw_df.to_excel(writer, TRDLIST_WITHDRAW)  # 回撤页保存成excel
		ItemSummary_df.to_excel(writer, TRDLIST_ITEM, index=False)  # 单品种页保存成excel
		writer.save()
	else:
		
		writer = pd.ExcelWriter(pn + '/' + fn1 + '_' + TRDLIST_TOTAL + '.xlsx')  # 路径
		Summary_df.to_excel(writer, TRDLIST_TOTAL, index=False)  # 汇总页保存成excel
		writer.save()
		
		if tradesim1.SaveMode == EXCEL_DETAIL:  # 详细版，保存所有页
			tradesim1.TradeSheet.to_csv(pn + '/' + fn1 + '_' + TRDLIST_TRDLIST + '.csv', index=False,
			                            encoding='GB18030')  # 交易列表
			tradesim1.TradeList3.to_csv(pn + '/' + fn1 + '_' + TRDLIST_TRDLIST3 + '.csv', index=False,
			                            encoding='GB18030')  # 交易列表3
			Balance_df.to_csv(pn + '/' + fn1 + '_' + TRDLIST_BALANCE + '.csv', index=False, encoding='GB18030')  # 权益表
			BalanceDay_df.to_csv(pn + '/' + fn1 + '_' + TRDLIST_BALANCEDAY + '.csv', index=False,
			                     encoding='GB18030')  # 权益表Day
			WithDraw_df.to_csv(pn + '/' + fn1 + '_' + TRDLIST_WITHDRAW + '.csv', encoding='GB18030')  # 回撤
			ItemSummary_df.to_csv(pn + '/' + fn1 + '_' + TRDLIST_ITEM + '.csv', index=False, encoding='GB18030')  # 品种
