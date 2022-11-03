import time
import requests 
import socket
import threading
import os 
from constant import *
from Util_functions import *
import csv
from datetime import datetime

import multiprocessing

from psutil import process_iter
import psutil

global user 
user = ""

global file_location
file_location = ""

global summary_being_read
summary_being_read = False 


POSITION_UPDATE = "Position Update"
SYMBOL_UPDATE = "Symbol Update"
SUMMARY_UPDATE  = "Summary update"

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
				pipe.send(["ppro_in","Disconnected"])

			if rec:
				stream_data = str(data)
				if work==False:
					pipe.send(["ppro_in","Connected"])

				work=True
				type_ = find_between(stream_data, "Message=", ",")

				if type_ == "OrderStatus":
					decode_order(stream_data,pipe)

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
	f.close()

def Ppro_in_old(port,pipe):

	now = datetime.now()
	ts = now.hour*60+now.minute 
	last_ts = 0
	l1data = {}

	UDP_IP = "localhost"
	UDP_PORT = port

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))

	ppro_conn = threading.Thread(target=ppro_connection_service,args=(pipe,port), daemon=True)
	ppro_conn.start()

	log_print("Socket Created:",sock)
	
	work=False

	count = 0

	f,writer = open_file()

	pipe.send(["msg","algo_ppro working"])
	write_count = 0
	#sock.settimeout(5)

	while True:

		try:
			rec= False
			#print("restart")

			log_print("waiting for input")
			try:
				data, addr = sock.recvfrom(1024)
				#print(data)
				rec = True
			except Exception as e:
				log_print(e)
				# IF I don't hear things for 5 seconds. it would result in a timed out. ok. good.
				work = False
				pipe.send(["ppro_in","Disconnected"])

			if rec:
				stream_data = str(data)
				if work==False:
					pipe.send(["ppro_in","Connected"])
				work=True
				type_ = find_between(stream_data, "Message=", ",")

				now = datetime.now()
				cur_ts = now.hour*60+now.minute 
				if cur_ts - ts >= 30:
					ts = cur_ts 
					ppro_conn = threading.Thread(target=ppro_connection_service,args=(pipe,port), daemon=True)
					ppro_conn.start()
				if cur_ts !=last_ts:
					log_print("PPRO message updating normal,",cur_ts)
					last_ts = cur_ts
				if type_ == "OrderStatus":
					decode_order(stream_data,pipe)
				elif type_ =="L1":
					decode_l1(stream_data,pipe,writer,l1data)
					count+=1
					if count %1000 ==0:
						save_file(f)
						f,writer = open_file()
		except Exception as e:
			PrintException(e,"PPRO IN error")
	f.close()
	

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


	c = 0

	while True:
		
		try:

			### first step, get user and file location
			if summary_being_read==False:
				threading_request("http://localhost:8080/Get?type=tool&tool=Summary_1&key=NCSA%20Equity")
				user,file_location = get_env()
			else:
				if c%50==0:

					now = datetime.now()

					cur_ts = now.hour*60+now.minute 
					log_print("PPro in : periodcal new loop",cur_ts)
					threading_request("http://localhost:8080/SetOutput?region=1&feedtype=OSTAT&output="+ str(port)+"&status=on") ## ORDER STATS.



				# ### 1. register OSTAT  
				# if c%5==0:
				# 	register_order_listener(port)

				### 2. Get open position 
				positions = get_current_positions()

				### 3. send request for summary PNL
				threading_request("http://localhost:8080/Get?type=tool&tool=Summary_1&key=NCSA%20Equity")

				c+=1
				### 4. send request for each individual symbol PNL

				if c%7==0:
					for symbol in positions.keys():
						threading_request("http://localhost:8080/Get?type=tool&tool=Summary_1&key=NCSA%20Equity"+"^"+user+"^"+symbol)

				if c%8==0:
					for symbol in positions.keys():
						threading_request("http://localhost:8080/Get?type=tool&tool=Summary_1&key=NCSA%20Equity"+"^"+symbol)


				### RETURN BUS. 
				pipe.send([POSITION_UPDATE,positions,user])

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
					os.remove(file_location)
				except:
					pass
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

										cur_exp  = float(find_between(i, "currentExposure=", ","))
										max_exp = float(find_between(i, "maxExposure=", ","))
										#print(time_,net,fees,trades,sizeTraded,unrealizedPlusNet)
										# SymbolLayerDisplayData: 
										d= {}
										d['net'] = round(net,2)
										d['fees'] = round(fees,2)
										d['trades'] = int(trades)
										d['sizeTraded'] = int(sizeTraded)
										d['unrealizedPlusNet'] = unrealizedPlusNet
										d['timestamp'] = ts
										d['unrealized'] = round(unrealized,2)	
										d["cur_exp"] = cur_exp
										d["max_exp"] = max_exp
										
										pipe.send([SUMMARY_UPDATE,d])

									elif l[1]=="SymbolLayerDisplayData:":


										ms,ts,mili_ts = timestamp_mili_seconds(l[0])
										symbol = find_between(i, "symbol=", ",")
										lastPrice = float(find_between(i, "lastPrice=", ","))
										l1AskPrice = float(find_between(i, "l1AskPrice=", ","))
										l1BidPrice = float(find_between(i, "l1BidPrice=", ","))
										
										#log_print("Symbol received:",symbol,l1AskPrice)

										d= {}
										d['time'] = ts
										d['symbol'] = symbol
										d['lastPrice'] = lastPrice
										d['l1AskPrice'] = l1AskPrice
										d['l1BidPrice'] = l1BidPrice
										d['timestamp'] = ts
										pipe.send([SYMBOL_UPDATE,d])
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
			log_print("file_location_not detected:",file_location)
			summary_being_read = False
			time.sleep(2)



def ppro_connection_service(pipe,port):

	#keep running and don't stop
	state = False

	if test_register():
		pipe.send(["ppro_in","Connected"])
		if state == False:
			log_print("Ppro connected. Registering OSTAT")
			i = 3
			while i >0:
				if register_order_listener(port):
					log_print("OSTAT registered")
					state = True
					break
				else:
					log_print("OSTAT registeration failed")
				i-=1 
	else:
		pipe.send(["ppro_in","Disconnected"])
		state = False



def get_current_positions():

	global user
	try:
		d = {}
		p="http://localhost:8080/GetOpenPositions?user="+user
		r= requests.get(p)

		for i in r.text.splitlines():
			if "Position Symbol" in i:

				symbol = find_between(i, "Symbol=", " ")[1:-1]

				price =  float(find_between(i, "AveragePrice=", " ")[1:-1])
				share = int(find_between(i, "Volume=", " ")[1:-1])

				
				d[symbol] = (price,share) 
		
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


# x= "LocalTime=15:56:54.742,Message=OrderStatus,MarketDateTime=20210504-15:56:55.000,Currency=1,Symbol=QQQ.NQ,Gateway=2030,Side=T,OrderNumber=QIAOSUN_02000326M1791F8100000,Price=329.540000,Shares=70,Position=4,OrderState=Filled,CurrencyChargeGway=1,ChargeGway=0.21000,CurrencyChargeAct=1,ChargeAct=0.0096600,CurrencyChargeSec=1,ChargeSec=0.47750,CurrencyChargeExec=0,ChargeExec=0,CurrencyChargeClr=1,ChargeClr=0.012950,OrderFlags=129,CurrencyCharge=1,Account=1TRUENV001TNVQIAOSUN_USD1,InfoCode=255,InfoText=LiqFlags:^Tag30:14^Tag31:329.5400000^Tag150:2^Tag9730:"
# log_print(find_between(x, "MarketDateTime=", ",")[9:-4])


# try:
# 	f = open("../../algo_logs/"+datetime.now().strftime("%m-%d")+"data.csv", "x")
# except:
# 	f = open("../../algo_logs/"+datetime.now().strftime("%m-%d")+"data.csv", "w")


# writer = csv.writer(f,lineterminator = '\n')
# writer.writerow(['symbol', 'timestamp','bid','ask'])

# for i in range(10):
# 	writer.writerow(['1', '2','3',i])




### TEST. thread on summary. main on periodic check

# req = threading.Thread(target=read_summary,args=(), daemon=True)
# req.start()


# test 1  get_env

# print(get_env())

# test 2 get_current_positions

# user = "QIAOSUN"
# print(get_current_positions())

#test 3 periodical_check

# multiprocessing.freeze_support()
# send_pipe, receive_pipe = multiprocessing.Pipe()

# req = threading.Thread(target=Ppro_in,args=(4195,send_pipe), daemon=True)
# req.start()


# while True:

# 	d = receive_pipe.recv()

# 	print(d)


# port =4609





