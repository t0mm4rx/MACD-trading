import ccxt
import lib.config as config
import pandas as pd
import numpy as np
import time

class Exchange:
	"""This class is used to interact with the market. It's a wrapper for a ccxt exchange object.
	"""

	def __init__(self, logger):
		"""
		- logger: a Logger instance linked to a bot
		"""
		self.logger = logger
		self.client = ccxt.binance(config.get_creds()['binance'])

	def get_latest_data(self, ticker, period, length = 0):
		"""Fetch the latest data for the given ticker. It will return at least lenth candles.
		
		- ticker: string, the ticker formatted like that: ASSET1/ASSET2
		- period: string, the period resolution you want (1m, 5m, 1h...)
		- length: int, the minimum number of past candles you want, optional
		Returns a pandas dataframe.
		"""
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

	def buy(self, ticker, amount=100):
		"""Buy the given ticker.

		- ticker: string, the ticker formatted like that: ASSET1/ASSET2
		- amount: int, percentage of the capital allowed to the bot to buy with, optional
		Returns a trade object.
		"""
		asset1 = ticker.split("/")[0]
		asset2 = ticker.split("/")[1]
		balance = self.get_balance(asset2)
		price = self.client.fetch_ticker(ticker)['last']
		qty = (balance * (amount / 100)) / price
		qty = self.client.amount_to_precision(ticker, qty)
		try:
			trade = self.client.create_market_buy_order(ticker, qty)
			self.logger.log("💵", f"Bought {qty}{asset1} for {trade['price']}{asset2} with {amount}% of available {asset2}")
			return trade
		except:
			self.logger.log("❌", "Cannot buy, retrying in 3 seconds")
			time.sleep(3)
			return self.buy(ticker, amount)

	def sell(self, ticker, amount=100):
		"""Sell the given ticker.

		- ticker: string, the ticker formatted like that: ASSET1/ASSET2
		- amount: int, percentage of the asset to sell, optional
		Returns a trade object.
		"""
		asset1 = ticker.split("/")[0]
		asset2 = ticker.split("/")[1]
		balance = self.get_balance(asset2)
		qty = balance * (amount/100)
		try:
			trade = self.client.create_market_sell_order(ticker, qty)
			self.logger.log("💵", f"Sold {qty}{asset1} ({amount}%) for {trade['price']}{asset2}")
		except:
			self.logger.log("❌", "Cannot sell, retrying in 3 seconds")
			time.sleep(3)
			return self.sell(ticker, amount)

	def get_balance(self, asset):
		"""Get the balance of the account for the given asset.

		- asset: string, the asset to check
		Returns the current asset balance as float.
		"""
		try:
			return self.client.fetch_balance()[asset]['free']
		except:
			self.logger.log("❌", f"Cannot fetch balance for {asset}")
			return None