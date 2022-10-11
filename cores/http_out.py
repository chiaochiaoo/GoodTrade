import requests
import threading 
import time
from datetime import datetime
import numpy as np
import socket

try:
	from bs4 import BeautifulSoup
except ImportError:
	import pip
	pip.main(['install', 'BeautifulSoup4'])
	from bs4 import BeautifulSoup

try:
	from selenium import webdriver
	#from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
	import pip
	#pip.main(['install', 'webdriver-manager'])
	pip.main(['install', 'selenium'])
	from selenium import webdriver

#Thoughts:
#Combine PPRO sutff with VOXCOM into one process.
#Create subclass for the algo manager.
#Entry strategy
#Manage strategy
#How to get the machine to read chart?
#DATA CLASS. SUPPORT/RESISTENCE.
#everything ppro related. sending orders, receiving orders. ,flatten.


def init_driver():

	while True:
		try:
			PATH = "cores/sys/chromedriver.exe"
			#driver = webdriver.Chrome(ChromeDriverManager().install())
			driver = webdriver.Chrome(PATH)
			driver.minimize_window()
			return driver
		except Exception as e:
			print("Driver init failed. restarting.",e)
			time.sleep(1)
			pass

def http_driver(pipe): #a sperate process. GLOBALLY. 

	driver = init_driver()
	print("Orders output moudule online.")
	termination = False
	while True and not termination:
		try:
			d = pipe.recv()

			try:
				driver.get(d)
				#log_print(sucess_str)
				sucessful = True
			except Exception as e:
				print(e,failure_str," driver restart")
				driver = init_driver()

		except Exception as e:
			print(e)

	print("ppro out terminated")


#return (find_between(r.text,"<Content>","</Content>"))
# symbol="QQQ.NQ"
# offset = 0.01
# share = 1
# a='http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=MEMX Buy MEMX Limit Near Visible DAY PostOnly&shares='+str(share)
# print(a)

# request = 

# r = requests.post(request)


# if __name__ == '__main__':  #TEST BLOCK
# 	PATH = "sys/chromedriver.exe"
# 	driver = webdriver.Chrome(PATH)
# 	# postbody = "http://localhost:8080/SetOutput?region=1&feedtype=OSTAT&output=4040&status=on"
# 	# r= requests.get(postbody)

# 	req = threading.Thread(target=test, args=(),daemon=True)
# 	req.start()
# 	global lst
# 	lst = []
# 	A=["NIO.NY","SPY.AM"]
# 	for i in range(20):
# 		global now 
# 		now = datetime.now()
# 		#dt = datetime.now().strftime('%M:%S.%f')[:-4]
# 		#print(dt)
# 		#buy_market_order("NIO.NY",1)
# 		current = i%2
# 		driver.get('http://localhost:8080/ExecuteOrder?symbol='+A[current]+'&limitprice=0.01&ordername=MEMX Buy MEMX Market DAY&shares=1')
# 		#time.sleep(1)
# 	while True:
# 		time.sleep(1)


	#sell_market_order("AAL.NQ",1)

	# def register(self,symbol):

			
	# def deregister(self,symbol):

	# 	if symbol in self.symbols:
	# 		self.symbols.remove(symbol)
	# 		self.register_to_ppro(symbol, False)

	# def register_to_ppro(self,symbol,status):

	# 	log_print("Registering",symbol,status)
	# 	if status == True:
	# 		postbody = "http://localhost:8080/SetOutput?symbol=" + symbol + "&region=1&feedtype=L1&output=" + str(self.port)+"&status=on"
	# 	else:
	# 		postbody = "http://localhost:8080/SetOutput?symbol=" + symbol + "&region=1&feedtype=L1&output=" + str(self.port)+"&status=off"

	# 	try:
	# 		r= requests.get(postbody)
	# 		if r.status_code==200:
	# 			return True
	# 		else:
	# 			return False
	# 	except:
	# 		log_print("register failed")
	# 		return False

	# def flatten_symbol(self,symbol,id_=None,status_text=None):

	# 	#check if this order is running.
	# 	running = self.check_order_running(id_,symbol)

	# 	#send once is good enough. 
	# 	if running:
	# 		flatten = threading.Thread(target=flatten_symbol,args=(symbol,), daemon=True)
	# 		flatten.start()
	# 		#self.current_share_data[id_]=0

	# 	else:
	# 		if id_!= None and status_text!= None:
	# 			if id_ in self.orders_registry:
	# 				self.orders_registry.remove(id_)

	# 				#if current order is not running. 
	# 				self.mark_off_algo(id_,self.status["Canceled"])
	# 				# current_status = status_text.get()
	# 				# if current_status=="Pending":
	# 				# 	status_text.set("Canceled")
	# 				# 	self.modify_algo_count(-1)
	# 				# else:
	# 				# 	status_text.set("Done.")


# def buy_limit_order(symbol, price,share,wait=0):

# 	price = round(float(price),2)
# 	r = 'http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=ARCA Buy ARCX Limit DAY&shares='+str(share)
# 	#r = 'http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=MEMX Buy MEMX Limit DAY BookOnly&shares='+str(share)
# 	sucess='buy limit order success on'+symbol
# 	failure="Error buy limit order on"+symbol

# 	req = threading.Thread(target=ppro_request, args=(r,sucess,failure,wait,),daemon=True)
# 	req.start()

# def sell_limit_order(symbol, price,share,wait=0):
# 	price = round(float(price),2)

# 	r = 'http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=ARCA Sell->Short ARCX Limit DAY&shares='+str(share)
# 	#r = 'http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=MEMX Sell->Short MEMX Limit DAY BookOnly&shares='+str(share)
# 	sucess='sell limit order success on'+symbol
# 	failure="Error sell limit order on"+symbol

# 	req = threading.Thread(target=ppro_request, args=(r,sucess,failure,wait,),daemon=True)
# 	req.start()

# def Ppro_outx(pipe,port): #a sperate process. GLOBALLY. 
# 	while True:
# 		try:
# 			d = pipe.recv()
# 			type_ = d[0]

# 			log_print("PPRO ORDER:",d)
# 			if type_ == BUY:

# 				symbol = d[1]
# 				share = d[2]
# 				rationale = d[3]

# 				buy_market_order(symbol,share)

# 			elif type_ ==SELL:

# 				symbol = d[1]
# 				share = d[2]
# 				rationale = d[3]
# 				sell_market_order(symbol,share)

# 			elif type_ == LIMITBUY:
				
# 				symbol = d[1]
# 				price = round(d[2],2)
# 				share = d[3]
# 				wait = d[4]
# 				rationale = d[5]
# 				buy_limit_order(symbol,price,share,wait)

# 			elif type_ == LIMITSELL:

# 				symbol = d[1]
# 				price = round(d[2],2)
# 				share = d[3]
# 				wait = d[4]
# 				rationale = d[5]

# 				sell_limit_order(symbol,price,share,wait)


# 			elif type_ == "Register":

# 				symbol = d[1]
# 				#register(symbol,port)
# 				register_web(symbol,port)

# 			elif type_ == FLATTEN:

# 				symbol = d[1]
# 				flatten_symbol(symbol)
# 			else:

# 				log_print("Unrecognized ppro command received.")

# 		except Exception as e:
# 			log_print(e)


####need to trace the order number to trace the stop id number. 
# def stoporder_to_market_buy(symbol,price,share,pipe=None):

# 	price = round(float(price),2)
# 	r='http://localhost:8080/SendSwiftStop?symbol='+symbol+'&limitprice=0&ordername=ARCA%20Buy%20ARCX%20Market%20DAY&shares='+str(share)+'&referenceprice=ask&swiftstopprice='+str(price)
# 	sucess='stoporder buy market order success on '+symbol
# 	failure="Error stoporder buy market"+symbol
   
# 	req = threading.Thread(target=ppro_request, args=(r,sucess,failure,True,symbol,"B",pipe),daemon=True)
# 	req.start()



# def stoporder_to_market_sell(symbol,price,share,pipe=None):

# 	price = round(float(price),2)

# 	r= 'http://localhost:8080/SendSwiftStop?symbol='+symbol+'&ordername=ARCA%20Sell-%3EShort%20ARCX%20Market%20DAY&shares='+str(share)+'&referenceprice=bid&swiftstopprice='+str(price)
# 	sucess='stoporder sell market order success on '+symbol
# 	failure="Error sell order on"+symbol
   
# 	req = threading.Thread(target=ppro_request, args=(r,sucess,failure,True,symbol,"S",pipe),daemon=True)
# 	req.start()

