from lib.Exchange import Exchange
from lib.Logger import Logger
import time

log = Logger("MACD")

log.balance(100, "USDT")

# exchange = Exchange(log, 10, "BTC/USDT", "1m")
# exchange.buy()
# exchange.sell()

# log.order('buy', 60123, 31)
# time.sleep(10)
# log.order('sell', 61003, 36)
# time.sleep(20)
# log.order('buy', 61129, 33)
# time.sleep(13)
# log.order('sell', 60890, 29)

# log.pnl(0.1, 20)
# time.sleep(10)
# log.pnl(-0.4, -6)
# time.sleep(20)
# log.pnl(1.4, 130)