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


def hex_to_string(int):
	a = hex(int)[-2:]
	a = a.replace("x","0")

	return a

def hexcolor(level):
	try:
		code = int(510*(level))
		if code >255:
			first_part = code-255
			return "#FF"+hex_to_string(255-first_part)+"00"
		else:
			return "#FF"+"FF"+hex_to_string(255-code)
	except:
		return "#FFFFFF"

def flatten_symbol(symbol):
    r = requests.post('http://localhost:8080/Flatten?symbol='+str(symbol))
    if r.status_code == 200:
        print('flatten Success!')
        return True
    else:
        print("flatten Failure")

def buy_market_order(symbol,share):
    r = requests.post('http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=ARCA Buy ARCX Market DAY&shares='+str(share))
    if r.status_code == 200:
        print('buy market order Success!')
        return True
    else:
        print("Error sending buy order")

def sell_market_order(symbol,share):
    r = requests.post('http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=ARCA Sell->Short ARCX Market DAY&shares='+str(share))
    if r.status_code == 200:
        print('sell market order Success!')
        #print(r.text)
        return True
    else:
        print("Error sending sell order")

def buy_limit_order(symbol, price,share):
    price = round(price,2)
    r = requests.post('http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=ARCA Buy ARCX Limit DAY&shares='+str(share))
    if r.status_code == 200:
        print('buy limit order Success! at',price)

        return True
    else:
        print("Error sending buy order")

def sell_limit_order(symbol, price,share):
    price = round(price,2)
    r = requests.post('http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=ARCA Sell->Short ARCX Limit DAY&shares='+str(share))
    if r.status_code == 200:
        print('sell limit order Success! at ',price)
        return True
    else:
        print("Error sending sell order")

#p=price_updator()
#p.deregister("AAPL.NQ")
#p.listener()

# print(find_between(test, "Symbol=", ","))
# print(find_between(test, "Side=", ","))
# print(find_between(test, "Price=", ","))
# print(find_between(test, "Price=", ","))


		# self.algo_status[id_] = tk.StringVar()
		# self.algo_status[id_].set(status)

		# self.current_share[id_] = tk.StringVar()
		# self.current_share[id_].set("0/"+str(share))

		# self.current_share_data[id_] = 0
		# self.target_share_data[id_] = share

		# self.realized[id_] = tk.StringVar()
		# self.realized[id_].set("0")
		# self.realized_data[id_] = 0

		# self.unrealized[id_] = tk.StringVar()
		# self.unrealized[id_].set("0")
		# self.unrealized_data[id_] = 0

		# self.unrealized_pshr[id_] = tk.StringVar()
		# self.unrealized_pshr[id_].set("0")
		# self.unrealized_pshr_data[id_] = 0

		# self.average_price[id_] = tk.StringVar()
		# self.average_price[id_].set("N/A")

		# self.average_price_data[id_] = 0

		# self.risk_data[id_] = -risk

		# self.order_info[id_] = [order_type,pos,order_price,share,symbol]


#		self.tk_strings=["algo_status","realized","shares","unrealized","unrealized_pshr","average_price"]
# a=[1,2,3,4]
# print(a.pop())