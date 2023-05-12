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

# try:
# 	from bs4 import BeautifulSoup
# except ImportError:
# 	import pip
# 	pip.main(['install', 'BeautifulSoup4'])
# 	from bs4 import BeautifulSoup

# try:
# 	from selenium import webdriver
# 	#from webdriver_manager.chrome import ChromeDriverManager
# except ImportError:
# 	import pip
# 	#pip.main(['install', 'webdriver-manager'])
# 	pip.main(['install', 'selenium'])
# 	from selenium import webdriver

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

	postbody = "http://127.0.0.1:8080/SetOutput?symbol=" + symbol + "&feedtype=L1&output=" + str(port)+"&status=on"

	return postbody,"register "+symbol,"register failed "+symbol

def deregister_web(symbol,port):

	postbody = "http://127.0.0.1:8080/SetOutput?symbol=" + symbol + "&feedtype=L1&output=" + str(port)+"&status=off"

	return postbody,"register "+symbol,"register failed "+symbol
	
def register_to_ppro(symbol,status,port):

	#log_print("Registering",symbol,status)
	if status == True:
		postbody = "http://127.0.0.1:8080/SetOutput?symbol=" + symbol + "&feedtype=L1&output=" + str(port)+"&status=on"
	else:
		postbody = "http://127.0.0.1:8080/SetOutput?symbol=" + symbol + "&feedtype=L1&output=" + str(port)+"&status=off"

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

	r = 'http://127.0.0.1:8080/Flatten?symbol='+str(symbol)
	sucess='flatten '+symbol+' Success!'
	failure='flatten '+symbol+' Failure.'

	return r,sucess,failure
	#req = threading.Thread(target=ppro_request, args=(r,sucess,failure,),daemon=True)
	#req.start()

def breakup_order(symbol,share,break_price):


	limprice = round(break_price+0.05,2)
	break_price = round(break_price,2)
	r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice='+str(limprice)+'&ordername=EDGX Buy ROUC StopLimit DAY&shares='+str(share)+'&stopprice='+str(break_price)
	
	sucess='buy market order success on'+symbol
	failure="Error buy order on"+symbol

	return r,sucess,failure

def breakdown_order(symbol,share,break_price):

	limprice = round(break_price-0.05,2)
	break_price = round(break_price,2)
	r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice='+str(limprice)+'&ordername=EDGX Sell->Short ROUC StopLimit DAY&shares='+str(share)+'&stopprice='+str(break_price)
	
	sucess='buy market order success on'+symbol
	failure="Error buy order on"+symbol

	return r,sucess,failure

def buy_market_order(symbol,share):

	#r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=EDGX Buy ROUC Market DAY&shares='+str(share)
	r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=ARCA Buy ARCX Market DAY&shares='+str(share)
	sucess='buy market order success on'+symbol
	failure="Error buy order on"+symbol

	return r,sucess,failure
	#
	#req = threading.Thread(target=ppro_request, args=(r,sucess,failure,),daemon=True)
	#req.start()

def sell_market_order(symbol,share):



	r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=ARCA Sell->Short ARCX Market DAY&shares='+str(share)
	#r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=EDGX Sell->Short ROUC Market DAY&shares='+str(share)
	sucess='sell market order success on'+symbol
	failure="Error sell order on"+symbol

	return r,sucess,failure

def buy_limit_order(symbol, price,share,gateway=0):

	price = round(float(price),2)

	if gateway ==0:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=MEMX Buy MEMX Limit Visible DAY&shares='+str(share)
	elif gateway ==1:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=ARCA Buy ARCX Limit DAY&shares='+str(share)
	elif gateway ==2:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=BATS Buy Parallel-2D Limit DAY&shares='+str(share)
	elif gateway ==3:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=EDGA Buy EDGA Limit PostMarket DAY Regular'+str(share)
	else:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=MEMX Buy MEMX Limit Visible DAY&shares='+str(share)
	#r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=MEMX Buy MEMX Limit DAY BookOnly&shares='+str(share)
	sucess='buy limit order success on '+symbol
	failure="Error buy limit order on "+symbol

	return r,sucess,failure

def sell_limit_order(symbol, price,share,gateway=0):
	price = round(float(price),2)

	if gateway ==0:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=MEMX Sell->Short MEMX Limit Visible DAY&shares='+str(share)
	#r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=MEMX Sell->Short MEMX Limit DAY BookOnly&shares='+str(share)
	elif gateway ==1:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=ARCA Sell->Short ARCX Limit DAY&shares='+str(share)
	elif gateway ==2:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=BATS Sell->Short Parallel-2D Limit DAY'+str(share)
	elif gateway ==3:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=EDGA Sell->Short EDGA Limit PostMarket DAY Regular'+str(share)
	else:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=MEMX Sell->Short MEMX Limit Visible DAY&shares='+str(share)


	sucess='sell limit order success on '+symbol
	failure="Error sell limit order on "+symbol

	return r,sucess,failure


def passive_buy(symbol	,share,offset):

	

	# BATS Buy BATSPostOnly Limit DAY
	# MEMX Buy MEMX Limit Visible DAY PostOnly
	# 	r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=MEMX Buy MEMX Pegged Near DAY MidPoint&shares='+str(share)

	r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=MEMX Buy MEMX Limit Near Visible DAY PostOnly&shares='+str(share)
	sucess='passive buy limit order success on '+symbol
	failure="Error passive buy limit order on "+symbol

	return r,sucess,failure

def passive_sell(symbol	,share,offset):



	# MEMX Sell->Short MEMX Limit Visible DAY PostOnly
	# BATS Sell->Short BATSPostOnly Limit DAY
	#	r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=MEMX Sell->Short MEMX Pegged Near DAY MidPoint&shares='+str(share)

	r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=MEMX Sell->Short MEMX Limit Near Visible DAY PostOnly&shares='+str(share)

	sucess='passive sell limit order success on '+symbol
	failure="Error passive sell limit order on "+symbol

	return r,sucess,failure


# MEMX Buy MEMX Limit Near Visible DAY PostOnly #
#################################################
# def passive_buy(symbol	,share,price):


# 	price = round(float(price),2)

# 	# BATS Buy BATSPostOnly Limit DAY
# 	# MEMX Buy MEMX Limit Visible DAY PostOnly
# 	r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=MEMX Buy MEMX Limit Visible DAY PostOnly&shares='+str(share)
# 	sucess='passive buy limit order success on'+symbol
# 	failure="Error passive buy limit order on"+symbol

# 	return r,sucess,failure

# def passive_sell(symbol	,share,price):

# 	price = round(float(price),2)

# 	# MEMX Sell->Short MEMX Limit Visible DAY PostOnly
# 	# BATS Sell->Short BATSPostOnly Limit DAY
# 	r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=MEMX Sell->Short MEMX Limit Visible DAY PostOnly&shares='+str(share)

# 	sucess='passive sell limit order success on'+symbol
# 	failure="Error passive sell limit order on"+symbol

# 	return r,sucess,failure


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

	r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice='+str(ask)+'&ordername=ARCA Buy ARCX Limit IOC&shares='+str(share)
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

	r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice='+str(bid)+'&ordername=ARCA Sell->Short ARCX Limit IOC&shares='+str(share)
	sucess='Aggresive limit sell order success on'+symbol
	failure="Error buy order on"+symbol

	return r,sucess,failure

def stoporder_to_market_buy(symbol,price,share):

	price = round(float(price),2)
	r='http://127.0.0.1:8080/SendSwiftStop?symbol='+symbol+'&limitprice=0&ordername=ARCA%20Buy%20ARCX%20Market%20DAY&shares='+str(share)+'&referenceprice=ask&swiftstopprice='+str(price)
	sucess='stoporder buy market order success on '+symbol
	failure="Error stoporder buy market"+symbol
   
	return r,sucess,failure

def stoporder_to_market_sell(symbol,price,share):

	price = round(float(price),2)

	r= 'http://127.0.0.1:8080/SendSwiftStop?symbol='+symbol+'&ordername=ARCA%20Sell-%3EShort%20ARCX%20Market%20DAY&shares='+str(share)+'&referenceprice=bid&swiftstopprice='+str(price)
	sucess='stoporder sell market order success on '+symbol
	failure="Error sell order on"+symbol
   
	return r,sucess,failure

def cancel_all_oders(symbol):

	r = 'http://127.0.0.1:8080/CancelOrder?type=all&symbol='+str(symbol)+'&side=order'
	#r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=MEMX Sell->Short MEMX Limit DAY BookOnly&shares='+str(share)
	sucess='cancel success on '+symbol
	failure="cancel error on "+symbol

	return r,sucess,failure

def init_driver(pipe_status):

	while True:
		try:
			PATH = "../sys/chromedriver.exe"

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

	#driver = init_driver(pipe_status)

	log_print("Orders output moudule online.")

	request_str = ""
	sucess_str= ""
	failure_str = ""
	termination = False
	pipe_status.send(["ppro_out","Connected"])
	while True and not termination:
		try:
			request_str = ""
			sucess_str= ""
			failure_str = ""
			d = pipe.recv()
			type_ = d[0]

			log_print("PPRO ORDER:",d)

			if type_ == "shutdown":
				log_print("ppro out termination")
				pipe_status.send("terminated")
				log_print("ppro out shutdown successful")
				termination = True
				
			elif type_ == REGISTER:

				symbol = d[1]
				request_str,sucess_str,failure_str = register_web(symbol,port)

			elif type_ == BUY:

				symbol = d[1]
				share = d[2]
				rationale = d[3]

				request_str,sucess_str,failure_str=buy_market_order(symbol,share)

			elif type_ ==SELL:

				symbol = d[1]
				share = d[2]
				rationale = d[3]
				request_str,sucess_str,failure_str=sell_market_order(symbol,share)

			elif type_ == PASSIVEBUY:

				symbol = d[1]
				share = d[2]
				offset = d[3]

				request_str,sucess_str,failure_str=passive_buy(symbol,share,offset)

			elif type_ == PASSIVESELL:

				symbol = d[1]
				share = d[2]
				offset = d[3]

				request_str,sucess_str,failure_str=passive_sell(symbol,share,offset)

			elif type_ ==BREAKUPBUY:
				symbol = d[1]
				share = d[2]
				stop = d[3]

				request_str,sucess_str,failure_str=breakup_order(symbol,share,stop)

			elif type_ ==BREAKDOWNSELL:

				symbol = d[1]
				share = d[2]
				stop = d[3]

				request_str,sucess_str,failure_str=breakdown_order(symbol,share,stop)

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
				gateway = d[4]
				rationale = d[5]
				request_str,sucess_str,failure_str=buy_limit_order(symbol,price,share,gateway)

			elif type_ == LIMITSELL:

				symbol = d[1]
				price = round(d[2],2)
				share = d[3]
				gateway = d[4]
				rationale = d[5]

				request_str,sucess_str,failure_str=sell_limit_order(symbol,price,share,gateway)

			elif type_ == CANCEL:

				symbol = d[1]

				request_str,sucess_str,failure_str=cancel_all_oders(symbol)


			elif type_ == CANCELALL:


				request_str = "http://127.0.0.1:8080/CancelOrder?type=all&symbol=*.*&side=order"
				sucess_str = "Cancell all sucess"
				failure_str = "Cancell all failed"

			elif type_ == FLATTEN:

				symbol = d[1]
				request_str,sucess_str,failure_str=flatten_symbol(symbol)
			else:

				log_print("Unrecognized  command received.",type_)

			sucessful = False


			
			if request_str!="":
				while not sucessful:
					try:

						req = str(request_str)
						r = requests.get(req)
						sucessful = True
						#log_print("POSTING:",request_str)
					except Exception as e:
						log_print(e,failure_str," driver restart")
						time.sleep(0.05)

		except Exception as e:
			log_print(e)

	log_print("ppro out terminated")


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
		req = "http://127.0.0.1:8080/GetOrderNumber?requestid="+str(request_number)
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

	req = 'http://127.0.0.1:8080/GetScriptState?scriptid='+id_
	r = requests.post(req)

	return (find_between(r.text,"<Content>","</Content>"))

def cancel_stoporder(id_):

	r="http://127.0.0.1:8080/CancelScript?scriptid="+str(id_)
	sucess='cancellation successful'
	failure="cancellation failed"

	req = threading.Thread(target=ppro_request, args=(r,sucess,failure),daemon=True)
	req.start()	


# print("start")
# req = "http://127.0.0.1:8080/ExecuteOrder?symbol=SPY.AM&ordername=ARCA%20Buy%20ARCX%20Market%20DAY&shares=5"
# r = requests.get(req)
