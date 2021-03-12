import crypto
import twitter
import datetime
import pickle
import time
import log
import os
import json

def set_variable(key, value):
	global variables

	variables[key] = value
	pickle.dump(variables, open("./data/variables.pickle", "wb+"))

def buy():
	global variables, config

	log.log("🤞", "Buy signal")
	set_variable('last_buy_balance', crypto.get_balance())
	trade = crypto.buy()
	set_variable('last_buy_price', trade['price'])
	log.log("💵", "Bought $BTC@{:.2f}".format(trade['price']))
	if (config['tweet']):
		twitter.tweet("🤞 I bought {} $BTC at {:.2f}$ for {:.2f}$.\n💵 My current balance is {:.2f}$.".format(
			trade['amount'],
			trade['price'],
			trade['cost'],
			variables['last_buy_balance']
		))
	log.order("buy", trade['price'], trade['cost'])
	log.log("⏳", "Now waiting to sell...")

def sell():
	global variables

	log.log("⚠️", "Sell signal")
	trade = crypto.sell()
	log.log("💵", "Sold $BTC @{:.2f}".format(trade['price']))
	log.order("sell", trade['price'], trade['cost'])
	balance = crypto.get_balance()
	profit = balance - variables['last_buy_balance']
	profit_percentage = profit / variables['last_buy_balance'] * 100
	true_percentage = ((trade['price'] - variables['last_buy_price']) / variables['last_buy_price']) * 100
	if (profit > 0):
		log.log("📈", "Profit: +{:.2f}$, +{:.2f}%".format(profit, profit_percentage))
		if (config['tweet']):
			twitter.tweet("🚀 I sold my $BTC at {:.2f}$ for {:.2f}$!\n📈 I won +{:.2f}$ (+{:.2f}%).\n💵 My current balance is {:.2f}$.".format(
				trade['price'],
				trade['cost'],
				profit,
				profit_percentage,
				balance
			))
	else:
		log.log("📉", "Loss: {:.2f}$, {:.2f}%".format(profit, profit_percentage))
		if (config['tweet']):
			twitter.tweet("😕 I sold my $BTC at {:.2f}$ for {:.2f}$!\n📉 I lost {:.2f}$ ({:.2f}%).\n💵 My current balance is {:.2f}$.".format(
				trade['price'],
				trade['cost'],
				profit,
				profit_percentage,
				balance
			))
	set_variable('last_buy_balance', None)
	set_variable('last_buy_price', None)
	log.pnl(profit, profit_percentage, true_percentage)

def check_macd():
	global variables, config

	data = crypto.get_live_data()
	should_buy = data.iloc[-1]['crossover_buy'] or data.iloc[-2]['crossover_buy']
	should_sell = data.iloc[-1]['crossover_sell'] or data.iloc[-2]['crossover_sell']
	if (variables['last_buy_balance'] != None and should_sell and not config['passive']):
		sell()
	if (variables['last_buy_balance'] == None and should_buy and not config['passive']):
		buy()
	crypto.plot_data(data)
	log.price(data.iloc[-1]['timestamp'], data.iloc[-1]['close'], data.iloc[-1]['macd'], data.iloc[-1]['macd9'])

config = json.load(open("./config.json"))

# Connecting to the different services
print("ℹ️  Connecting to the log database")
log.connect("macd_bot")
log.log("✅", "Connected to the log database")
log.log("ℹ️", "Connecting to the exchange...")
crypto.connect()
if (config['tweet']):
	log.log("ℹ️", "Connecting to Twitter...")
	twitter.connect()
log.log("✅", "Connected to the exchange and Twitter")

if (config['passive']):
	log.log("👁", "Started in passive mode, won't take any decision")

# Globals
try:
	variables = pickle.load(open("./data/variables.pickle", "rb"))
	if (variables['last_buy_balance'] != None):
		log.log("❗️", "The script has been interrupted with an open position")
except:
	variables = {}
	set_variable('last_buy_balance', None)
	set_variable('last_buy_price', None)

offset_seconds = 10
frequency = 30
while True:
	current_time = datetime.datetime.now()
	if (current_time.second == offset_seconds and current_time.minute % 30 == 0):
		while True:
			current_time = datetime.datetime.now()
			log.log("ℹ️", "Checking for {}".format(current_time))
			check_macd()
			time.sleep(offset_seconds + frequency * 60 - datetime.datetime.now().second)
