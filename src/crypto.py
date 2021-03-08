import pandas as pd
import numpy as np
import ccxt
import json

exchange = None

def connect():
	global exchange
	creds = json.loads(open("./creds.json", "r").read())
	exchange = ccxt.binance(creds['binance'])

def get_balance():
	return exchange.fetch_balance()['USDT']['total']

def get_live_data():
	# Fetch latest data
	candles = np.array(exchange.fetch_ohlcv("BTC/USDT", '5m'))
	
	# Format data into a dataframe
	data = pd.DataFrame()
	data['timestamp'] = candles[:, 0]
	data['date'] = pd.to_datetime(data['timestamp'] * 1000000)
	data['open'] = candles[:, 1]
	data['high'] = candles[:, 2]
	data['low'] = candles[:, 3]
	data['close'] = candles[:, 4]
	data['volume'] = candles[:, 5]

	# Calculate MACD
	ewm12 = data['close'].ewm(span=12, adjust=False).mean()
	ewm26 = data['close'].ewm(span=26, adjust=False).mean()
	macd = ewm12 - ewm26
	macd9 = macd.ewm(span=9, adjust=False).mean()
	data['macd'] = macd
	data['macd9'] = macd9

	# Calculate MACD crossovers
	macd9_shifted = data['macd9'].shift(1)
	macd_shifted = data['macd'].shift(1)
	crossovers_buy = (macd_shifted < macd9_shifted) & (data['macd'] >= data['macd9'])
	data['crossover_buy'] = crossovers_buy
	crossovers_sell = (macd_shifted > macd9_shifted) & (data['macd'] <= data['macd9'])
	data['crossover_sell'] = crossovers_sell

	return data
