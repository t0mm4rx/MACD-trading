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

def price(timestamp, value):
	global client

	try:
		client.write_points([{
			"measurement": "price",
			"fields": {
				"value": value
			},
			"timestamp": timestamp
		}], time_precision='ms')
	except:
		print("❌ Cannot send data to the database")

def macd(macd1, macd2):
	pass