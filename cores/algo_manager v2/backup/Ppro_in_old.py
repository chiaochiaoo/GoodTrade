import time
import requests 
import socket
import threading
from constant import *
from Util_functions import *
import csv

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


	try:
		f = open("../../algo_logs/"+datetime.now().strftime("%m-%d")+"data.csv", "x")
	except:
		f = open("../../algo_logs/"+datetime.now().strftime("%m-%d")+"data.csv", "w")

	writer = csv.writer(f,lineterminator = '\n')
	writer.writerow(['symbol', 'timestamp','bid','ask'])
	


	pipe.send(["msg","algo_ppro working"])
	while True:
		data, addr = sock.recvfrom(1024)
		stream_data = str(data)
		if work==False:
			pipe.send(["msg","algo_ppro msg receive. all functional."])
		work=True
		type_ = find_between(stream_data, "Message=", ",")

		if type_ == "OrderStatus":
			decode_order(stream_data,pipe)
		elif type_ =="L1":
			decode_l1(stream_data,pipe,writer,l1data)

	f.close()
def ppro_connection_service(pipe,port):

	#keep running and don't stop
	state = False
	while True:

		if test_register():
			pipe.send(["status","Connected"])
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
			pipe.send(["status","Disconnected"])
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
		minute = int(p[0])*60+int(p[1])
		second = minute*60+int(p[2])
		milisecond = x*1000 + mili
		return minute,second,milisecond
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


"""
Every second -> small update.
Every minute -> One big update.

Track a 30 minutes list.
"""
def decode_l1(stream_data,pipe,writer,l1data):
	symbol = find_between(stream_data, "Symbol=", ",")
	bid=float(find_between(stream_data, "BidPrice=", ","))
	ask=float(find_between(stream_data, "AskPrice=", ","))
	#ts= timestamp_seconds(find_between(stream_data, "MarketTime=", ",")[:-4])

	mints,ts,mili_ts = timestamp_mili_seconds(find_between(stream_data, "MarketTime=", ","))

	send = False

	if symbol in l1data:
		#if either level has changed. register. 
		if l1data[symbol]["bid"]!=bid or l1data[symbol]["ask"]!=ask:
			send = True
		elif ts-l1data[symbol]["timestamp"] >1:
			send = True
		#if has been more then 2 leconds. registered.

	else: #initialize the localize database. Two parts, internal part, and external part.?? WHATS THE DIFFERNE?!! Internal (ppro in only.) Edternal: output part.
		l1data[symbol] = {}

		l1data[symbol]["internal"] = {}
		l1data[symbol]["external_per_update"] = {}
		l1data[symbol]["external_per_minute"] = {}

		l1data[symbol]["internal"]["current_minute_bins"] = []
		l1data[symbol]["internal"]["highs"] = []
		l1data[symbol]["internal"]["lows"] = []
		l1data[symbol]["internal"]["opens"] = []
		l1data[symbol]["internal"]["closes"] = []
		l1data[symbol]["internal"]["last"] = 0


		l1data[symbol]["external_per_minute"]["type"] = "Per_minute"
		l1data[symbol]["external_per_minute"]["MA6"] = 0
		l1data[symbol]["external_per_minute"]["MA12"] = 0
		l1data[symbol]["external_per_minute"]["MA18"] = 0
		l1data[symbol]["external_per_minute"]["MA24"] = 0
		l1data[symbol]["external_per_minute"]["MA30"] = 0

		l1data[symbol]["external_per_update"]["type"] = "Per_update"
		l1data[symbol]["external_per_update"]["symbol"] = symbol
		l1data[symbol]["external_per_update"]["bid"] = bid
		l1data[symbol]["external_per_update"]["ask"] = ask
		l1data[symbol]["external_per_update"]["timestamp"] = ts
		send = True

	if send:

		l1data[symbol]["external_per_minute"]["symbol"] = symbol
		l1data[symbol]["external_per_minute"]["bid"] = bid
		l1data[symbol]["external_per_minute"]["ask"] = ask
		l1data[symbol]["external_per_minute"]["timestamp"] = ts

		pipe.send(["order update",l1data[symbol]["external_per_minute"]])
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
