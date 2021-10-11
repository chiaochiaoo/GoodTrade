import time
import requests 
import socket
import threading
from constant import *
from Util_functions import *
import csv


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

def Ppro_in(port,pipe):


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
	sock.settimeout(5)
	while True:
		rec= False
		#print("restart")
		try:
			data, addr = sock.recvfrom(1024)
			#print(data)
			rec = True
		except Exception as e:
			log_print(e)
			#register_order_listener(port)
			work = False
			pipe.send(["ppro_in","Disconnected"])

		if rec:
			stream_data = str(data)
			if work==False:
				pipe.send(["ppro_in","Connected"])
				#pipe.send(["msg","algo_ppro msg receive. all functional."])
			work=True
			type_ = find_between(stream_data, "Message=", ",")

			if type_ == "OrderStatus":
				decode_order(stream_data,pipe)
			elif type_ =="L1":
				decode_l1(stream_data,pipe,writer,l1data)
				count+=1
				if count %1000 ==0:
					save_file(f)
					f,writer = open_file()
	f.close()
	
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
	ms,ts,mili_ts = timestamp_mili_seconds(find_between(stream_data, "MarketTime=", ","))

	bidsize = int(find_between(stream_data, "BidSize=", ","))
	asksize = int(find_between(stream_data, "AskSize=", ","))
	#ts= timestamp_seconds(find_between(stream_data, "MarketTime=", ",")[:-4])

	# writer.writerow([symbol,mili_ts,bid,ask,bidsize,asksize])

	# if symbol!="QQQ.NQ":
	# 	print(stream_data)
	

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
			update_["EMAcount"]=l1data[symbol]["internal"]["EMA_count"]
			pipe.send(["order update_m",l1data[symbol],update_])

			# writer.writerow([symbol,mili_ts,bid,ask,\
			# 	l1data[symbol]["internal"]["EMA5H"],\
			# 	l1data[symbol]["internal"]["EMA5L"],\
			# 	l1data[symbol]["internal"]["EMA5C"],\
			# 	l1data[symbol]["internal"]["EMA8H"],\
			# 	l1data[symbol]["internal"]["EMA8L"],\
			# 	l1data[symbol]["internal"]["EMA8C"]])

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

			else: #induction! 
				dic["EMA5H"] = new_ema(dic["high"],dic["EMA5H"],5)
				dic["EMA5L"] = new_ema(dic["low"],dic["EMA5L"],5)
				dic["EMA5C"] = new_ema(dic["close"],dic["EMA5C"],5)

				dic["EMA8H"] = new_ema(dic["high"],dic["EMA8H"],8)
				dic["EMA8L"] = new_ema(dic["low"],dic["EMA8L"],8)
				dic["EMA8C"] = new_ema(dic["close"],dic["EMA8C"],8)

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
