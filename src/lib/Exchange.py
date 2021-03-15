import ccxt
import lib.config as config
import pandas as pd
import numpy as np
import time
import traceback

class Exchange:
	"""This class is used to interact with the market. It's a wrapper for a ccxt exchange object.
	"""

	def __init__(self, logger, capital_allowed, default_ticker=None, default_period=None):
		"""
		- logger: a Logger instance linked to a bot
		"""
		self.logger = logger
		self.capital_allowed = capital_allowed
		self.default_ticker = default_ticker
		self.default_period = default_period
		self.client = ccxt.binance(config.get_creds()['binance'])

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
		data = pd.DataFrame()
		data['timestamp'] = candles[:, 0]
		data['date'] = pd.to_datetime(data['timestamp'] * 1000000)
		data['open'] = candles[:, 1]
		data['high'] = candles[:, 2]
		data['low'] = candles[:, 3]
		data['close'] = candles[:, 4]
		data['volume'] = candles[:, 5]
		return data

	def buy(self, ticker=None, amount=100):
		"""Buy the given ticker.

		- ticker: string, the ticker formatted like that: ASSET1/ASSET2, optional if default is set
		- amount: int, percentage of the capital allowed to the bot to buy with, optional
		Returns a trade object.
		"""
		if (ticker is None):
			ticker = self.default_ticker
		asset1 = ticker.split("/")[0]
		asset2 = ticker.split("/")[1]
		balance = self.get_balance(asset2)
		price = self.client.fetch_ticker(ticker)['last']
		proportion = (amount / 100) * (self.capital_allowed / 100)
		qty = (balance * proportion) / price
		qty = self.client.amount_to_precision(ticker, qty)
		try:
			self.logger.log("ℹ️", f"Buying {qty}{asset1}")
			trade = self.client.create_market_buy_order(ticker, qty)
			self.logger.log("💵", f"Bought {qty}{asset1} for {trade['price']:.2f}{asset2} with {amount}% of available {asset2}")
			self.logger.order('buy', trade['price'], trade['cost'])
			return trade
		except:
			traceback.print_exc()
			self.logger.log("❌", "Cannot buy, retrying in 3 seconds")
			time.sleep(3)
			return self.buy(ticker, amount)

	def sell(self, ticker=None, amount=100):
		"""Sell the given ticker.

		- ticker: string, the ticker formatted like that: ASSET1/ASSET2, optional if default is set
		- amount: int, percentage of the asset to sell, optional
		Returns a trade object.
		"""
		if (ticker is None):
			ticker = self.default_ticker
		asset1 = ticker.split("/")[0]
		asset2 = ticker.split("/")[1]
		balance = self.get_balance(asset1)
		qty = balance * (amount / 100)
		try:
			self.logger.log("ℹ️", f"Selling {qty}{asset1}")
			trade = self.client.create_market_sell_order(ticker, qty)
			self.logger.log("💵", f"Sold {qty}{asset1} ({amount}%) for {trade['price']}{asset2}")
			self.logger.order('sell', trade['price'], trade['cost'])
			return trade
		except:
			traceback.print_exc()
			self.logger.log("❌", "Cannot sell, retrying in 3 seconds")
			time.sleep(3)
			return self.sell(ticker, amount)

	def get_balance(self, asset=None):
		"""Get the balance of the account for the given asset.

		- asset: string, the asset to check, optional if default is set
		Returns the current asset balance as float.
		"""
		if (asset is None):
			asset = self.default_ticker.split("/")[1]
		try:
			return self.client.fetch_balance()[asset]['free']
		except:
			self.logger.log("❌", f"Cannot fetch balance for {asset}")
			return None