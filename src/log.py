if (__name__ == "__main__"):
	exit(1)

import influxdb
import json

client = None

def connect(name):
	global client

	config = json.load(open("./config.json", "r"))
	client = influxdb.InfluxDBClient(host=config['influxdb'])
	
	dbs = client.get_list_database()
	found = False
	for db in dbs:
		if (db['name'] == name):
			found = True
	if (not found):
		client.create_database(name)
	client.switch_database(name)
	client.ping()

def log(emoji, message):
	global client

	print("{} {}".format(emoji, message))
	try:
		client.write_points([
			{
				"measurement": "log",
				"fields": {
					"emoji": emoji,
					"message": message
				}
			}
		])
	except:
		print("❌ Cannot send data to the database")

def price(timestamp, value, macd, macd9):
	global client

	try:
		client.write_points([{
			"measurement": "price",
			"fields": {
				"value": value,
				"macd": macd,
				"macd9": macd9
			},
			"timestamp": timestamp
		}], time_precision='s')
	except:
		print("❌ Cannot send data to the database")

def pnl(usdt, percentage, true_percentage):
	global client

	try:
		client.write_points([{
			"measurement": "pnl",
			"fields": {
				"usdt": float(usdt),
				"percentage": float(percentage),
				"true_percentage": float(true_percentage)
			},
		}], time_precision='s')
	except:
		print("❌ Cannot send data to the database")

def order(way, price, cost):
	global client

	try:
		client.write_points([{
			"measurement": "order",
			"fields": {
				"price": price,
				"cost": cost,
				"way": way
			},
		}], time_precision='s')
	except:
		print("❌ Cannot send data to the database")
