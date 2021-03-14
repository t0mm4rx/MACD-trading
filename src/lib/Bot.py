from Data import Data
from Logger import Logger
import datetime
import time

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

	The exchange property is an instance of Exchange. It allows you to interact with the actual markets.
	"""

	def __init__(self, name, ticker, period, period_needed=None):
		self.name = name
		self.ticker = ticker
		self.period_text = period
		self.period_needed = period_needed
		self.offset_seconds = 10
		self.logger = Logger(self.name)
		self.data = Data(self.name)
		try:
			self.period = period_matching[period]
		except:
			print("Available periods: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 3h, 4h, 1d, 1w")
			raise
		self.logger.log("ℹ️", f"Bot {self.name} started with a period of {period}")
		self.setup()
		self.loop()

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
			pass

	def setup(self):
		"""To implement. Set the bot variable, instantiate classes... This will be done once before the bot
		starts.
		"""
		pass

	def compute(self, data):
		"""To implement. Called every period, you have the latest data available. You can here take decisions.
		"""
		pass