from pannel import *
from tkinter import ttk
import requests
#Thoughts:
#Combine PPRO sutff with VOXCOM into one process.

#Create subclass for the algo manager.

#Entry strategy 

#Manage strategy

#How to get the machine to read chart?


#DATA CLASS. SUPPORT/RESISTENCE. 


#everything ppro related. sending orders, receiving orders. ,flatten.


def Ppro_out(pipe): #a sperate process. GLOBALLY. 
	while True:
		try:
			d = pipe.recv()
			type_ = d[0]

			if type_ == "Buy":

				symbol = d[1]
				share = d[2]
				buy_market_order(symbol,share)

			elif type_ =="Sell":

				symbol = d[1]
				share = d[2]
				sell_market_order(symbol,share)

			elif type_ == "Register":

				symbol = d[1]
				register(symbol)

			elif type_ == "Fallen":

				symbol = d[1]
				flatten_symbol(symbol)


		except Exception as e:
			print(e)

	# def register(self,symbol):
	# 	req = threading.Thread(target=self.register_to_ppro, args=(symbol, True,),daemon=True)
	# 	req.start()
			
	# def deregister(self,symbol):

	# 	if symbol in self.symbols:
	# 		self.symbols.remove(symbol)
	# 		self.register_to_ppro(symbol, False)

	# def register_to_ppro(self,symbol,status):

	# 	print("Registering",symbol,status)
	# 	if status == True:
	# 		postbody = "http://localhost:8080/SetOutput?symbol=" + symbol + "&region=1&feedtype=L1&output=" + str(self.port)+"&status=on"
	# 	else:
	# 		postbody = "http://localhost:8080/SetOutput?symbol=" + symbol + "&region=1&feedtype=L1&output=" + str(self.port)+"&status=off"

	# 	try:
	# 		r= requests.get(postbody)
	# 		if r.status_code==200:
	# 			return True
	# 		else:
	# 			return False
	# 	except:
	# 		print("register failed")
	# 		return False

	# def flatten_symbol(self,symbol,id_=None,status_text=None):

	# 	#check if this order is running.
	# 	running = self.check_order_running(id_,symbol)

	# 	#send once is good enough. 
	# 	if running:
	# 		flatten = threading.Thread(target=flatten_symbol,args=(symbol,), daemon=True)
	# 		flatten.start()
	# 		#self.current_share_data[id_]=0

	# 	else:
	# 		if id_!= None and status_text!= None:
	# 			if id_ in self.orders_registry:
	# 				self.orders_registry.remove(id_)

	# 				#if current order is not running. 
	# 				self.mark_off_algo(id_,self.status["Canceled"])
	# 				# current_status = status_text.get()
	# 				# if current_status=="Pending":
	# 				# 	status_text.set("Canceled")
	# 				# 	self.modify_algo_count(-1)
	# 				# else:
	# 				# 	status_text.set("Done.")






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
	failure = 0

	while True:
		r = requests.post(request)
		if r.status_code ==200:
			# if success!=None:
			# 	print(success)
			if traceid==True:
				get_order_id(find_between(r.text,"<Content>","</Content>"),symbol,side,pipe)  #need to grab the request id. obtain the order id. assign it to the symbol.the 
			return True
		else:
			print(failure)
			#return False
			failure +=1

		if failure>4:
			break

	return False

def get_order_id(request_number,symbol,side,pipe):
	count=0
	while True:
		req = "http://localhost:8080/GetOrderNumber?requestid="+str(request_number)
		r = requests.post(req)
		if r.status_code ==200:
			#return id, symbol, and side. 
			print(symbol,side,"stop id aquired")
			pipe.send(["new stoporder",[find_between(r.text,"<Content>","</Content>"),symbol,side]])
			break
		else:
			count = count+1
			print(symbol,side,"get id failed:",count)

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


def get_stoporder_status(id_):

	req = 'http://localhost:8080/GetScriptState?scriptid='+id_
	r = requests.post(req)

	return (find_between(r.text,"<Content>","</Content>"))

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