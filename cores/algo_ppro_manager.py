import time
import requests 
import socket
import threading
# register a symbol.


# pipe out update .


		#restarted the whole thing 
def hexcolor_green_to_red(level):

	if level>0:
		code = int(510*(level))
		#print(code,"_")
		if code >255:
			first_part = code-255
			return "#FF"+hex_to_string(255-first_part)+"00"
		else:
			return "#FF"+"FF"+hex_to_string(255-code)

	else:
		code = int(255*(abs(level)))
		first_part = 255-code

		return "#"+hex_to_string(first_part)+"FF"+hex_to_string(first_part)

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

def hex_to_string(int):
	a = hex(int)[-2:]
	a = a.replace("x","0")

	return a

#1-5 is good 
def hexcolor_red(level):
	code = int(510*(level))
	print(code,"_")
	if code >255:
		first_part = code-255
		return "#FF"+hex_to_string(255-first_part)+"00"
	else:
		return "#FF"+"FF"+hex_to_string(255-code)


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
			if side =="T": side ="S"

			data ={}
			data["symbol"]= symbol
			data["side"]= side
			data["price"]= float(price)
			data["shares"]= int(share)

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

	r = 'http://localhost:8080/Flatten?symbol='+str(symbol)
	sucess='flatten '+symbol+' Success!'
	failure='flatten '+symbol+' Failure.'
   
	req = threading.Thread(target=ppro_request, args=(r,sucess,failure,),daemon=True)
	req.start()

def buy_market_order(symbol,share):

	
	r = 'http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=ARCA Buy ARCX Market DAY&shares='+str(share)
	sucess='buy market order success on'+symbol
	failure="Error buy order on"+symbol
   
	req = threading.Thread(target=ppro_request, args=(r,sucess,failure,),daemon=True)
	req.start()


def sell_market_order(symbol,share):

	r = 'http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&ordername=ARCA Sell->Short ARCX Market DAY&shares='+str(share)
	sucess='sell market order success on'+symbol
	failure="Error sell order on"+symbol
   
	req = threading.Thread(target=ppro_request, args=(r,sucess,failure,),daemon=True)
	req.start()


def buy_limit_order(symbol, price,share):

	price = round(float(price),2)
	r = 'http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=ARCA Buy ARCX Limit DAY&shares='+str(share)
	sucess='buy limit order success on'+symbol
	failure="Error buy limit order on"+symbol
   
	req = threading.Thread(target=ppro_request, args=(r,sucess,failure,),daemon=True)
	req.start()


def sell_limit_order(symbol, price,share):
	price = round(float(price),2)

	r = 'http://localhost:8080/ExecuteOrder?symbol='+str(symbol)+'&limitprice=' + str(price) +'&ordername=ARCA Sell->Short ARCX Limit DAY&shares='+str(share)
	sucess='sell limit order success on'+symbol
	failure="Error sell limit order on"+symbol
   
	req = threading.Thread(target=ppro_request, args=(r,sucess,failure,),daemon=True)
	req.start()

def ppro_request(request,success=None,failure=None,traceid=False,symbol=None,side=None,pipe=None):
	r = requests.post(request)
	if r.status_code ==200:
		if success!=None:
			print(success)

		if traceid==True:
			get_order_id(find_between(r.text,"<Content>","</Content>"),symbol,side,pipe)  #need to grab the request id. obtain the order id. assign it to the symbol.the 

		return True
	else:
		print(failure)
		return False

def get_order_id(request_number,symbol,side,pipe):
	req = "http://localhost:8080/GetOrderNumber?requestid="+str(request_number)
	r = requests.post(req)
	if r.status_code ==200:
		#return id, symbol, and side. 
		pipe.send(["new stoporder",[find_between(r.text,"<Content>","</Content>"),symbol,side]])

####need to trace the order number to trace the stop id number. 
def stoporder_to_market_buy(symbol,price,share,pipe=None):

	price = round(float(price),2)
	#r = 'localhost:8080/SendSwiftStop?symbol=&ordername=ARCA Buy ARCX Market DAY&shares=&referenceprice=ask&swiftstopprice='
	r='http://localhost:8080/SendSwiftStop?symbol='+symbol+'&ordername=ARCA%20Buy%20ARCX%20Market%20DAY&shares='+str(share)+'&referenceprice=ask&swiftstopprice='+str(price)
	#print(r)
	sucess='stoporder buy market order success on '+symbol
	failure="Error stoporder buy market"+symbol
   
	req = threading.Thread(target=ppro_request, args=(r,sucess,failure,True,symbol,"B",pipe),daemon=True)
	req.start()


def stoporder_to_market_sell(symbol,price,share,pipe=None):

	price = round(float(price),2)
	#http://localhost:8080/SendSwiftStop?symbol=AAPL.NQ&ordername=ARCA%20Sell-%3EShort%20ARCX%20Market%20DAY&shares=10&referenceprice=bid&swiftstopprice=140.0
	#r= 'http://localhost:8080/SendSwiftStop?symbol='+symbol+'&ordername=ARCA%20Sell'+'-'+'%'+'3E'+'Short%20ARCX%20Market%20DAY&shares='+str(share)+'&referenceprice=bid&swiftstopprice'+str(price)
	#r = 'localhost:8080/SendSwiftStop?symbol='+symbol+'&ordername=ARCA Sell->Short ARCX Market DAY&shares='+str(share)+'&referenceprice=bid&swiftstopprice='+str(price)
	r= 'http://localhost:8080/SendSwiftStop?symbol='+symbol+'&ordername=ARCA%20Sell-%3EShort%20ARCX%20Market%20DAY&shares='+str(share)+'&referenceprice=bid&swiftstopprice='+str(price)
	sucess='stoporder sell market order success on '+symbol
	failure="Error sell order on"+symbol
   
	req = threading.Thread(target=ppro_request, args=(r,sucess,failure,True,symbol,"S",pipe),daemon=True)
	req.start()


def cancel_stoporder(id_):

	r="http://localhost:8080/CancelScript?scriptid="+str(id_)
	sucess='cancellation successful'
	failure="cancellation failed"

	req = threading.Thread(target=ppro_request, args=(r,sucess,failure),daemon=True)
	req.start()	

#QIAOSUN_01000016S179196100000
#cancel_stoporder("QIAOSUN_01000016S179196100000")
#stoporder_to_market_sell("QQQ.NQ",340,10)

# #get_order_id(3535810)
# while True:
#

print(2//3)

