import ccxt
import lib.config as config
import pandas as pd
import numpy as np
import time
import traceback
from datetime import datetime
from lib.Data import Data

class Exchange:
	"""This class is used to interact with the market. It's a wrapper for a ccxt exchange object.
	"""

	def __init__(self, logger, data, capital_allowed, live_mode, default_ticker=None, default_period=None):
		"""
		- logger: a Logger instance linked to a bot
		- data: a Data instance linked to a bot
		- capital_allowed: float, percentage (0-100) of the capital this instance is able to trade with
		- live_mode: bool, should we make real orders on the markets or simulate them
		- default_ticker: string, the ticker formatted like that: ASSET1/ASSET2, optional 
		- default_period: string, the period resolution you want to get data in (1m, 5m, 1h...), optional
		"""
		self.logger = logger
		self.data = data
		self.capital_allowed = capital_allowed
		self.default_ticker = default_ticker
		self.default_period = default_period
		self.live_mode = live_mode
		self.fake_balance = []
		self.fake_pnl = []
		self.fake_current_price = None
		self.fake_current_date = None
		self.fake_orders = []
		if (self.default_period and self.default_ticker):
			self.cache = Data(f"{self.default_period}-{''.join(self.default_ticker.split('/'))}-cache")
		else:
			self.cache = None
		self.client = ccxt.binance(config.get_creds()['binance'])

	def candles_to_df(self, candles):
		data = pd.DataFrame()
		data['timestamp'] = candles[:, 0]
		data['date'] = pd.to_datetime(data['timestamp'] * 1000000)
		data['open'] = candles[:, 1]
		data['high'] = candles[:, 2]
		data['low'] = candles[:, 3]
		data['close'] = candles[:, 4]
		data['volume'] = candles[:, 5]
		return data

	def get_latest_data(self, ticker=None, period=None, length=0):
		"""Fetch the latest data for the given ticker. It will return at least lenth candles.
		
		- ticker: string, the ticker formatted like that: ASSET1/ASSET2, optional if default is set
		- period: string, the period resolution you want (1m, 5m, 1h...), optional is default is set
		- length: int, the minimum number of past candles you want, optional
		Returns a pandas dataframe.
		"""
		if (ticker is None):
			ticker = self.default_ticker
		if (period is None):
			period = self.default_period
		candles = None
		try:
			candles = np.array(self.client.fetch_ohlcv(ticker, period))
		except:
			self.logger.log("❗️", "Unable to fetch live data, retrying in 10 seconds")
			time.sleep(10)
			return self.get_latest_data(ticker, length)
		return self.candles_to_df(candles)

	def get_data(self, start_date, end_date, ticker=None, period=None):
		"""Get historical data between the given dates.

		- start_date: string, a date formatted in ISO 8601 from when to download data
		- end_date: string, a date formatted in ISO 8601
		"""
		if (ticker is None):
			ticker = self.default_ticker
		if (period is None):
			period = self.default_period
		if (not self.cache is None and not self.cache.get(f"{start_date}-{end_date}") is None):
			return self.cache.get(f"{start_date}-{end_date}")
		start = self.client.parse8601(start_date)
		end = self.client.parse8601(end_date)

		candles = None
		last_date = start
		while (last_date < end):
			print(f"Downloading {datetime.utcfromtimestamp(last_date / 1000).isoformat()}")
			new_candles = np.array(self.client.fetch_ohlcv(ticker, period, last_date))
			if (candles is None):
				candles = new_candles
			else:
				candles = np.vstack([candles, new_candles])
			last_date = int(candles[-1][0])
			time.sleep(1)
		df = self.candles_to_df(candles)
		if (not self.cache is None):
			self.cache.set(f"{start_date}-{end_date}", df)
		return df

	def buy(self, ticker=None, max_try=3):
		"""Buy the given ticker.

		- ticker: string, the ticker formatted like that: ASSET1/ASSET2, optional if default is set
		Returns a trade object.
		"""
		if (max_try <= 0):
			self.logger.log("❌", "Failed 3 times to buy, giving up")
			return None
		if (ticker is None):
			ticker = self.default_ticker
		if (not self.live_mode):
			return self.fake_buy(ticker)
		asset1 = ticker.split("/")[0]
		asset2 = ticker.split("/")[1]
		balance = self.get_balance(asset2)
		price = self.client.fetch_ticker(ticker)['last']
		proportion = (self.capital_allowed / 100)
		qty = (balance * proportion) / price
		qty = self.client.amount_to_precision(ticker, qty)
		try:
			self.logger.log("ℹ️", f"Buying {qty}{asset1}")
			trade = self.client.create_market_buy_order(ticker, qty)
			self.logger.log("💵", f"Bought {qty}{asset1} for {trade['price']:.2f}{asset2}")
			self.logger.order('buy', trade['price'], trade['cost'])
			self.data.set("buy_cost", trade['cost'])
			return trade
		except:
			traceback.print_exc()
			self.logger.log("❌", "Cannot buy, retrying in 3 seconds")
			time.sleep(3)
			return self.buy(ticker, max_try - 1)

	def sell(self, ticker=None, max_try=3):
		"""Sell the given ticker.

		- ticker: string, the ticker formatted like that: ASSET1/ASSET2, optional if default is set
		Returns a trade object.
		"""
		if (max_try <= 0):
			self.logger.log("❌", "Failed 3 times to sell, giving up")
			return None
		if (ticker is None):
			ticker = self.default_ticker
		if (not self.live_mode):
			return self.fake_sell(ticker)
		asset1 = ticker.split("/")[0]
		asset2 = ticker.split("/")[1]
		balance = self.get_balance(asset1)
		try:
			self.logger.log("ℹ️", f"Selling {balance}{asset1}")
			trade = self.client.create_market_sell_order(ticker, balance)
			self.logger.log("💵", f"Sold {balance}{asset1} for {trade['price']}{asset2}")
			self.logger.order('sell', trade['price'], trade['cost'])
			balance_diff = trade['cost'] - self.data.get("buy_cost")
			self.logger.pnl(
				balance_diff / self.data.get("buy_cost") * 100,
				balance_diff
			)
			self.logger.balance(self.get_balance())
			self.data.remove("buy_cost")
			return trade
		except:
			traceback.print_exc()
			self.logger.log("❌", "Cannot sell, retrying in 3 seconds")
			time.sleep(3)
			return self.sell(ticker, max_try - 1)
	
	def fake_buy(self, ticker):
		"""This functions creates a fake buy order.
		The buy function of a bot in backtracking mode is redirected here.
		It's called automatically by the backtracking algorithm, you shouldn't
		have to use it.
		"""
		self.data.set("buy_price", self.fake_current_price)
		self.fake_orders.append({
			'action': 'buy',
			'date': self.fake_current_date
		})

	def fake_sell(self, ticker):
		"""This functions creates a fake sell order.
		The sell function of a bot in backtracking mode is redirected here.
		It's called automatically by the backtracking algorithm, you shouldn't
		have to use it.
		It will calculate estimated PNL for the trade.
		"""
		diff_cost = self.fake_current_price - self.data.get("buy_price")
		diff_per = (diff_cost / self.data.get("buy_price")) * 100
		diff_per -= 0.2
		profit = self.fake_balance[-1] * (diff_per / 100)
		self.fake_balance.append(self.fake_balance[-1] + profit)
		self.fake_pnl.append(diff_per)
		self.data.remove("buy_price")
		self.fake_orders.append({
			'action': 'sell',
			'date': self.fake_current_date
		})

	def get_balance(self, asset=None):
		"""Get the balance of the account for the given asset.

		- asset: string, the asset to check, optional if default is set
		Returns the current asset balance as float.
		"""
		if (not self.live_mode):
			return None
		if (asset is None):
			asset = self.default_ticker.split("/")[1]
		try:
			return self.client.fetch_balance()[asset]['free']
		except:
			self.logger.log("❌", f"Cannot fetch balance for {asset}")
			return None
	
	def init_fake_balance(self):
		"""This functions initializes the backtesting fake balance array
		"""
		self.fake_balance = [100]
		self.fake_pnl = []
		self.fake_orders = []