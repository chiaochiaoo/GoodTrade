import requests
import time 



# for i in range(100):
# 	req = "https://tnv.ngrok.io/Basket=DTEST"+str(i)+",Order=*QQQ.NQ:1*"

# 	requests.get(req)


# for i in range(100):
# 	req = "https://tnv.ngrok.io/Basket=DTEST"+str(i+100)+",Order=*SPY.NQ:-1*"

# 	requests.get(req)


for i in range(20):
	req = "https://tnv.ngrok.io/Basket=DTEST"+str(i+300)+",Order=*TQQQ.NQ:1*"

	requests.get(req)

time.sleep(3)