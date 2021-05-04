import time
import requests 
import socket
import threading


def Ppro_in(port,pipe):

	UDP_IP = "localhost"
	UDP_PORT = port

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))

	ppro_conn = threading.Thread(target=ppro_connection_service,args=(pipe,port), daemon=True)
	ppro_conn.start()

	print("Socket Created:",sock)
	
	work=False
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
			decode_l1(stream_data,pipe)

def ppro_connection_service(pipe,port):

	#keep running and don't stop
	state = False
	while True:

		if test_register():
			pipe.send(["status","Connected"])
			if state == False:
				print("Ppro connected. Registering OSTAT")
				i = 3
				while i >0:
					if register_order_listener(port):
						print("OSTAT registered")
						state = True
						break
					else:
						print("OSTAT registeration failed")
					i-=1 
		else:
			pipe.send(["status","Disconnected"])
			state = False
			
def test_register():
	try:
		p="http://localhost:8080/Register?symbol=QQQ.NQ&feedtype=L1"
		r= requests.get(p)
		#print(r.status_code)
		#print(r)
		if r.status_code==200:
			return True
		else:
			return False

	except Exception as e:
		return False



	except:
		print("register failed")
		return False

def timestamp_seconds(s):

	p = s.split(":")
	try:
		x = int(p[0])*3600+int(p[1])*60+int(p[2])
		return x
	except Exception as e:
		print("Timestamp conversion error:",e,s)
		return 0
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
		print("register failed")
		return False

def decode_order(stream_data,pipe):
	if "OrderState" in stream_data:
		#print(stream_data)
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

			pipe.send(["order rejected",data])


def decode_l1(stream_data,pipe):
	symbol = find_between(stream_data, "Symbol=", ",")
	bid=find_between(stream_data, "BidPrice=", ",")
	ask=find_between(stream_data, "AskPrice=", ",")
	ts=find_between(stream_data, "MarketTime=", ",")[:-4]

	data ={}
	data["symbol"]= symbol
	data["bid"]= float(bid)
	data["ask"]= float(ask)
	data["timestamp"]= timestamp_seconds(ts)
	#add time
	pipe.send(["order update",data])

# x= "LocalTime=15:56:54.742,Message=OrderStatus,MarketDateTime=20210504-15:56:55.000,Currency=1,Symbol=QQQ.NQ,Gateway=2030,Side=T,OrderNumber=QIAOSUN_02000326M1791F8100000,Price=329.540000,Shares=70,Position=4,OrderState=Filled,CurrencyChargeGway=1,ChargeGway=0.21000,CurrencyChargeAct=1,ChargeAct=0.0096600,CurrencyChargeSec=1,ChargeSec=0.47750,CurrencyChargeExec=0,ChargeExec=0,CurrencyChargeClr=1,ChargeClr=0.012950,OrderFlags=129,CurrencyCharge=1,Account=1TRUENV001TNVQIAOSUN_USD1,InfoCode=255,InfoText=LiqFlags:^Tag30:14^Tag31:329.5400000^Tag150:2^Tag9730:"
# print(find_between(x, "MarketDateTime=", ",")[9:-4])