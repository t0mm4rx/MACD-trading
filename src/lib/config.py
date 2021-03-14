import json

def get_creds():
	return json.load(open("./creds.json"))

def get_config():
	return json.load(open("./config.json"))