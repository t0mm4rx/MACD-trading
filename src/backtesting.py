from MACD import MACD
import matplotlib.pyplot as plt

bot = MACD(False)

balance, pnl = bot.backtest('2019-01-01T00:00:00', '2019-01-05T00:00:00')

plt.plot(balance)
plt.savefig("./graphs/balance.png")
plt.clf()
plt.hist(pnl, bins=20)
plt.savefig("./graphs/pnl_distrib.png")