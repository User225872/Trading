import backtrader as bt
import backtrader.feeds as btfeeds
import datetime
import os
import pandas as pd
import sys

CASH = 10 ** 5
STRATDATE = '2013-01-04'
ENDDATE = '2021-03-19'
NUMOFDAY = 2005

class SMAEMAStrategy(bt.Strategy):
	params = (
		('smaperiod', 15),
		('emaperiod1', 12),
		('emaperiod2', 26),
	)

	def log(self, txt, dt=None):
		dt = dt or self.datas[0].datetime.date(0)
		print('%s, %s' % (dt.isoformat(), txt))

	def __init__(self):
		self.dataclose = self.datas[0].close
		self.order = None
		self.buyprice = None

		self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.smaperiod)
		self.macd = bt.indicators.MACD(self.datas[0], period_me1=self.params.emaperiod1, period_me2=self.params.emaperiod2)

		self.close_over_sma = self.dataclose > self.sma
		self.macd_over_zero = self.macd > 0

		self.buy_sig = bt.And(self.close_over_sma, self.macd_over_zero)

		self.close_below_sma = self.dataclose < self.sma
		self.macd_below_zero = self.macd < 0

		self.sell_sig = bt.And(self.close_below_sma, self.macd_below_zero)

	def notify_order(self, order):
		if order.status in [order.Submitted, order.Accepted]:
			return

		if order.status in [order.Completed]:
			if order.isbuy():
				self.log(
					'BUY EXECUTED, Price: %.2f, Cost: %.2f' %
					(order.executed.price,
					 order.executed.value))

				self.buyprice = order.executed.price
			else:
				self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f' %
						 (order.executed.price,
						  order.executed.value))

			self.bar_executed = len(self)

		elif order.status in [order.Canceled, order.Margin, order.Rejected]:
			self.log('Order Canceled/Margin/Rejected')

		self.order = None

	def notify_trade(self, trade):
		if not trade.isclosed:
			return

		self.log('OPERATION PROFIT, NET %.2f' % trade.pnlcomm)

	def next(self):
		if self.order:
			return

		if not self.position:
			if self.buy_sig:
				self.log('BUY CREATE, %.2f' % self.dataclose[0])

				self.order = self.buy()
		else:
			if self.sell_sig:
				self.log('SELL CREATE, %.2f' % self.dataclose[0])

				self.order = self.sell()

def Preprocess():
	global new_df
	global new_tickers

	df = pd.read_csv('data.csv')
	df['date']= pd.to_datetime(df['date'])

	tickers = set(df['ticker'].to_list())

	new_tickers = []

	for ticker in tickers:
		df_ticker = df.loc[df['ticker'] == ticker]

		if df_ticker.shape[0] == NUMOFDAY:
			new_tickers.append(ticker)

	new_tickers.sort()

	new_df = df.loc[df['ticker'].isin(new_tickers)]

def main(argv):
	Preprocess()

	cerebro = bt.Cerebro()

	cerebro.addstrategy(SMAEMAStrategy)

	for ticker in new_tickers[ : 1]:
		df_ = new_df.loc[new_df['ticker'] == ticker]
		data = bt.feeds.PandasData(dataname=df_, datetime="date", open='last', high='last', low='last', close='last', volume='volume', openinterest=None)
		cerebro.adddata(data, name=ticker)

	cerebro.broker.setcash(CASH)

	cerebro.addsizer(bt.sizers.FixedSize, stake=10)

	print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

	cerebro.run()

	print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

if __name__ == "__main__":
	main(sys.argv[1 : ])
