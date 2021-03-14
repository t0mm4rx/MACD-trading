import ccxt

class Exchange:

	def __init__(self, name, exchange, logger):
		self.name = name
		self.exchange = exchange
		self.logger = logger