# MACD crossover trading algo

> ⚠️ This code is directly connected to your exchange and your wallet. It deals with real money.
>
> ⚠️ This program is in progress. I strongly advise you to not run this for now.

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
	}
}
```

## Contact me

Question? Support? Advice? ➡ DM [AirM4rx](https://twitter.com/AirM4rx) on Twitter.