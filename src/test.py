import crypto
import time

crypto.connect()

# print(crypto.get_live_data().iloc[-1])

# print(crypto.buy())

print(crypto.get_balance())

print(crypto.buy())
time.sleep(30)
print(crypto.sell())

print(crypto.get_balance())