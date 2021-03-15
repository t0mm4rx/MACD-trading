from lib.Bot import Bot

class MACD(Bot):

	def __init__(self):
		super().__init__("MACD", "BTC/USDT", "1m")

	def setup(self):
		pass

	def compute(self, candles):

		# Compute MACD
		ewm12 = candles['close'].ewm(span=12, adjust=False).mean()
		ewm26 = candles['close'].ewm(span=26, adjust=False).mean()
		macd = ewm12 - ewm26
		macd9 = macd.ewm(span=9, adjust=False).mean()
		candles['macd'] = macd
		candles['macd9'] = macd9

		# Creating signals
		macd9_shifted = candles['macd9'].shift(1)
		macd_shifted = candles['macd'].shift(1)
		crossovers_buy = (macd_shifted < macd9_shifted) & (candles['macd'] >= candles['macd9'])
		candles['crossover_buy'] = crossovers_buy
		crossovers_sell = (macd_shifted > macd9_shifted) & (candles['macd'] <= candles['macd9'])
		candles['crossover_sell'] = crossovers_sell

		# Taking a decision
		should_buy = candles.iloc[-1]['crossover_buy'] or candles.iloc[-2]['crossover_buy']
		should_sell = candles.iloc[-1]['crossover_sell'] or candles.iloc[-2]['crossover_sell']

		# We log our calculations to monitor
		self.logger.custom('macd', {
			'macd_short': candles.iloc[-1]['macd'],
			'macd_long': candles.iloc[-1]['macd9'],
			'buy_signal': should_buy,
			'sell_signal': should_sell
		})