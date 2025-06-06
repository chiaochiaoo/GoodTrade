import time
import requests 
import socket
import threading
import os 
from constant import *
from Util_functions import *
import csv
from datetime import datetime
import re
import multiprocessing

from psutil import process_iter
import psutil

import json

import xml.etree.ElementTree as ET


global user 
user = ""

global file_location
file_location = ""

global summary_being_read
summary_being_read = False 


POSITION_UPDATE = "Position Update"
SYMBOL_UPDATE = "Symbol Update"
SUMMARY_UPDATE  = "Summary update"
ORDER_UPDATE = "Order Update"

def open_file():

	try:
		f = open("../../algo_logs/"+datetime.now().strftime("%m-%d")+"data.csv", "a")
		writer = csv.writer(f,lineterminator = '\n')
	except:
		f = open("../../algo_logs/"+datetime.now().strftime("%m-%d")+"data.csv", "w")
		writer = csv.writer(f,lineterminator = '\n')
		writer.writerow(['symbol', 'timestamp','bid','ask','EMA5H','EMA5L','EMA5C','EMA8H','EMA8L','EMA8C'])
	
	return f,writer 

def save_file(f):
	f.close()

def threading_request(request_str):
	req = threading.Thread(target=request,args=(request_str,), daemon=True)
	req.start()

def request(request_str):
	requests.get(request_str)

def Ppro_in(port,pipe):

	p1 = threading.Thread(target=periodical_check,args=(pipe,port), daemon=True)
	p1.start()

	p2 = threading.Thread(target=read_summary,args=(pipe,), daemon=True)
	p2.start()

	last_ts = 0

	UDP_IP = "localhost"
	UDP_PORT = port

	force_close_port(port)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))
	log_print("Ppro in moudule initializing")
	pipe.send(["msg","algo_ppro working"])
	#sock.settimeout()
	work = False
	while True:

		try:
			rec= False
			try:
				data, addr = sock.recvfrom(1024)
				#print(data)
				rec = True
			except Exception as e:
				log_print(e)
				# IF I don't hear things for 5 seconds. it would result in a timed out. ok. good.
				work = False
				#pipe.send(["ppro_in","DISCONNECTED"])

			if rec:
				stream_data = str(data)
				# if work==False:
				# 	pipe.send(["ppro_in","Connected"])

				work=True
				type_ = find_between(stream_data, "Message=", ",")

				if type_ == "OrderStatus":
					decode_order(stream_data,pipe)

				#### CAN USE THIS TO TAKE CURRENT SYMBOLS ####

				#now = datetime.now()

				# cur_ts = now.hour*60+now.minute 
				# if cur_ts - ts >= 30:
				# 	ts = cur_ts 
				# 	ppro_conn = threading.Thread(target=ppro_connection_service,args=(pipe,port), daemon=True)
				# 	ppro_conn.start()
				# if cur_ts !=last_ts:
				# 	log_print("PPRO message updating normal,",cur_ts)
				# 	last_ts = cur_ts

				# elif type_ =="L1":
				# 	decode_l1(stream_data,pipe,writer,l1data)
				# 	count+=1
				# 	if count %1000 ==0:
				# 		save_file(f)
				# 		f,writer = open_file()

		except Exception as e:
			PrintException(e,"PPRO IN error")
	#f.close()


	
def get_symbol_price(symbols,pipe,lock):

	with lock:

		if len(symbols)>0:
			s = ''
			for i in symbols:
				s+=i+','
			s=s[:-1]

			b = "https://financialmodelingprep.com/api/v3/quote-short/"+s+"?apikey=a901e6d3dd9c97c657d40a2701374d2a"

			res=requests.get(b)
			d= json.loads(res.text)

			x = {}
			for i in d:
				x[i['symbol']] = i['price']

			pipe.send([SYMBOL_UPDATE,x])
			print("price update complete.. symbols:",len(symbols))
	


def periodical_check(pipe,port):


	"""
	Two things in there.
	1. Periodically send out OSSTAT and request for get ENV.
	2. Perioddically send out read orders 


	### UPDATE . 1. Summary PNL  2. Total Positions/Symbols 
	"""
	global user 
	global file_location
	global summary_being_read

	#lock = threading.Lock()

	c = 0

	open_order_count = 0
	status = False 
	while True:
		
		try:

			#### API CHECK BEFORE ALL ELSE. ####

			if c%10==0 or status==False:

				req = "http://127.0.0.1:8080/Register?symbol=QQQ.NQ&feedtype=L1"

				try:
					r = requests.post(req)

					if r.status_code ==200:
						pipe.send(["ppro_api","Connected"])
						status= True 
					else:
						pipe.send(["ppro_api","DISCONNECTED"])
						status = False 
				except:
					pipe.send(["ppro_api","DISCONNECTED"])
					status = False 

			### first step, get user and file location
			if status:
				if summary_being_read==False:
					threading_request("http://127.0.0.1:8080/Get?type=tool&tool=Summary_1&key=NCSA%20Equity")
					user,file_location = get_env()
				else:
					if c%50==0:
						#log_print("PPro in : periodcal new loop",cur_ts)
						threading_request("http://127.0.0.1:8080/SetOutput?region=1&feedtype=OSTAT&output="+ str(port)+"&status=on") ## ORDER STATS.
						threading_request("http://127.0.0.1:8080/SetOutput?region=2&feedtype=OSTAT&output="+ str(port)+"&status=on") ## ORDER STATS.
					# ### 1. register OSTAT  
					# if c%5==0:
					# 	register_order_listener(port)

					### 2. Get open position 
					positions = get_current_positions()

					### 3. send request for summary PNL

					if c%5==0:
						accepted_orders = get_current_orders()
						log_print(accepted_orders)

						if 'Accepted' in accepted_orders:
							open_order_count = accepted_orders['Accepted']

					threading_request("http://127.0.0.1:8080/Get?type=tool&tool=Summary_1&key=NCSA%20Equity")

					c+=1
					pipe.send([POSITION_UPDATE,positions,user,open_order_count])

		except Exception as e:
			PrintException(e,"periodical_check error ")
		time.sleep(1)

def get_env():

	try:
		p="http://localhost:8080/GetEnvironment?"
		r= requests.get(p)

		if r.status_code==200:
			user = find_between(r.text, "User=", " ")[1:-1]
			directory = find_between(r.text, "DataDir=", "/")[1:]

			# print("user",user)
			# print("directory",directory)

			file_location = directory+"\\"+user+'_Summary_1.log'
			log_print("Get ENV complete,",user,file_location)
			return (user,file_location)
		else:
			return ('','')
	except Exception as e:
		PrintException(e,"Get ENV failed ")
		return ('','')



def read_summary(pipe):

	global file_location
	global summary_being_read

	file_found = False 
	while True:

		if os.path.exists(file_location):
			log_print("summary file located.")
			if file_found==False:
				try:
					with open(file_location, 'r') as file:
						content = file.readlines()

					# Calculate the index to delete up to

					if len(content)>100:

						half_index = len(content) // 10
						log_print("summary file length:",len(content))
						# Delete the first half of the content
						del content[:-half_index]
						log_print("new summary file length:",len(content))
						# Open the file for writing
						with open(file_location, 'w') as file:
							file.writelines(content)
					
					#os.remove(file_location)
					# with open(file_location, 'w') as creating_new_csv_file: 
					# 	pass 
				except Exception as e:
					print("Shorting file error:,",e)
				file_found = True 
			else:

				log_print("reading summary functional, removing old file")
				summary_being_read = True

				try:
					with open(file_location, 'r') as f:
						#print(f.readline())
						f.readlines()
						while True:
							i=f.readline()

							if len(i)>0:
								l = i.split(" ")

								if len(l)>1:
									if l[1]=="RegionAssetLayerDisplayData:":
										#print(l)

										ms,ts,mili_ts = timestamp_mili_seconds(l[0])
										net = float(find_between(i, "net=", ","))
										fees = float(find_between(i, "totalFees=", ","))
										trades = int(find_between(i, "totalTrades=", ","))
										sizeTraded = int(find_between(i, "sizeTraded=", ","))
										unrealizedPlusNet = float(find_between(i, "unrealizedPlusNet=", ","))
										unrealized = unrealizedPlusNet	-net 

										cur_exp  = round(float(find_between(i, "currentExposure=", ",")))
										max_exp = round(float(find_between(i, "maxExposure=", ",")))
										#print(time_,net,fees,trades,sizeTraded,unrealizedPlusNet)
										# SymbolLayerDisplayData: 
										d= {}

										d['unrealizedPlusNet'] = unrealizedPlusNet
										d['timestamp'] = ts
										d['unrealized'] = round(unrealized,2)
										d['net'] = round(net,2)
										d['fees'] = round(fees,2)
										d['trades'] = int(trades)
										d['sizeTraded'] = int(sizeTraded)
										
										
										if cur_exp<1000000:
											d["cur_exp"] = str(cur_exp//1000)+"k"
										else:
											d["cur_exp"] = str(cur_exp//1000000)+"m"

										if max_exp<1000000:
											d["max_exp"] = str(max_exp//1000)+"k"
										else:
											d["max_exp"] = str(max_exp//1000000)+"m"										

										
										pipe.send([SUMMARY_UPDATE,d])

									# elif l[1]=="SymbolLayerDisplayData:":


									# 	ms,ts,mili_ts = timestamp_mili_seconds(l[0])
									# 	symbol = find_between(i, "symbol=", ",")
									# 	lastPrice = float(find_between(i, "lastPrice=", ","))
									# 	l1AskPrice = float(find_between(i, "l1AskPrice=", ","))
									# 	l1BidPrice = float(find_between(i, "l1BidPrice=", ","))
										
									# 	#log_print("Symbol received:",symbol,l1AskPrice)

									# 	d= {}
									# 	d['time'] = ts
									# 	d['symbol'] = symbol
									# 	d['lastPrice'] = lastPrice
									# 	d['l1AskPrice'] = l1AskPrice
									# 	d['l1BidPrice'] = l1BidPrice
									# 	d['timestamp'] = ts
									# 	pipe.send([SYMBOL_UPDATE,d])
									# 4 net 
									# 5 fees
									# 6 trades
									# 8 max profit 
									# 10 sizeTraded
									# 22 unrealizedPlusNet


				except Exception as e:  ## ANYTHING HAPPENED, EJECT. 
					PrintException("reading summary error",e)
					summary_being_read = False

		else:
			log_print("Ppro_in:, file_location_not detected:",file_location)
			summary_being_read = False

			pipe.send([SUMMARY_UPDATE,{}])
			#### ALERT. ? #### 
			time.sleep(2)


def get_current_orders():

	global user
	#user = "QIAOSUN"
	try:
		d = {}
		p="http://127.0.0.1:8080/GetOpenOrders?user="+user
		r= requests.get(p)

		description_pattern = re.compile(r'description="([^"]+)"')
		matches = description_pattern.findall(r.text)


		#log_print("Ppro_in:, get positions:",d)
		for i in matches:
			if i not in d:
				d[i] = 1
			else:
				d[i] +=1
		return d
	except Exception as e:
		PrintException(e)
		return {}



# print(get_current_orders())

def get_current_positions():

	global user
	try:
		d = {}
		p="http://127.0.0.1:8080/GetOpenPositions?user="+user
		r= requests.get(p)
		symbol=""
		share=""
		for i in r.text.splitlines():
			if "Position Symbol" in i:

				symbol = find_between(i, "Symbol=", " ")[1:-1]

				price =  float(find_between(i, "AveragePrice=", " ")[1:-1])
				share = int(find_between(i, "Volume=", " ")[1:-1])

				
				d[symbol] = (price,share) 
		#log_print("Ppro_in:, get positions:",d)
		return d
	except Exception as e:
		PrintException(e)
		return {}

def test_register():
	try:
		p="http://localhost:8080/Register?symbol=QQQ.NQ&feedtype=L1"
		r= requests.get(p)
		#log_print(r.status_code)
		#log_print(r)
		if r.status_code==200:
			return True
		else:
			return False

	except Exception as e:
		return False

	except:
		log_print("register failed")
		return False

def timestamp_seconds(s):

	p = s.split(":")
	try:
		x = int(p[0])*3600+int(p[1])*60+int(p[2])
		return x
	except Exception as e:
		log_print("Timestamp conversion error:",e,s)
		return 0

def timestamp_mili_seconds(s):

	#s="15:41:56.526"

	p = s[:-4].split(":")
	mili = int(s[-3:])
	try:
		x1 = int(p[0])*60+int(p[1])
		x = int(p[0])*3600+int(p[1])*60+int(p[2])
		x2 = x*1000 + mili
		return x1,x,x2
	except Exception as e:
		log_print("Timestamp conversion error:",e,s)
		print("")

def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data

def register_order_listener(port):

	postbody = "http://localhost:8080/SetOutput?region=1&feedtype=OSTAT&output="+ str(port)+"&status=on"

	try:
		r= requests.get(postbody)
		if r.status_code==200:
			return True
		else:
			return False
	except:
		log_print("register failed")
		return False

def decode_order(stream_data,pipe):
	if "OrderState" in stream_data:
		#log_print(stream_data)
		state = find_between(stream_data, "OrderState=", ",")
		if state =="Filled" or state =="Partially Filled":
			symbol = find_between(stream_data, "Symbol=", ",")
			side = find_between(stream_data, "Side=", ",")
			price = find_between(stream_data, "Price=", ",")
			share = find_between(stream_data, "Shares=", ",")
			ts=find_between(stream_data, "MarketDateTime=", ",")[9:-4]
			#add time
			if side =="T" or side =="S": side ="Short"
			if side =="B": side = "Long"

			data ={}
			data["symbol"]= symbol
			data["side"]= side
			data["price"]= float(price)
			data["shares"]= int(share)
			data["timestamp"]= timestamp_seconds(ts)
			pipe.send(["order confirm",data])

		if state =="Rejected":
			symbol = find_between(stream_data, "Symbol=", ",")
			side = find_between(stream_data, "Side=", ",")
			info = find_between(stream_data, "InfoText=", ",")
			data ={}
			if side =="T" or side =="S": side ="Short"
			if side =="B": side = "Long"

			data["symbol"]= symbol
			data["side"]= side
			data["info"]=info
			try:
				log_print(symbol,side,info)
			except:
				pass
			pipe.send(["order rejected",data])


#'LocalTime=14:24:34.886,Message=L1,MarketTime=14:24:38.206,Symbol=SNDL.NQ,BidPrice=0.828300,BidSize=13899,AskPrice=0.828400,AskSize=2364,Tick=?\n'
def decode_l1(stream_data,pipe,writer,l1data):
	symbol = find_between(stream_data, "Symbol=", ",")
	bid=float(find_between(stream_data, "BidPrice=", ","))
	ask=float(find_between(stream_data, "AskPrice=", ","))
	#ts= timestamp_seconds(find_between(stream_data, "MarketTime=", ",")[:-4])

	ms,ts,mili_ts = timestamp_mili_seconds(find_between(stream_data, "MarketTime=", ","))

	send = False

	if symbol in l1data:
		#if either level has changed. register. 
		if l1data[symbol]["bid"]!=bid or l1data[symbol]["ask"]!=ask:
			send = True
		elif ts-l1data[symbol]["timestamp"] >1:
			send = True

		#if has been more then 2 leconds. registered.

	else:
		l1data[symbol] = {}

		l1data[symbol]["symbol"] = symbol
		l1data[symbol]["bid"] = bid
		l1data[symbol]["ask"] = ask
		l1data[symbol]["timestamp"] = ts

		l1data[symbol]["internal"] = {}
		l1data[symbol]["internal"]["timestamp"] = ms
		l1data[symbol]["internal"]["current_minute_bins"] = [bid,ask]
		l1data[symbol]["internal"]["EMA_count"] = 0

		#Realizing - I won't need to track these values no more.
		l1data[symbol]["internal"]["high"] = ask
		l1data[symbol]["internal"]["low"] = bid
		l1data[symbol]["internal"]["open"] = ask
		l1data[symbol]["internal"]["close"] = bid

		l1data[symbol]["internal"]["EMA_count"] = 0

		l1data[symbol]["internal"]["EMA5H"] = 0
		l1data[symbol]["internal"]["EMA5L"] = 0
		l1data[symbol]["internal"]["EMA5C"] = 0

		l1data[symbol]["internal"]["EMA8H"] = 0
		l1data[symbol]["internal"]["EMA8L"] = 0
		l1data[symbol]["internal"]["EMA8C"] = 0

		l1data[symbol]["internal"]["EMA21H"] = 0
		l1data[symbol]["internal"]["EMA21L"] = 0
		l1data[symbol]["internal"]["EMA21C"] = 0
		send = True

	#process the informations. process internal only. 

	#two kinds of update. normal second; and new second. 
	if send:

		update = process_l1(l1data[symbol]["internal"],bid,ask,ms)

		"""two cases. small, and big."""

		l1data[symbol]["symbol"] = symbol
		l1data[symbol]["bid"] = bid
		l1data[symbol]["ask"] = ask
		l1data[symbol]["timestamp"] = ts

		if update:

			update_ = {}
			update_["EMA5H"]=l1data[symbol]["internal"]["EMA5H"]
			update_["EMA5L"]=l1data[symbol]["internal"]["EMA5L"]
			update_["EMA5C"]=l1data[symbol]["internal"]["EMA5C"]

			update_["EMA8H"]=l1data[symbol]["internal"]["EMA8H"]
			update_["EMA8L"]=l1data[symbol]["internal"]["EMA8L"]
			update_["EMA8C"]=l1data[symbol]["internal"]["EMA8C"]

			update_["EMA21H"]=l1data[symbol]["internal"]["EMA21H"]
			update_["EMA21L"]=l1data[symbol]["internal"]["EMA21L"]
			update_["EMA21C"]=l1data[symbol]["internal"]["EMA21C"]


			update_["close"] = l1data[symbol]["internal"]["close"]
			
			update_["EMAcount"]=l1data[symbol]["internal"]["EMA_count"]

			pipe.send(["order update_m",l1data[symbol],update_])
			writer.writerow([symbol,mili_ts,bid,ask,\
				l1data[symbol]["internal"]["EMA8H"],\
				l1data[symbol]["internal"]["EMA8L"],\
				l1data[symbol]["internal"]["EMA8C"],\
				l1data[symbol]["internal"]["EMA21H"],\
				l1data[symbol]["internal"]["EMA21L"],\
				l1data[symbol]["internal"]["EMA21C"]])
			#print(symbol,l1data[symbol],update_)
		else:

			#print(l1data[symbol])
			#add time
			pipe.send(["order update",l1data[symbol]])
			writer.writerow([symbol,mili_ts,bid,ask])


def process_l1(dic,bid,ask,ms):

	"""two senarios. within current timestamp, and out. """

	if dic["timestamp"]  != ms: #a new minute. 

		dic["timestamp"] = ms
		if len(dic["current_minute_bins"])>1:
			dic["high"]=max(dic["current_minute_bins"])
			dic["low"]=min(dic["current_minute_bins"])
			dic["open"]=dic["current_minute_bins"][0]
			dic["close"]=dic["current_minute_bins"][-1]

			dic["current_minute_bins"] = []

			if dic["EMA_count"]==0: #first time setting up.
				### HERE. What i need to do is have the GT&server also track the EMA values of these. 
				dic["EMA5H"] = dic["high"]
				dic["EMA5L"] = dic["low"]
				dic["EMA5C"] = dic["close"]

				dic["EMA8H"] = dic["high"]
				dic["EMA8L"] = dic["low"]
				dic["EMA8C"] = dic["close"]

				dic["EMA21H"] = dic["high"]
				dic["EMA21L"] = dic["low"]
				dic["EMA21C"] = dic["close"]

			else: #induction! 
				dic["EMA5H"] = new_ema(dic["high"],dic["EMA5H"],5)
				dic["EMA5L"] = new_ema(dic["low"],dic["EMA5L"],5)
				dic["EMA5C"] = new_ema(dic["close"],dic["EMA5C"],5)

				dic["EMA8H"] = new_ema(dic["high"],dic["EMA8H"],8)
				dic["EMA8L"] = new_ema(dic["low"],dic["EMA8L"],8)
				dic["EMA8C"] = new_ema(dic["close"],dic["EMA8C"],8)

				dic["EMA21H"] = new_ema(dic["high"],dic["EMA21H"],21)
				dic["EMA21L"] = new_ema(dic["low"],dic["EMA21L"],21)
				dic["EMA21C"] = new_ema(dic["close"],dic["EMA21C"],21)

			dic["EMA_count"]+=1
			return True
		else:
			return False
	else: #same minute 
		dic["current_minute_bins"].append(bid)
		dic["current_minute_bins"].append(ask)
		return False

def new_ema(current,last_EMA,n):
	
	return round((current - last_EMA)*(2/(n+1)) + last_EMA,2)



def decode_l1_(stream_data,pipe,writer,l1data):
	symbol = find_between(stream_data, "Symbol=", ",")
	bid=float(find_between(stream_data, "BidPrice=", ","))
	ask=float(find_between(stream_data, "AskPrice=", ","))
	#ts= timestamp_seconds(find_between(stream_data, "MarketTime=", ",")[:-4])

	ts,mili_ts = timestamp_mili_seconds(find_between(stream_data, "MarketTime=", ","))

	send = False

	if symbol in l1data:
		#if either level has changed. register. 
		if l1data[symbol]["bid"]!=bid or l1data[symbol]["ask"]!=ask:
			send = True
		elif ts-l1data[symbol]["timestamp"] >1:
			send = True

		#if has been more then 2 leconds. registered.

	else:
		l1data[symbol] = {}
		l1data[symbol]["symbol"] = symbol
		l1data[symbol]["bid"] = bid
		l1data[symbol]["ask"] = ask
		l1data[symbol]["timestamp"] = ts
		send = True

	if send:
		l1data[symbol]["symbol"] = symbol
		l1data[symbol]["bid"] = bid
		l1data[symbol]["ask"] = ask
		l1data[symbol]["timestamp"] = ts
		#print(l1data[symbol])
		#add time
		pipe.send(["order update",l1data[symbol]])
		writer.writerow([symbol,mili_ts,bid,ask])

def force_close_port(port, process_name=None):
	"""Terminate a process that is bound to a port.
	
	The process name can be set (eg. python), which will
	ignore any other process that doesn't start with it.
	"""
	for proc in psutil.process_iter():
		for conn in proc.connections():
			if conn.laddr[1] == port:
				#Don't close if it belongs to SYSTEM
				#On windows using .username() results in AccessDenied
				#TODO: Needs testing on other operating systems
				try:
					proc.username()
				except psutil.AccessDenied:
					pass
				else:
					if process_name is None or proc.name().startswith(process_name):
						try:
							proc.kill()
						except (psutil.NoSuchProcess, psutil.AccessDenied):
							pass 


############################ PART 1 #######################################
# GET_POSITION_URL =  "http://127.0.0.1:8080/GetOpenPositions?user=BENCART"

previous_positions = {}
temp_positions = {}
symbol_buffers = {}  # symbol: { 'active': bool, 'expiry': int ms }
latest_fills={}
lock = threading.Lock()
BUFFER_TIME_MS = 100

def fetch_positions(p):

	try:
		response = requests.get(p, timeout=1)
		response.raise_for_status()
		root = ET.fromstring(response.text)

		positions = {}
		for region in root.findall('.//Region'):
			for position in region.findall('Position'):
				symbol = position.attrib.get('Symbol')
				volume = int(position.attrib.get('Volume'))
				side = position.attrib.get('Side')
				avg_price = float(position.attrib.get('AveragePrice'))

				positions[symbol] = {
					'symbol': symbol,
					'volume': volume,
					'side':side,
					'average_price': avg_price
				}
		#print(positions)
		return positions
	except Exception as e:
		print(f"[ERROR in fetch_positions] {e}")
		return {}

		
def update_symbol_buffers(current_positions, now_ms):
	changed_symbols = set()
	all_symbols = set(temp_positions.keys()).union(current_positions.keys())

	for symbol in all_symbols:
		old_data = temp_positions.get(symbol, {'volume': 0, 'average_price': 0})
		new_data = current_positions.get(symbol, {'volume': 0, 'average_price': 0})

		if old_data != new_data:
			changed_symbols.add(symbol)
			temp_positions[symbol] = new_data.copy()
			symbol_buffers[symbol] = {
				'active': True,
				'expiry': now_ms + BUFFER_TIME_MS
			}

	return changed_symbols

def flush_expired_buffers(now_ms,pipe):
	for symbol in list(symbol_buffers.keys()):
		buffer = symbol_buffers[symbol]
		if buffer['active'] and now_ms >= buffer['expiry']:
			old = previous_positions.get(symbol, {'volume': 0, 'average_price': 0})
			new = temp_positions.get(symbol, {'volume': 0, 'average_price': 0})
			vol_diff = new['volume'] - old['volume']

			if vol_diff != 0:
				old_value = old['volume'] * old['average_price']
				new_value = new['volume'] * new['average_price']
				try:
					approx_fill_price = (new_value - old_value) / vol_diff
				except ZeroDivisionError:
					approx_fill_price = 0

				#print(f"[{symbol}] Volume Change: {vol_diff}, Approx Fill Price: {round(approx_fill_price, 4)}")
				#with lock:
				ostat_price = None
				fill_info = latest_fills.get(symbol)#latest_fills.get(symbol)
				if fill_info:
					ostat_fill_time_ms = fill_info["timestamp"]
					if abs(now_ms - ostat_fill_time_ms) <= 500:
						ostat_price = fill_info["price"]
					print(latest_fills,fill_info,now_ms-ostat_fill_time_ms)

				final_price = ostat_price if ostat_price is not None else approx_fill_price
				data ={}
				data["symbol"]= symbol

				data["price"]= float(final_price)
				data["shares"]= int(vol_diff)
				data["timestamp"]= now_ms
				data['total'] = new['volume']
				pipe.send(["order confirm",data])
				
				print(f"[{symbol}] Volume Change: {vol_diff}, Fill Price: {round(final_price, 4)},{ostat_price},{approx_fill_price}")
			else:
				print(f"[{symbol}] No net volume change")

			previous_positions[symbol] = new.copy()
			buffer['active'] = False

			# Optional cleanup if position closed
			if new['volume'] == 0:
				temp_positions.pop(symbol, None)
				symbol_buffers.pop(symbol, None)

	#pipe.send(["order confirm",current_positions])
def track_position_changes(pipe):

	global user 
	global file_location
	user,file_location = get_env()
	p="http://127.0.0.1:8080/GetOpenPositions?user="+user


	while True:
		current_positions = fetch_positions(p)
		now = int(time.time() * 1000)

		with lock:
			changed = update_symbol_buffers(current_positions, now)
			# if changed:
			# 	print(f"[CHANGE DETECTED] {changed}")
			flush_expired_buffers(now,pipe)

		time.sleep(0.03)



############################### PART 2 ################################################

def decode_ostat(stream_data,pipe):
    if "OrderState" not in stream_data:
        return

    state = find_between(stream_data, "OrderState=", ",")

    if state in ("Filled", "Partially Filled"):
        symbol = find_between(stream_data, "Symbol=", ",")
        price = float(find_between(stream_data, "Price=", ","))
        ts_str = find_between(stream_data, "MarketDateTime=", ",")[9:-4]  # HH:MM:SS

        # Use current wall-clock time in ms
        fill_time = int(time.time() * 1000)

        with lock:
            latest_fills[symbol] = {
                'price': price,
                'timestamp': fill_time
            }

    elif state == "Rejected":
        symbol = find_between(stream_data, "Symbol=", ",")
        side = find_between(stream_data, "Side=", ",")
        info = find_between(stream_data, "InfoText=", ",")

        # Normalize side label
        side = "Short" if side in ("T", "S") else "Long" if side == "B" else "Unknown"

        data = {
            "symbol": symbol,
            "side": side,
            "info": info
        }

        try:
            log_print(symbol, side, info)
        except Exception:
            pass

        pipe.send(["order rejected", data])


def register_ostat_output(port=9999):
	url = f"http://localhost:8080/SetOutput?region=1&feedtype=OSTAT&output={port}&status=on"
	try:
		requests.post(url)
		#print(f"[OSTAT] Feed registered on port {port}")
	except Exception as e:
		print(f"[OSTAT ERROR] {e}")


def api_checker(pipe,port):


	"""
	Two things in there.
	1. Periodically send out OSSTAT and request for get ENV.
	2. Perioddically send out read orders 

	### UPDATE . 1. Summary PNL  2. Total Positions/Symbols 
	"""
	global user 
	global file_location
	global summary_being_read

	#lock = threading.Lock()

	c = 0

	open_order_count = 0
	status = False 
	while True:
		
		try:

			#### API CHECK BEFORE ALL ELSE. ####

			if c%10==0 or status==False:

				req = "http://127.0.0.1:8080/Register?symbol=QQQ.NQ&feedtype=L1"

				try:
					r = requests.post(req)

					if r.status_code ==200:
						pipe.send(["ppro_api","Connected"])
						status= True 
					else:
						pipe.send(["ppro_api","DISCONNECTED"])
						status = False 
				except:
					pipe.send(["ppro_api","DISCONNECTED"])
					status = False 

			### first step, get user and file location
			if status:
				if summary_being_read==False:
					threading_request("http://127.0.0.1:8080/Get?type=tool&tool=Summary_1&key=NCSA%20Equity")
					user,file_location = get_env()
				else:
					if c%50==0:
						#log_print("PPro in : periodcal new loop",cur_ts)
						threading_request("http://127.0.0.1:8080/SetOutput?region=1&feedtype=OSTAT&output="+ str(port)+"&status=on") ## ORDER STATS.
						threading_request("http://127.0.0.1:8080/SetOutput?region=2&feedtype=OSTAT&output="+ str(port)+"&status=on") ## ORDER STATS.

					#positions = get_current_positions()
					positions = {}
					### 3. send request for summary PNL

					if c%5==0:
						accepted_orders = get_current_orders()
						log_print(accepted_orders)

						if 'Accepted' in accepted_orders:
							open_order_count = accepted_orders['Accepted']

					threading_request("http://127.0.0.1:8080/Get?type=tool&tool=Summary_1&key=NCSA%20Equity")

					c+=1
					pipe.send([POSITION_UPDATE,positions,user,open_order_count])

		except Exception as e:
			PrintException(e,"periodical_check error ")
		time.sleep(1)


def Ppro_in_v6(port,pipe):

	p1 = threading.Thread(target=api_checker,args=(pipe,port), daemon=True)
	p1.start()

	p2 = threading.Thread(target=read_summary,args=(pipe,), daemon=True)
	p2.start()

	p3 = threading.Thread(target=track_position_changes,args=(pipe,),daemon=True)
	p3.start()

	last_ts = 0

	UDP_IP = "localhost"
	UDP_PORT = port

	force_close_port(port)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))
	log_print("Ppro in moudule initializing")
	pipe.send(["msg","algo_ppro working"])
	#sock.settimeout()
	work = False
	while True:

		try:
			rec= False
			try:
				data, addr = sock.recvfrom(4096)
				#print(data)
				rec = True
			except Exception as e:
				log_print(e)
				# IF I don't hear things for 5 seconds. it would result in a timed out. ok. good.
				work = False
				#pipe.send(["ppro_in","DISCONNECTED"])

			if rec:
				stream_data = str(data)

				work=True
				type_ = find_between(stream_data, "Message=", ",")

				if type_ == "OrderStatus":
					decode_ostat(stream_data,pipe)

		except Exception as e:
			PrintException(e,"PPRO IN error")



# if __name__ == "__main__":
	
# 	multiprocessing.freeze_support()

# 	port =4609

# 	ppro_in, ppro_pipe_end = multiprocessing.Pipe()

# 	ppro_in_manager = multiprocessing.Process(name="ppro in",target=Ppro_in_v6, args=(port,ppro_pipe_end),daemon=True)
# 	ppro_in_manager.daemon=True
# 	ppro_in_manager.start()
# 	while True:
# 		d = ppro_in.recv()
# 		print(d)