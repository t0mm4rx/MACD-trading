# MACD crossover trading algo

> ⚠️ This code is directly connected to your exchange and your wallet. It deals with real money.
>
> ⚠️ This program is in progress. I strongly advise you to not run this for now.
> 
> ⚠️ This strategy is shit, it won't make money, for educational purpose only

This project is a bot trading Bitcoin using a really simple strategy.

All the decisions and positions are shared in live on a Twitter account: [@macd_bot](https://twitter.com/bot_macd).

## Algo

This algorithm is really simple:

- We fetch the latest data from the selected exchange
- We compute MACD
- We compute MACD crossovers
- If we cross, we open the position
- We wait for the opposite crossover
- We sell our position

## What's MACD

MACD is one of the most-used technical indicator.

You can compute MACD by subtracting EWM12 and EWM26 of the ticker.

We also use the MACD EWM9.

## How to use?

First, create a creds.json file at the root of the project. You can fill it like that:

```json
{
	"binance": {
		"apiKey": "XXX",
		"secret": "XXX"
	},
	"twitter": {
		"consumerKey": "XXX",
		"consumerSecret": "XXX",
		"accessToken": "XXX",
		"accessTokenSecret": "XXX"
	},
}
```

Then, create a .env file:
```sh
# To set in passive mode or not
PASSIVE_MODE=1

# Define the Grafana user/password
GF_SECURITY_ADMIN_USER=user
GF_SECURITY_ADMIN_PASSWORD=password
```

Then to run the project:
```sh
docker-compose up

# If you want to run it on your SSH server in deamon mode
docker-compose up -d
# To stop the project
docker-compose kill
```

## Contact me

Question? Support? Advice? ➡ DM [AirM4rx](https://twitter.com/AirM4rx) on Twitter.
