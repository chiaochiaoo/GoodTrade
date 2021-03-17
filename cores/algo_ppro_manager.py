import time
import requests 
import socket
import threading
# register a symbol.


# pipe out update .
def timestamp_seconds(s):

	p = s.split(":")
	try:
		x = int(p[0])*3600+int(p[1])*60+int(p[2])
		return x
	except Exception as e:
		print("Timestamp conversion error:",e)
		return 0
def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data


### Take L1 quote,
### Track order status 

	# def communication(self):
		
	# 	#register, deregister trade.

	# 	while True:
	# 		d = self.pipe.recv()
	# 		if d[0] =="registration":
	# 			symbol = d[1]
	# 			self.register_to_ppro(symbol,True)
	# 		elif d[0] =="deregistration":
	# 			symbol = d[1]
	# 			self.register_to_ppro(symbol,False)

	# 	#takes in request from algo manager

	# #process all the update and send to pipe.
def algo_ppro_manager(port,pipe):

	UDP_IP = "localhost"
	UDP_PORT = port

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))

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


def decode_order(stream_data,pipe):
	if "OrderState" in stream_data:
		state = find_between(stream_data, "OrderState=", ",")
		if state =="Filled" or state =="Partially Filled":
			symbol = find_between(stream_data, "Symbol=", ",")
			side = find_between(stream_data, "Side=", ",")
			price = find_between(stream_data, "Price=", ",")
			share = find_between(stream_data, "Shares=", ",")

			data ={}
			data["symbol"]= symbol
			data["side"]= side
			data["price"]= float(price)
			data["shares"]= int(share)

			pipe.send(["order confirm",data])

def decode_l1(stream_data,pipe):
	symbol = find_between(stream_data, "Symbol=", ",")
	bid=find_between(stream_data, "BidPrice=", ",")
	ask=find_between(stream_data, "AskPrice=", ",")

	data ={}
	data["symbol"]= symbol
	data["bid"]= float(bid)
	data["ask"]= float(ask)
	pipe.send(["order update",data])

#p=price_updator()
#p.deregister("AAPL.NQ")
#p.listener()

# print(find_between(test, "Symbol=", ","))
# print(find_between(test, "Side=", ","))
# print(find_between(test, "Price=", ","))
# print(find_between(test, "Price=", ","))