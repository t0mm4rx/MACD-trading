from lib.Data import Data
from lib.Logger import Logger
from lib.Exchange import Exchange
import lib.config as config
import datetime
import time
import pandas as pd

period_matching = {
	'1m': 1,
	'3m': 3,
	'5m': 5,
	'15m': 15,
	'30m': 30,
	'1h': 1 * 60,
	'2h': 2 * 60,
	'3h': 3 * 60,
	'4h': 4 * 60,
	'1d': 1 * 60 * 24,
	'1w': 7 * 60 * 24,
}

class Bot:
	"""This class is an instance of a bot.
	Every bot has a name, a ticker, and period.
	The period can be 1m, 3m, 5m, 15m, 30m, 1h, 2h, 3h, 4h, 1d, 1w.
	A bot can have a period_needed property that will specify how much past data you want at least
	at every loop.
	
	Example: a bot with a time period of 5m and a period_needed of 200 will receive at every loop the 200
	last ticker, 1000 minutes.

	To implement a bot, you just have to override the compute and setup function. Those two functions will be
	called automatically by the timing system.
	Compute will receive the last period_needed candles for the selected asset.

	The data property is a Data object that allows you to store important and persistant information.
	Every important variables or objects should be stored in data, in case the bot is restarted or if the server is down.

	The logger property is an instance of Logger. It allows you to log information in the console and in the
	database and the Dashboard. If you want to log custom metrics, use logger.custom. You will be able to create
	visualizations in Grafana with this logs.

	The config property is the dictionnary with the same name as the bot in the config.

	The exchange property is an instance of Exchange. It allows you to interact with the actual markets.

	The live_mode property indicates if the bot should loop and receive live data. Use it only to test your bot
	live. If you want to backtrack or test your algorithm, leave live_mode = False.
	When live_mode is False, the logger won't log to the DB, and the exchange actions will be simulated.
	"""

	def __init__(self, name, ticker, period, live_mode, periods_needed=200):
		"""
		- name: string, the name of the bot
		- ticker: string, the ticker formatted like that: ASSET1/ASSET2
		- period: string, the period on which the loop will be set, and the resolution of the candles
		- live_mode: bool, should we launch the live loop and start trading live
		- periods_needed: int, the number of candles you will get every loop, optional
		"""
		self.live_mode = live_mode
		self.name = name
		self.ticker = ticker
		self.period_text = period
		self.periods_needed = periods_needed
		self.offset_seconds = 10
		if (not self.name in config.get_config()):
			print("❌ Cannot instantiate bot: no config entry")
			exit(1)
		self.config = config.get_config()[self.name]
		if (not "capitalAllowed" in self.config):
			print("❌ Cannot instantiate bot: no 'capitalAllowed' property")
			exit(1)
		try:
			self.logger = Logger(self.name, live_mode)
		except:
			print("❌ Cannot connect to the log DB, are you sure it's running?")
			raise
		if (self.live_mode):
			self.data = Data(self.name)
		else:
			self.data = Data(self.name + "-test")
		self.exchange = Exchange(self.logger, self.data, self.config['capitalAllowed'], live_mode, self.ticker, self.period_text)
		try:
			self.period = period_matching[period]
		except:
			print("Available periods: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 3h, 4h, 1d, 1w")
			raise
		self.logger.log("ℹ️", f"Bot {self.name} started with a period of {period}")
		self.logger.log("ℹ️", f"Capital allowed: {self.config['capitalAllowed']}%")
		self.setup()
		if (self.live_mode):
			self.preloop()

	def preloop(self):
		"""Waits for the selected period to begin. We use UTC time.
		"""
		while (1):
			current_time = datetime.datetime.utcnow()
			if (self.period < 60):
				if (current_time.minute % self.period == 0 and current_time.second == self.offset_seconds):
					self.loop()
			elif (self.period <= 4 * 60):
				hour_offset = int(self.period / 60)
				if (current_time.hour % hour_offset == 0 and current_time.minute == 0 and current_time.second == self.offset_seconds):
					self.loop()
			elif (self.period <= 1 * 60 * 24):
				if (current_time.hour == 0
					and current_time.minute == 0
					and current_time.second == self.offset_seconds):
					self.loop()
			else:
				if (current_time.weekday() == 0
					and current_time.hour == 0
					and current_time.minute == 0
					and current_time.second == self.offset_seconds):
					self.loop()

	def loop(self):
		"""Once we waited for the period to start, we can loop over the periods. At every period we
		call compute with the latest data.
		"""
		while (1):
			current_time = datetime.datetime.utcnow()
			self.logger.log("ℹ️", f"Downloading latest data at {current_time}")
			data = self.exchange.get_latest_data(self.ticker, self.period_text, self.periods_needed)
			self.logger.price(data.iloc[-1]['close'])
			self.compute(data)
			time.sleep(self.offset_seconds + self.period * 60 - datetime.datetime.now().second)

	def backtest(self, start_date, end_date):
		self.exchange.init_fake_balance()
		self.data.reset()
		price = []
		date = []
		data = self.exchange.get_data(start_date, end_date, self.ticker, self.period_text)
		if (data.shape[0] == 0):
			self.logger.log("❌", "No data for the given time frame")
		for i in range(self.periods_needed, data.shape[0]):
			batch = data.iloc[i - self.periods_needed:i]
			self.exchange.fake_current_price = batch.iloc[-1]['close']
			self.exchange.fake_current_date = batch.iloc[-1]['date']
			price.append(batch.iloc[-1]['close'])
			date.append(batch.iloc[-1]['date'])
			self.compute(batch.copy())
		hist = pd.DataFrame()
		hist['date'] = date
		hist['price'] = price
		for order in self.exchange.fake_orders:
			hist.loc[hist['date'] == order['date'], 'action'] = order['action']
		return (self.exchange.fake_balance, self.exchange.fake_pnl, hist)

	def setup(self):
		"""To implement. Set the bot variable, instantiate classes... This will be done once before the bot
		starts.
		"""
		pass

	def compute(self, data):
		"""To implement. Called every period, you have the latest data available. You can here take decisions.
		"""
		pass