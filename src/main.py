import crypto
import twitter
import datetime
import pickle
import time

def set_last_buy_balance(value):
	global last_buy_balance

	last_buy_balance = value
	pickle.dump(last_buy_balance, open("./data/last_buy_balance.pickle", "wb"))


def buy():
	global last_buy_balance

	print("🤞 Buy signal")
	set_last_buy_balance(crypto.get_balance())
	trade = crypto.buy()
	print("💵 Bought $BTC@{:.2f}".format(trade['price']))
	twitter.tweet("🤞 I bought {} $BTC for {:.4f}$ at {:.2f}$.\n💵 My current balance is {:.2f}$.".format(
		trade['amount'],
		trade['cost'],
		trade['price'],
		last_buy_balance
	))
	print("⏳ Now waiting to sell...")

def sell():
	global last_buy_balance

	print("⚠️ Sell signal")
	trade = crypto.sell()
	print("💵 Sold $BTC @{:.2f}".format(trade['price']))
	balance = crypto.get_balance()
	profit = balance - last_buy_balance
	profit_percentage = profit / last_buy_balance * 100
	if (profit > 0):
		print("📈🚀 Profit: +{:.2f}$, +{:.2f}%".format(profit, profit_percentage))
		twitter.tweet("🚀 I sold my $BTC at {:.2f}$ for {:.2f}$!\n📈 I won +{:.2f}$ (+{:.2f}%).\n💵 My current balance is {:.2f}$.".format(
			trade['price'],
			trade['cost'],
			profit,
			profit_percentage,
			balance
		))
	else:
		print("📉😕 Loss: {:.2f}$, {:.2f}%".format(profit, profit_percentage))
		twitter.tweet("😕 I sold my $BTC at {:.4f}$ for {:.4f}$!\n📉 I lost {:.2f}$ ({:.2f}%).\n💵 My current balance is {:.2f}$.".format(
			trade['price'],
			trade['cost'],
			profit,
			profit_percentage,
			balance
		))
	set_last_buy_balance(None)

def check_macd():
	global last_buy_balance

	data = crypto.get_live_data()
	print(data)
	should_buy = data.iloc[-1]['crossover_buy'] or data.iloc[-2]['crossover_buy']
	should_sell = data.iloc[-1]['crossover_sell'] or data.iloc[-2]['crossover_sell']
	print("last_buy_balance", last_buy_balance)
	print("should_buy", should_buy)
	print("should_sell", should_sell)
	print("cond1", last_buy_balance == None and should_buy)
	print("cond1", last_buy_balance != None and should_sell)
	if (last_buy_balance != None and should_sell):
		sell()
	if (last_buy_balance == None and should_buy):
		buy()
	crypto.plot_data(data)

print("ℹ️  Connecting to the exchange...")
crypto.connect()
print("ℹ️  Connecting to Twitter...")
twitter.connect()
print("✅ Connected to the exchange and Twitter")

# Globals
try:
	last_buy_balance = pickle.load(open("./data/last_buy_balance.pickle", "rb"))
	if (last_buy_balance != None):
		print("❗️ The script has been interrupted with an open position")
except:
	set_last_buy_balance(None)

# sell()
# exit()

while True:
	current_time = datetime.datetime.now()
	if (current_time.second == 10 and current_time.minute % 1 == 0 and current_time.microsecond == 0):
		while True:
			current_time = datetime.datetime.now()
			print("ℹ️  Checking for {}".format(current_time))
			check_macd()
			time.sleep(80 - datetime.datetime.now().second)
