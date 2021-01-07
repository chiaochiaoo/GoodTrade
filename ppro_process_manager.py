import requests
import multiprocessing
import threading
import time
from Symbol_data_manager import *

global reg_count
reg_count = 0

global lock
lock = {}

global black_list
black_list = []

global reg_list
reg_list = []

global data
data = {}

global retry_list
retry_list = []




############################################################
#### pipe in, symbol. if symbol not reg, reg. if reg, dereg.
#### main loop. for each reg, thread out and return.
#### send the updates back to the client.
############################################################


def register(symbol):
	global reg_count
	global reg_list

	try:
		p="http://localhost:8080/Register?symbol="+symbol+"&feedtype=L1"
		#p ="http://localhost:8080/GetSnapshot?symbol="+symbol+"&feedtype=L1"
		r= requests.get(p)
		p="http://localhost:8080/Register?symbol="+symbol+"&feedtype=TOS"
		#p ="http://localhost:8080/GetSnapshot?symbol="+symbol+"&feedtype=TOS"
		r= requests.get(p)

		reg_count+=1
		print(symbol,"registerd ","total:",reg_count)

		reg_list.append(symbol)

		#append it to the list. 
	except Exception as e:
		print("Register,",e)
		
		#it could be database not linked 
		

def deregister(symbol):
	global reg_count
	try:
		p="http://localhost:8080/Deregister?symbol="+symbol+"&feedtype=L1"
		r= requests.get(p)
		p="http://localhost:8080/Deregister?symbol="+symbol+"&feedtype=TOS"
		r= requests.get(p)
		reg_count-=1
		print(symbol,"deregister","total:",reg_count)
		reg_list.pop(p)

	except Exception as e:
		print("Dereg",symbol,e)

def multi_processing_price(pipe_receive):

	global black_list
	global reg_list
	global retry_list
	print("Database for Database online")

	while True:
		
		#check new symbols. 
		rec = []
		while pipe_receive.poll():
			rec.append(pipe_receive.recv())

		#bulk cmds. reg these symbols. 
		for i in rec:
			if i not in black_list:
				if i not in reg_list:
					reg = threading.Thread(target=register,args=(i,), daemon=True)
					reg.start()
				else:
					dereg = threading.Thread(target=deregister,args=(i,), daemon=True)
					dereg.start()

		#try to register again the ones that have ppro errors. 

		for i in retry_list:
			reg = threading.Thread(target=register,args=(i,), daemon=True)
			reg.start()

		#bulk cmds. get updates on these symbols. on finish, send it back to client. 
		for i in reg_list:
			info = threading.Thread(target=getinfo,args=(i,pipe_receive,), daemon=True)
			info.start()

		time.sleep(2.5)
		#send each dictionary. 
		#pipe_receive.send(data)

def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data

def timestamp(s):

	p = s.split(":")
	try:
		x = int(p[0])*60+int(p[1])
		return x
	except Exception as e:
		print("timestamp",e)
		return 0

#IF STILL THE SAME TIME, TRY TO reregister?

def init(symbol):
	global data
	data[symbol] = {}
	d = data[symbol]

	d["price"]=0
	d["timestamp"] =0
	d["time"] = ""

	d["high"] = 0
	d["low"] = 0

	d["range"] = 0
	d["last_5_range"] = 0

	d["volume"] = 0
	#only after open
	d["open"] = 0
	d["oh"] = 0
	d["ol"] = 0

	d["f5r"] = 0
	d["f5v"] = 0

	d["timetamps"] = []
	d["highs"] = []
	d["lows"] = []
	d["vols"]=[]

def process_and_send(lst,pipe):

	global lock
	status,symbol,time,timestamp,price,open_,high,low,vol  = lst[0],lst[1],lst[2],lst[3],lst[4],lst[5],lst[6],lst[7],lst[8]

	global data
	if symbol not in data:
		init(symbol)
	
	d = data[symbol]

	#pre-market
	
	d["timestamp"] =timestamp
	d["time"] = time
	d["price"] = price
	d["open"] = open_
	d["high"] = high
	d["low"] = low

	d["oh"] = round(high - open_,3)
	d["ol"] = round(open_ - low,3)


	if timestamp <570:
		if price<d["low"]:
			d["low"] = price
		if price>d["high"]:
			d["high"] = price
		d["open"] = 0
		d["oh"] = 0
		d["ol"] = 0

	d["range"] = round(d["high"] - d["low"],3)
	
	# now update the datalists. 
	if timestamp not in d["timetamps"]:
		if len(d["timetamps"])==0:
			d["timetamps"].append(timestamp-1)
		else:
			d["timetamps"].append(timestamp)
		d["highs"].append(price)
		d["lows"].append(price)
		d["vols"].append(vol)
	else:
		if price >= d["highs"][-1]:
			d["highs"][-1] = price
		if price <= d["lows"][-1]:
			d["lows"][-1] = price
		d["vols"][-1] = vol

	#print(d["timetamps"],d["highs"],d["lows"],d["vols"])
	#last 5 range
	d["last_5_range"] = round(max(d["highs"][-5:]) - min(d["lows"][-5:]),3)
	# last 5 volume
	index = min(len(d["vols"]), 5)
	d["vol"] = round((d["vols"][-1] - d["vols"][-index])/1000,2)
	
	if timestamp <575:
		d["f5r"] = d["last_5_range"]
		d["f5v"] = d["vol"]

	#pre-market
	pipe.send([status,symbol,price,time,timestamp,d["high"],d["low"],\
	d["range"],d["last_5_range"],d["vol"],d["open"],d["oh"],d["ol"],
	d["f5r"],d["f5v"]])

	lock[symbol] = False

def getinfo(symbol,pipe):
	global lock
	global retry_list
	global black_list

	if symbol not in lock:
		lock[symbol] = False
	if not lock[symbol]:
		try:
			lock[symbol] = True
			p="http://localhost:8080/GetLv1?symbol="+symbol
			r= requests.get(p)

			if(r.text =='<Response><Content>No data available symbol</Content></Response>'):
				print("No symbol found")
				black_list.append(symbol)
				pipe.send(["Unfound",symbol])
			else:
				time=find_between(r.text, "MarketTime=\"", "\"")[:-4]
				Bidprice= float(find_between(r.text, "BidPrice=\"", "\""))
				Askprice= float(find_between(r.text, "AskPrice=\"", "\""))
				open_ = float(find_between(r.text, "OpenPrice=\"", "\""))
				high = float(find_between(r.text, "HighPrice=\"", "\""))
				low = float(find_between(r.text, "LowPrice=\"", "\""))
				vol = int(find_between(r.text, "Volume=\"", "\""))
				price = round((Bidprice+Askprice)/2,4)

				ts = timestamp(time[:5])
				#print(time,price)
				process_and_send(["Connected",symbol,time,ts,price,open_,high,low,vol],pipe)

				if symbol in retry_list:
					retry_list.pop(symbol)
			#pipe.send(output)

		except Exception as e:
			print("Get info",e)
			retry_list.append(symbol)
			pipe.send(["Ppro Error",symbol])
			lock[symbol] = True

# i may need to come up with a new strucutre.
# now its like. iterate through each symbols. and wait for some seconds. do it again.

# new structure:
# Access the 

# turn someone into a single process. 

#  > link:
#  > link:

# Want: all the information are processed locally. only update is sent. 

class ppro_process_manager:

	#A big manager. Who has access to all the corresponding grids in the labels. 
	#update each symbols per, 39 seconds? 
	#run every ten seconds. 
	def __init__(self,request_pipe):
		#need to track. 1 min range/ volume. 5 min range/volume.
		#self.depositLabel['text'] = 'change the value'
		#fetch this 
		self.request = request_pipe

		self.reg_list = []
		self.black_list = []
		self.lock = {}

		self.init = False

		#repeat this every 5 seconds.

	def set_symbols_manager(self,s):

		##? 
		self.data = s

		self.data_list = s.update_list
		self.symbols = s.get_list()

		for i in self.symbols:
			self.register(i)

		self.init_info()
		self.receive_start()

	def receive_start(self):
		receive = threading.Thread(name="Thread: Database info receiver",target=self.receive_request, daemon=True)
		receive.start()

	def receive_request(self):

		#put the receive in corresponding box.
		while True:
			print(d)
			d = self.request.recv()
			status = d[0]
			symbol = d[1]

			self.data_list[0][symbol].set(status)
			if status == "Connected":
				if len(d)-1 == len(self.data_list):
					for i in range(1,len(self.data_list)):
						#self.data_list[i][symbol].set(d[i+1])
						if self.data_list[i][symbol].get()!=d[i+1]:
							self.data_list[i][symbol].set(d[i+1])

		#grab all info. 

		# take input

	def init_info(self):
		for i in self.symbols:
			self.data.change_status(i, "Connecting")
			self.register(i)

	def register(self,symbol):
		self.request.send(symbol)

	def deregister(self,symbol):
		self.request.send(symbol)
	

# if __name__ == '__main__':

# 	multiprocessing.freeze_support()
# 	request_pipe, receive_pipe = multiprocessing.Pipe()
# 	p = multiprocessing.Process(target=multi_processing_price, args=(receive_pipe,),daemon=True)
# 	p.daemon=True
# 	p.start()

# 	t = ppro_process_manager(request_pipe)
# 	t.register("AAPL.NQ")

# 	# request_pipe.send("AAPL.NQ")
# 	# request_pipe.send("AMD.NQ")

# 	while True:
# 		print(request_pipe.recv())









# on one hand, takes in new symbol and register. other hand, get current. ? 

# for every itertaions:
# 1. check if pipe/queue is empty.
	 #if not, register/deregister these symbols. 
# 2. For each of these register symbols,fetch the updates for it! 

