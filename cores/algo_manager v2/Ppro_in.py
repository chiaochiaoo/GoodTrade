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
			ts=find_between(r.text, "MarketTime=\"", "\"")[:-4]
			#add time
			if side =="T": side ="S"

			data ={}
			data["symbol"]= symbol
			data["side"]= side
			data["price"]= float(price)
			data["shares"]= int(share)
			date["timestamp"]= timestamp_seconds(ts)
			pipe.send(["order confirm",data])

		if state =="Rejected":
			symbol = find_between(stream_data, "Symbol=", ",")
			side = find_between(stream_data, "Side=", ",")
			info = find_between(stream_data, "InfoText=", ",")
			data ={}
			if side =="T": side ="S"
			data["symbol"]= symbol
			data["side"]= side
			data["info"]=info

			pipe.send(["order rejected",data])

def decode_l1(stream_data,pipe):
	symbol = find_between(stream_data, "Symbol=", ",")
	bid=find_between(stream_data, "BidPrice=", ",")
	ask=find_between(stream_data, "AskPrice=", ",")
	ts=find_between(r.text, "MarketTime=\"", "\"")[:-4]
	data ={}
	data["symbol"]= symbol
	data["bid"]= float(bid)
	data["ask"]= float(ask)
	date["timestamp"]= timestamp_seconds(ts)
	#add time
	pipe.send(["order update",data])



# print(9*3600+30*60)
# class Ppro_in:

# 	def __init__(self):
# 		pass

# 	def ppro_in(self):
# 		while True:
# 			d = self.order_pipe.recv()

# 			if d[0] =="status":
# 				try:
# 					self.ppro_status.set("Ppro : "+str(d[1]))

# 					if str(d[1])=="Connected":
# 						self.ppro_status_["background"] = "#97FEA8"
# 					else:
# 						self.ppro_status_["background"] = "red"
# 				except Exception as e:
# 					print(e)

# 			if d[0] =="msg":
# 				print(d[1])

# 			if d[0] =="order confirm":
# 				#get symbol,price, shares.
# 				# maybe filled. maybe partial filled.
# 				self.ppro_order_confirmation(d[1])

# 			if d[0] =="order update":

# 				#update the quote, unrealized. 
# 				self.ppro_order_update(d[1])

# 			if d[0] =="order rejected":

# 				self.ppro_order_rejection(d[1])

# 			if d[0] =="new stoporder":

# 				#print("stop order received:",d[1])
# 				self.ppro_append_new_stoporder(d[1])
			
# 	#when there is a change of quantity of an order. 
