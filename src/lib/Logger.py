import influxdb
import lib.config as config

class Logger:
	"""This class is used to log data to the console and to the database.
	It can be used to visualize data in the dashboard, and have a clear understanding of your
	algorithm.
	"""

	db_name = "cryptotrading"

	def __init__(self, name):
		"""Connect to the DB, create the table if it doesn't exist yet.

		- name: string, the name of the bot which will be logging
		"""
		self.name = name
		self.client = influxdb.InfluxDBClient(
			host=config.get_config()['influxdb'], username=config.get_creds()['influxdb']['user'], password=config.get_creds()['influxdb']['password']
		)
		dbs = self.client.get_list_database()
		found = False
		for db in dbs:
			if (db['name'] == self.db_name):
				found = True
		if (not found):
			self.client.create_database(self.db_name)
		self.client.switch_database(self.db_name)

	def price(self, price):
		"""Log the latest asset price. It will be called automatically by the Bot class.

		- price: float, the current price of the traded asset
		"""
		try:
			self.client.write_points([{
				"measurement": "asset_price",
				"fields": {
					"price": price
				},
				"tags": {
					"bot": self.name
				}
			}])
		except:
			print("❌ Cannot log price to the database")

	def log(self, emoji, message):
		"""Simple text log that will be printed in the console and the database.
		You have to specify a message and an emoji, because it's prettier.

		- emoji: single character string, unicode emoji
		- message: the message to log
		"""
		print(f"{emoji} {message}")
		try:
			self.client.write_points([{
				"measurement": "log",
				"fields": {
					"emoji": emoji,
					"message": message
				},
				"tags": {
					"bot": self.name
				}
			}])
		except:
			print("❌ Cannot log to the database")

	def custom(self, name, fields):
		"""Logs a custom event to the DB. It can be used to create custom live visualizations in the dashboard.

		- name: string, the name of the data to log
		- fields: a dictionnary, containing all the data you want to log

		Example: you have a simple MACD bot, you want to monitor live the MACD crossovers.
		self.logger.log("macd", {
			'macd_short': value_short,
			'macd_long': value_long,
		})
		"""
		try:
			self.client.write_points([{
				"measurement": name,
				"fields": fields,
				"tags": {
					"bot": self.name
				}
			}])
		except:
			print("❌ Cannot log custom event to the database")

	def balance(self, balance, currency="USDT"):
		"""Logs the current account balance. Called in the Bot loop.

		- balance: float, the balance quantity
		- currency: string, the balance currency, optional
		"""
		try:
			self.client.write_points([{
				"measurement": "balance",
				"fields": {
					"balance": balance,
					"currency": currency
				},
				"tags": {
					"bot": self.name
				}
			}])
		except:
			print("❌ Cannot log balance to the database")

	def pnl(self, percentage, currency):
		"""Logs PNL (profits and losses) for a trade. Called after a trade, to monitor your performance.

		- percentage: float, the trade performance in percentage of the invested capital
		- currency: float, the trade return in the base currency

		Example: you're trading on BTC/USDT, you buy at 1000$ and you sell at 1100$. The percentage will
		be 0.1 and the currency profit 100$.
		"""
		try:
			self.client.write_points([{
				"measurement": "pnl",
				"fields": {
					"percentage": percentage,
					"currency": currency
				},
				"tags": {
					"bot": self.name
				}
			}])
		except:
			print("❌ Cannot log pnl to the database")

	def order(self, way, price, cost):
		"""Logs an order on the market.

		- way: string, 'buy' or 'sell'
		- price: float, the order asset price
		- cost: float, what you paid or received

		Example: you buy BTC at 2113$ with 20$
		self.logger.order('buy', 2113, 20)

		Example: you sell BTC at 2230$ with 30$
		self.logger.order('sell', 2230, 30)
		"""
		try:
			self.client.write_points([{
				"measurement": "order",
				"fields": {
					"way": way,
					"price": price,
					"cost": cost
				},
				"tags": {
					"bot": self.name
				}
			}])
		except:
			print("❌ Cannot log order to the database")