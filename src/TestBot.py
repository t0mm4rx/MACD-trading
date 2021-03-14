from lib.Bot import Bot

class TestBot(Bot):

	def __init__(self):
		super().__init__("TestBot", "BTC/USDT", "1m")

	def setup(self):
		pass

	def compute(self, candles):
		print(candles)