if (__name__ == "__main__"):
	exit(1)

import pandas as pd
import numpy as np
import ccxt
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

exchange = None

def connect():
	global exchange
	creds = json.loads(open("./creds.json", "r").read())
	exchange = ccxt.binance(creds['binance'])

def get_balance():
	return exchange.fetch_balance()['USDT']['total']

def get_live_data():
	# Fetch latest data
	candles = np.array(exchange.fetch_ohlcv("BTC/USDT", '1m'))
	
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

def plot_data(data):
	fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(20, 20))
	ax1.plot(data['date'], data['close'])
	ax2.plot(data['date'], data['volume'])
	ax3.plot(data['date'], data['macd'])
	ax3.plot(data['date'], data['macd9'])
	ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))

	for _, row in data.iterrows():
		if (row['crossover_buy']):
			ax3.scatter(row['date'], row['macd'], color='b')
			ax1.scatter(row['date'], row['close'], color='b')
		if (row['crossover_sell']):
			ax3.scatter(row['date'], row['macd'], color='r')
			ax1.scatter(row['date'], row['close'], color='r')
	fig.savefig("./graphs/latest_analyse.png")
	plt.close()
	plt.clf()

def buy():
	balance = get_balance()
	proportion = 0.5
	price = get_live_data().iloc[-1]['close']
	amount = (balance * proportion) / price
	amount = exchange.amount_to_precision("BTC/USDT", amount)
	return exchange.create_market_buy_order("BTC/USDT", amount)

def sell():
	balance = exchange.fetch_balance()['BTC']['total']
	return exchange.create_market_sell_order("BTC/USDT", balance)