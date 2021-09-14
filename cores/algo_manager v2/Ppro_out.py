from pannel import *
from tkinter import ttk
import requests
import threading 
from constant import *
from Util_functions import *
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



def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data

def register(symbol,port):
	req = threading.Thread(target=register_to_ppro, args=(symbol, True,port,),daemon=True)
	req.start()

def register_web(symbol,port):

	postbody = "http://localhost:8080/SetOutput?symbol=" + symbol + "&feedtype=L1&output=" + str(port)+"&status=on"

	return postbody,"register "+symbol,"register failed "+symbol
	
def register_to_ppro(symbol,status,port):

	#log_print("Registering",symbol,status)
	if status == True:
		postbody = "http://localhost:8080/SetOutput?symbol=" + symbol + "&feedtype=L1&output=" + str(port)+"&status=on"
	else:
		postbody = "http://localhost:8080/SetOutput?symbol=" + symbol + "&feedtype=L1&output=" + str(port)+"&status=off"

	try:
		r= requests.get(postbody)
		if r.status_code==200:
			return True
		else:
			return False
	except:
		log_print("register failed")
		return False

def flatten_symbol(symbol):

	r = 'http://localhost:8080/Flatten?symbol='+str(symbol)
	sucess='flatten '+symbol+' Success!'
	failure='flatten '+symbol+' Failure.'

	return r,sucess,failure
	#req = threading.Thread(target=ppro_request, args=(r,sucess,failure,),daemon=True)
	#req.start()

def buy_market_order(symbol,share):


	r = 'http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=0.01&ordername=ARCA Buy ARCX Market DAY&shares='+str(share)
	sucess='buy market order success on'+symbol
	failure="Error buy order on"+symbol

	return r,sucess,failure
	#req = threading.Thread(target=ppro_request, args=(r,sucess,failure,),daemon=True)
	#req.start()

def sell_market_order(symbol,share):

	r = 'http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=0.01&ordername=ARCA Sell->Short ARCX Market DAY&shares='+str(share)
	sucess='sell market order success on'+symbol
	failure="Error sell order on"+symbol

	return r,sucess,failure

def buy_limit_order(symbol, price,share,wait=0):

	price = round(float(price),2)
	r = 'http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=ARCA Buy ARCX Limit DAY&shares='+str(share)
	#r = 'http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=MEMX Buy MEMX Limit DAY BookOnly&shares='+str(share)
	sucess='buy limit order success on'+symbol
	failure="Error buy limit order on"+symbol

	return r,sucess,failure


def sell_limit_order(symbol, price,share,wait=0):
	price = round(float(price),2)

	r = 'http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=ARCA Sell->Short ARCX Limit DAY&shares='+str(share)
	#r = 'http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=MEMX Sell->Short MEMX Limit DAY BookOnly&shares='+str(share)
	sucess='sell limit order success on'+symbol
	failure="Error sell limit order on"+symbol

	return r,sucess,failure


def buy_aggressive_limit_order(symbol,share,ask):

	#ask = ask*1.03
	if ask<2:
		ask = round((ask+0.02),2) 
	elif ask>=2 and ask<=10:
		ask = round((ask+0.05),2) 
	elif ask>10:
		ask = round((ask+0.1),2)  
	elif ask>100:
		ask = round((ask+0.2),2)

	r = 'http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice='+str(ask)+'&ordername=ARCA Buy ARCX Limit IOC&shares='+str(share)
	sucess='Agrresive limit buy order success on'+symbol
	failure="Error buy order on"+symbol

	return r,sucess,failure

def short_aggressive_limit_order(symbol,share,bid):

	#bid = bid*0.97

	if bid <2:
		bid = round((bid-0.02),2)
	elif bid>=2 and bid<=10:
		bid = round((bid-0.05),2) 
	elif bid>10:
		bid = round((bid-0.1),2)
	elif bid>100:
		bid = round((bid-0.2),2)

	r = 'http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice='+str(bid)+'&ordername=ARCA Sell->Short ARCX Limit IOC&shares='+str(share)
	sucess='Aggresive limit sell order success on'+symbol
	failure="Error buy order on"+symbol

	return r,sucess,failure



def stoporder_to_market_buy(symbol,price,share):

	price = round(float(price),2)
	r='http://localhost:8080/SendSwiftStop?symbol='+symbol+'&limitprice=0&ordername=ARCA%20Buy%20ARCX%20Market%20DAY&shares='+str(share)+'&referenceprice=ask&swiftstopprice='+str(price)
	sucess='stoporder buy market order success on '+symbol
	failure="Error stoporder buy market"+symbol
   
	return r,sucess,failure

def stoporder_to_market_sell(symbol,price,share):

	price = round(float(price),2)

	r= 'http://localhost:8080/SendSwiftStop?symbol='+symbol+'&ordername=ARCA%20Sell-%3EShort%20ARCX%20Market%20DAY&shares='+str(share)+'&referenceprice=bid&swiftstopprice='+str(price)
	sucess='stoporder sell market order success on '+symbol
	failure="Error sell order on"+symbol
   
	return r,sucess,failure

def cancel_all_oders(symbol):

	r = 'http://localhost:8080/CancelOrder?type=all&symbol='+str(symbol)+'&side=order'
	#r = 'http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=MEMX Sell->Short MEMX Limit DAY BookOnly&shares='+str(share)
	sucess='cancel success on'+symbol
	failure="cancel error on"+symbol

	return r,sucess,failure


def init_driver(pipe_status):

	while True:
		try:
			PATH = "sys/chromedriver.exe"

			#driver = webdriver.Chrome(ChromeDriverManager().install())
			driver = webdriver.Chrome(PATH)
			driver.minimize_window()
			pipe_status.send(["ppro_out","Connected"])
			return driver
		except Exception as e:
			log_print("Driver init failed. restarting.",e)
			pipe_status.send(["ppro_out","Disconnected"])
			time.sleep(1)
			pass

def Ppro_out(pipe,port,pipe_status): #a sperate process. GLOBALLY. 


	driver = init_driver(pipe_status)
	log_print("Orders output moudule online.")
	request_str = ""
	sucess_str= ""
	failure_str = ""
	while True:
		try:
			request_str = ""
			sucess_str= ""
			failure_str = ""
			d = pipe.recv()
			type_ = d[0]

			log_print("PPRO ORDER:",d)


			if type_ == BUY:

				symbol = d[1]
				share = d[2]
				rationale = d[3]

				request_str,sucess_str,failure_str=buy_market_order(symbol,share)

			elif type_ ==SELL:

				symbol = d[1]
				share = d[2]
				rationale = d[3]
				request_str,sucess_str,failure_str=sell_market_order(symbol,share)

			elif type_ ==IOCBUY:
				symbol = d[1]
				share = d[2]
				ask = d[3]
				#print("iocbuy",ask)
				now = datetime.now()
				ts = now.hour*60+now.minute

				if ts<570:
					request_str,sucess_str,failure_str=buy_aggressive_limit_order(symbol,share,ask)
				else:
					request_str,sucess_str,failure_str=buy_market_order(symbol,share)

			elif type_ ==IOCSELL:	
				symbol = d[1]
				share = d[2]
				bid = d[3]
				#print("iocsell",bid)
				now = datetime.now()
				ts = now.hour*60+now.minute

				if ts<570:
					request_str,sucess_str,failure_str=short_aggressive_limit_order(symbol,share,bid)
				else:
					request_str,sucess_str,failure_str=sell_market_order(symbol,share)
					
			elif type_ == LIMITBUY:

				symbol = d[1]
				price = round(d[2],2)
				share = d[3]
				wait = d[4]
				rationale = d[5]
				request_str,sucess_str,failure_str=buy_limit_order(symbol,price,share,wait)

			elif type_ == LIMITSELL:

				symbol = d[1]
				price = round(d[2],2)
				share = d[3]
				wait = d[4]
				rationale = d[5]

				request_str,sucess_str,failure_str=sell_limit_order(symbol,price,share,wait)

			elif type_ == CANCEL:

				symbol = d[1]

				request_str,sucess_str,failure_str=cancel_all_oders(symbol)


			elif type_ == REGISTER:

				symbol = d[1]
				#register(symbol,port)
				request_str,sucess_str,failure_str = register_web(symbol,port)

			elif type_ == STOPBUY:

				symbol = d[1]
				price = round(d[2],2)
				share = d[3]

				request_str,sucess_str,failure_str=stoporder_to_market_buy(symbol,price,share,wait)

			elif type_ == STOPSELL:

				symbol = d[1]
				price = round(d[2],2)
				share = d[3]

				request_str,sucess_str,failure_str=stoporder_to_market_sell(symbol,price,share,wait)

			elif type_ == FLATTEN:

				symbol = d[1]
				request_str,sucess_str,failure_str=flatten_symbol(symbol)
			else:

				log_print("Unrecognized ppro command received.")

			sucessful = False

			if request_str!="":
				while not sucessful:
					try:
						driver.get(request_str)
						log_print(sucess_str)
						sucessful = True
					except Exception as e:
						log_print(e,failure_str," driver restart")
						driver = init_driver(pipe_status)

		except Exception as e:
			log_print(e)


def ppro_request(request,success=None,failure=None,wait=0,traceid=False,symbol=None,side=None,pipe=None):
	failure = 0

	if wait!=0:
		time.sleep(wait)

	while True:
		r = requests.post(request)
		#print(r.text)
		if r.status_code ==200:
			# if success!=None:
			# 	log_print(success)
			if traceid==True:
				get_order_id(find_between(r.text,"<Content>","</Content>"),symbol,side,pipe)  #need to grab the request id. obtain the order id. assign it to the symbol.the 
			return True
		else:
			log_print(failure)
			#return False
			failure +=1

		if failure>4:
			break

	return False

def get_order_id(request_number,symbol,side,pipe):
	count=0
	while True:
		req = "http://localhost:8080/GetOrderNumber?requestid="+str(request_number)
		r = requests.post(req)
		if r.status_code ==200:
			#return id, symbol, and side. 
			log_print(symbol,side,"stop id aquired")
			pipe.send(["new stoporder",[find_between(r.text,"<Content>","</Content>"),symbol,side]])
			break
		else:
			count = count+1
			log_print(symbol,side,"get id failed:",count)



def get_stoporder_status(id_):

	req = 'http://localhost:8080/GetScriptState?scriptid='+id_
	r = requests.post(req)

	return (find_between(r.text,"<Content>","</Content>"))

def cancel_stoporder(id_):

	r="http://localhost:8080/CancelScript?scriptid="+str(id_)
	sucess='cancellation successful'
	failure="cancellation failed"

	req = threading.Thread(target=ppro_request, args=(r,sucess,failure),daemon=True)
	req.start()	


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