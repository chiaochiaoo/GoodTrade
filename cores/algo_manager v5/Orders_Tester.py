import requests
import time 



for i in range(10):
	req = "https://tnv.ngrok.io/Basket=DTEST"+str(i)+",Order=*QQQ.NQ:1*"

	requests.get(req)


time.sleep(3)