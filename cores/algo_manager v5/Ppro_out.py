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


def buy_market_order(symbol,share):
#
	if ".TO" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=TSX Buy SweepSOR Market ANON DAY&shares='+str(share)

	elif ".PA" in symbol:																												
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=TRQS Buy TRQSPARIS Market DAY&shares='+str(share)
	elif ".AS" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=TRQS Buy TRQSAMSTERDAM Market DAY&shares='+str(share)
	elif ".BR" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=TRQS Buy TRQSBRUSSELS Market DAY&shares='+str(share)
	elif ".LS" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=TRQS Buy TRQSLISBON Market DAY&shares='+str(share)
	elif ".MI" in symbol:#
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=TRQS Buy TRQSMILAN Market DAY&shares='+str(share)
	elif ".DE" in symbol:#TRQS Buy TRQSXETRA Limit DAY
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=TRQS Buy TRQSXETRA Market DAY&shares='+str(share)
	elif ".CH" in symbol:#TRQS Buy TRQSCOPENHAGEN Limit DAY #TRQS Buy TRQXSWISS Limit DAY
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=TRQS Buy TRQXSWISS Market DAY&shares='+str(share)
	elif ".CO" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=TRQS Buy TRQSCOPENHAGEN Market DAY&shares='+str(share)
	else:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=EDGX Buy ROUC Market DAY&shares='+str(share)
		#r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=ARCA Buy ARCX Market DAY&shares='+str(share)

	sucess='buy market order success on'+symbol
	failure="Error buy order on"+symbol

	return r,sucess,failure
	#
	#req = threading.Thread(target=ppro_request, args=(r,sucess,failure,),daemon=True)
	#req.start()

def sell_market_order(symbol,share):

	if ".TO" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=TSX Sell->Short SweepSOR Market ANON DAY&shares='+str(share)
	elif ".PA" in symbol:																												
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=TRQS Sell TRQSPARIS Market DAY&shares='+str(share)
	elif ".AS" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=TRQS Sell TRQSAMSTERDAM Market DAY&shares='+str(share)
	elif ".BR" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=TRQS Sell TRQSBRUSSELS Market DAY&shares='+str(share)
	elif ".LS" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=TRQS Sell TRQSLISBON Market DAY&shares='+str(share)
	elif ".MI" in symbol:																												
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=TRQS Sell TRQSMILAN Market DAY&shares='+str(share)
	elif ".DE" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=TRQS Sell TRQSXETRA Market DAY&shares='+str(share)
	elif ".CH" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=TRQS Sell TRQXSWISS Market DAY&shares='+str(share)
	elif ".CO" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=TRQS Sell TRQSCOPENHAGEN Market DAY&shares='+str(share)
	else:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=EDGX Sell->Short ROUC Market DAY&shares='+str(share)
		#r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=ARCA Sell->Short ARCX Market DAY&shares='+str(share)
	#r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=NSDQ Sell->Short SCAN Market DAY&shares='+str(share)
	#r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=EDGX Sell->Short ROUC Market DAY&shares='+str(share)
	sucess='sell market order success on'+symbol
	failure="Error sell order on"+symbol

	return r,sucess,failure


#TRQS Buy TRQSBRUSSELS Limit DAY
def passive_buy(symbol,share,offset,gateway):

	if ".TO" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=TSX Buy SweepSOR Limit Near ANON DAY&shares='+str(share)
	elif ".PA" in symbol:																												
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=TRQS Buy TRQSPARIS Limit Near DAY&shares='+str(share)
	elif ".AS" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=TRQS Buy TRQSAMSTERDAM Limit Near DAY&shares='+str(share)
	elif ".BR" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=TRQS Buy TRQSBRUSSELS Limit Near DAY&shares='+str(share)
	elif ".LS" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=TRQS Buy TRQSLISBON Limit Near DAY&shares='+str(share)
	elif ".MI" in symbol:																												
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=TRQS Buy TRQSMILAN Limit Near DAY&shares='+str(share)
	elif ".DE" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=TRQS Buy TRQSXETRA Limit Near DAY&shares='+str(share)
	elif ".CH" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=TRQS Buy TRQXSWISS Limit Near DAY&shares='+str(share)
	elif ".CO" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=TRQS Buy TRQSCOPENHAGEN Limit Near DAY&shares='+str(share)
	else:
		if gateway ==0:
			r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=MEMX Buy MEMX Limit Near Visible DAY&shares='+str(share)
		#r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=MEMX Sell->Short MEMX Limit DAY BookOnly&shares='+str(share)
		elif gateway ==1:
			r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=ARCA Buy ARCX Limit Near DAY&shares='+str(share)
		elif gateway ==2:
			r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=BATS Buy Parallel-2D Limit Near DAY&shares='+str(share)
		elif gateway ==3:
			r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=EDGA Buy ROUC Limit Near DAY&shares='+str(share)
		else:
			r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=ARCA Buy ARCX Limit Near DAY&shares='+str(share)

	sucess='passive buy limit order success on '+symbol
	failure="Error passive buy limit order on "+symbol

	return r,sucess,failure


def passive_sell(symbol	,share,offset,gateway):

	# MEMX Sell->Short MEMX Limit Visible DAY PostOnly
	# BATS Sell->Short BATSPostOnly Limit DAY TRQS Sell TRQSLISBON Limit DAY
	#	r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=MEMX Sell->Short MEMX Pegged Near DAY MidPoint&shares='+str(share)
	if ".TO" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=TSX Sell->Short SweepSOR Limit Near ANON DAY&shares='+str(share)
	elif ".PA" in symbol:																												
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=TRQS Sell TRQSPARIS Limit Near DAY&shares='+str(share)
	elif ".AS" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=TRQS Sell TRQSAMSTERDAM Limit Near DAY&shares='+str(share)
	elif ".BR" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=TRQS Sell TRQSBRUSSELS Limit Near DAY&shares='+str(share)
	elif ".LS" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=TRQS Sell TRQSLISBON Limit Near DAY&shares='+str(share)
	elif ".MI" in symbol:																												
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=TRQS Sell TRQSMILAN Limit Near DAY&shares='+str(share)
	elif ".DE" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=TRQS Sell TRQSXETRA Limit Near DAY&shares='+str(share)
	elif ".CH" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=TRQS Sell TRQXSWISS Limit Near DAY&shares='+str(share)
	elif ".CO" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=TRQS Sell TRQSCOPENHAGEN Limit Near DAY&shares='+str(share)
	else:
		if gateway ==0:
			r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=MEMX Sell->Short MEMX Limit Near Visible DAY&shares='+str(share)
		#r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=MEMX Sell->Short MEMX Limit DAY BookOnly&shares='+str(share)
		elif gateway ==1:
			r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=ARCA Sell->Short ARCX Limit Near DAY&shares='+str(share)
		elif gateway ==2:
			r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=BATS Sell->Short Parallel-2D Limit Near DAY&shares='+str(share)
		elif gateway ==3:
			r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=EDGA Sell->Short ROUC Limit Near DAY&shares='+str(share)
		else:
			r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=MEMX Sell->Short MEMX Limit Near Visible DAY&shares='+str(share)

	sucess='passive sell limit order success on '+symbol
	failure="Error passive sell limit order on "+symbol

	return r,sucess,failure

# reque,s,f = passive_sell("AC.PA",10,0,0)
# requests.post(reque)

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
		#ARCA Buy ARCX Limit Near DAY Reserve

	#r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice='+str(ask)+'&ordername=ARCA Buy ARCX Limit IOC&shares='+str(share)

	if ".TO" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&priceadjust=0.05&ordername=AEQN Buy AequitasLIT Limit Near Broker DAY&shares='+str(share)
	else:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&priceadjust=0.05&ordername=ARCA Buy ARCX Limit Near IOC&shares='+str(share)
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

	#r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice='+str(bid)+'&ordername=ARCA Sell->Short ARCX Limit IOC&shares='+str(share)

	if ".TO" in symbol:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&priceadjust=-0.05&ordername=AEQN Sell->Short AequitasLIT Limit Near Broker DAY&shares='+str(share)
	else:
		r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&priceadjust=-0.05&ordername=ARCA Sell->Short ARCX Limit Near IOC&shares='+str(share)

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


def Ppro_out(pipe,port,pipe_status): #a sperate process. GLOBALLY. 

	#driver = init_driver(pipe_status)

	log_print("Orders output moudule online.")

	request_str = ""
	sucess_str= ""
	failure_str = ""
	termination = False

	# req = threading.Thread(target=ppro_api_check, args=(pipe_status,),daemon=True)
	# req.start()	
	
	while True and not termination:
		try:
			request_str = ""
			sucess_str= ""
			failure_str = ""
			symbol = ""
			
			is_order = False
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

			# elif type_ == BUY:

			# 	symbol = d[1]
			# 	share = d[2]
			# 	rationale = d[3]

			# 	request_str,sucess_str,failure_str=buy_market_order(symbol,share)
			# 	is_order = True
			# elif type_ ==SELL:

			# 	symbol = d[1]
			# 	share = d[2]
			# 	rationale = d[3]
			# 	request_str,sucess_str,failure_str=sell_market_order(symbol,share)
			# 	is_order = True
			elif type_ == PASSIVEBUY:

				symbol = d[1]
				share = d[2]
				offset = d[3]
				gateway = d[4]
				request_str,sucess_str,failure_str=passive_buy(symbol,share,offset,gateway)
				is_order = True
			elif type_ == PASSIVESELL:

				symbol = d[1]
				share = d[2]
				offset = d[3]
				gateway = d[4]
				request_str,sucess_str,failure_str=passive_sell(symbol,share,offset,gateway)
				is_order = True

			# elif type_ ==BREAKUPBUY:
			# 	symbol = d[1]
			# 	share = d[2]
			# 	stop = d[3]

			# 	request_str,sucess_str,failure_str=breakup_order(symbol,share,stop)
			# 	is_order = True
			# elif type_ ==BREAKDOWNSELL:

			# 	symbol = d[1]
			# 	share = d[2]
			# 	stop = d[3]

			# 	request_str,sucess_str,failure_str=breakdown_order(symbol,share,stop)
			# 	is_order = True

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
				is_order = True

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
				is_order = True

			# elif type_ == LIMITBUY:

			# 	symbol = d[1]
			# 	price = round(d[2],2)
			# 	share = d[3]
			# 	gateway = d[4]
			# 	rationale = d[5]
			# 	request_str,sucess_str,failure_str=buy_limit_order(symbol,price,share,gateway)
			# 	is_order = True
			# elif type_ == LIMITSELL:

			# 	symbol = d[1]
			# 	price = round(d[2],2)
			# 	share = d[3]
			# 	gateway = d[4]
			# 	rationale = d[5]

			# 	request_str,sucess_str,failure_str=sell_limit_order(symbol,price,share,gateway)
			# 	is_order = True

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

				req = threading.Thread(target=ppro_request, args=(request_str,sucess_str,failure_str,symbol,pipe_status,is_order),daemon=True)
				req.start()	

		except Exception as e:
			PrintException("PPro out:",e)

	log_print("ppro out terminated")


#### ORDER TRACING PROGAM ###



def ppro_request(request_str,sucess_str,failure_str,symbol,pipe,is_order):


	try:
		r = requests.post(request_str)

		if r.status_code ==200:
			if is_order==True:
				time.sleep(0.2)

				order_number=""
				order_id = find_between(r.text,"<Content>","</Content>")

				if len(order_id)>0:
					order_id = int(order_id)
					req = "http://127.0.0.1:8080/GetOrderNumber?requestid="+str(order_id)
					r = requests.get(req)
					order_number = find_between(r.text,"<Content>","</Content>")

				if len(order_number)>0:
					req = "http://127.0.0.1:8080/GetOrderState?ordernumber="+order_number
					r = requests.post(req)

					if "Rejected" in r.text:

						data = {}
						data["symbol"]= symbol
						data["side"]= ""
						data["info"]=r.text

						log_print("Rejected:",symbol)

						pipe.send(["order rejected",data])


					# elif "Pending" in r.text or "Filled" in r.text or "Accepted" in r.text:
					# 	log_print(sucess_str)

					# else:
					# 	log_print("PPRO OUT: WERID MESSAGE:",r.text)

		else:
			log_print(failure_str," ",r.text)
			if is_order==True and symbol!="" and  "Invalid" in r.text:

				data = {}
				data["symbol"]= symbol
				data["side"]= ""
				data["info"]=r.text

				log_print("Rejected:",symbol)

				pipe.send(["order rejected",data])


	except Exception as e:

		log_print("PPRO OUT ERROR:",e)



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



# symbol = "XIU.TO"
# offset=0.0
# share = 10 
# r = 'http://127.0.0.1:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(0.01) +'&priceadjust='+str(offset)+'&ordername=AEQN Buy AequitasLIT Limit Near Broker DAY&shares='+str(share)

# request_number = 32718
# req = "http://127.0.0.1:8080/GetOrderNumber?requestid="+str(request_number)
# r = requests.post(r)

# print(r.text)


# print("start")
# req = "http://127.0.0.1:8080/ExecuteOrder?symbol=USO.AM&ordername=ARCA%20Buy%20ARCX%20Market%20DAY&shares=1"
# r = requests.post(req)

# order_id = find_between(r.text,"<Content>","</Content>")

# state = ""

# time.sleep(0.2)
# order_number=""
# if len(order_id)>0:
# 	order_id = int(order_id)
# 	req = str("http://127.0.0.1:8080/GetOrderNumber?requestid="+str(order_id))
# 	req = "http://127.0.0.1:8080/GetOrderNumber?requestid="+str(order_id)
# 	r = requests.get(req)
# 	print(req,r.text)
# 	order_number = find_between(r.text,"<Content>","</Content>")
# print(order_number)

# if len(order_number)>0:
# 	req = "http://127.0.0.1:8080/GetOrderState?ordernumber="+order_number
# 	r = requests.post(req)


# print(r.text)

# symbol = "QQQ.NQ"
# share = 1
# offset = 0.5 
# if share<0:
# 	reque =  "http://127.0.0.1:8080/ExecuteOrder?symbol="+symbol+'&priceadjust='+str(offset)+'&ordername=ARCA%20Sell->Short%20ARCX%20LOO%20Far%20OnOpen&shares='+str(abs(share))

# else:
# 	reque =  "http://127.0.0.1:8080/ExecuteOrder?symbol="+symbol+'&priceadjust='+str(offset)+'&ordername=ARCA%20Buy%20ARCX%20LOO%20Far%20OnOpen&shares='+str(abs(share))
# r = requests.post(reque)
# print(r.text)