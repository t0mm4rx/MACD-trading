from MACD import MACD
import matplotlib.pyplot as plt

bot = MACD(False)

balance, pnl, hist = bot.backtest('2020-01-01T00:00:00', '2020-02-01T00:00:00')

fig, ax = plt.subplots(figsize=(30, 10))
ax.plot(hist['date'], hist['price'])
for i, row in hist[hist['action'] == 'buy'].iterrows():
	ax.scatter(row['date'], row['price'], marker='o', c='green', alpha=0.5)
for i, row in hist[hist['action'] == 'sell'].iterrows():
	ax.scatter(row['date'], row['price'], marker='o', c='red', alpha=0.5)
fig.savefig('./graphs/backtrack.png', bbox_inches='tight')
fig.clf()
plt.plot(balance)
plt.savefig("./graphs/balance.png")
plt.clf()
plt.hist(pnl, bins=20)
plt.savefig("./graphs/pnl_distrib.png")