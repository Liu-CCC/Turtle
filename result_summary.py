import os

import pandas as pd


def summary_results(arrStrategy):
	# path = 'results/'+arrStrategy+'/BTC/15min'
	path = 'results/' + arrStrategy + '/' + timePeriod
	for f, l, m in os.walk(path):
		pass
	data = pd.DataFrame()
	for i in range(len(m)):
		print(m[i])
		try:
			df = pd.read_excel(path + '/' + m[i], sheet_name=u'汇总')
			df = df[['Item', u'汇总']].dropna().T
			df.columns = df.loc['Item']
			df.drop(index='Item', inplace=True)
			df.rename(index={u'汇总': m[i]}, inplace=True)
			
			SumRes_last_eq = u'期末权益'
			SumRes_hold_rate = u'持仓比例_最大值'
			SumRes_trade_day = u'交易周期'
			SumRes_rate = u'收益率'
			SumRes_annul_ret = u'年化收益率'
			SumRes_md_day = u'最大回撤_周期_日期'
			SumRes_md = u'最大回撤_周期_比例'
			SumRes_singal_num = u'信号次数'
			SumRes_win_rate = u'胜率'
			SumRes_md_days = u'回撤天数_最大值'
			SumRes_ms_loss = u'最大单笔亏损'
			SumRes_avr_s_loss = u'平均单笔亏损'
			SumRes_ms_win = u'最大单笔盈利'
			SumRes_avr_s_win = u'平均单笔盈利'
			SumRes_R = u'R'
			SumRes_R2 = u'R2'
			SumRes_md_times = u'回撤次数'
			SumRes_md_avr = u'回撤均值'
			SumRes_md_std = u'回撤标准差'
			SumRes_md_avr_std = u'回撤avg+2*std'
			SumRes_p_md2b = u'P/MD2b'
			SumRes_p_md = u'P/MD'
			SumRes_avr_hold = u'平均持仓'
			SumRes_std_hold = u'持仓标准差'
			SumRes_fee_win = u'手续费/净利润'
			SumRes_win_avr_hold = u'盈利交易平均持仓'
			data = pd.concat([data, df])
		except Exception as e:
			print(e)
	data = data[
		[SumRes_last_eq, SumRes_hold_rate, SumRes_trade_day, SumRes_rate, SumRes_annul_ret, SumRes_md_day, SumRes_md,
		 SumRes_singal_num, SumRes_win_rate, SumRes_md_days, SumRes_ms_loss, SumRes_avr_s_loss, SumRes_ms_win,
		 SumRes_avr_s_win, SumRes_R, SumRes_R2, SumRes_md_times, SumRes_md_avr, SumRes_md_std, SumRes_md_avr_std,
		 SumRes_p_md2b, SumRes_p_md, SumRes_avr_hold, SumRes_std_hold, SumRes_fee_win, SumRes_win_avr_hold]]
	data.to_excel('results/' + arrStrategy + timePeriod + '.xlsx')


arrStrategy = 'Turtle'
timePeriod = "4H"
summary_results(arrStrategy=arrStrategy)
