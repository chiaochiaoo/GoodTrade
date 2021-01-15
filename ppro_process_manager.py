import requests
import multiprocessing
import threading
import time
from datetime import datetime

from Symbol_data_manager import *
from ppro_process_manager_client import *


global reg_count
reg_count = 0

global lock
lock = {}

global black_list
global reg_list
global data
black_list = []
reg_list = []
data = {}

global connection_error
############################################################
#### pipe in, symbol. if symbol not reg, reg. if reg, dereg.
#### main loop. for each reg, thread out and return.
#### send the updates back to the client.
############################################################


def test_register():
	try:
		p="http://localhost:8080/Deregister?symbol=AAPL.NQ&feedtype=L1"
		r= requests.get(p)
		if "Response" in r.text:
			return False
		else:
			return True

	except Exception as e:
		return True

def register(symbol):
	global reg_count
	global reg_list

	global lock

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

		if symbol not in lock:
			lock[symbol] = False

		#append it to the list. 
	except Exception as e:
		#means cannot connect. 
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
	global connection_error

	try:

		k = 0

		connection_error = True

		while True:

			# k+=1
			# if k%5 == 0:
			# 	current_time = datetime.now().strftime("%M:%S")
			# 	msg = "Server functional."+current_time
			# 	pipe_receive.send(["message",msg])

			while connection_error:
				connection_error = test_register()

				if connection_error:
					pipe_receive.send(["message","Conection failed. try again in 3 sec."])

				else:
					pipe_receive.send(["message","Connection established."])

					for i in reg_list:
						reg = threading.Thread(target=register,args=(i,), daemon=True)
						reg.start()

				time.sleep(3)

			#check new symbols. 
			reg = []
			dereg = []
			long_ = []
			short_ = []

			while pipe_receive.poll():
				rec = pipe_receive.recv()
				rec = rec.split("_")
				order,symbol = rec[0],rec[1]
				if order == "reg":
					reg.append(symbol)
				elif order == "dereg":
					dereg.append(symbol)
				elif order == "long":
					long_.append(symbol)
				elif order == "short":
					short_.append(symbol)

			#bulk cmds. reg these symbols. 
			for i in reg:
				if i not in black_list:
					reg = threading.Thread(target=register,args=(i,), daemon=True)
					reg.start()

			for i in dereg:
				dereg = threading.Thread(target=deregister,args=(i,), daemon=True)
				dereg.start()

			for i in long_:
				l = threading.Thread(target=buy_market_order,args=(i,10), daemon=True)
				l.start()

			for i in short_:
				s = threading.Thread(target=sell_market_order,args=(i,10), daemon=True)
				s.start()

			#try to register again the ones that have ppro errors. 
			#bulk cmds. get updates on these symbols. on finish, send it back to client. 
			for i in reg_list:
				info = threading.Thread(target=getinfo,args=(i,pipe_receive,), daemon=True)
				info.start()

			time.sleep(2.5)
			#send each dictionary. 
			#pipe_receive.send(data)
	except Exception as e:
		pipe_receive.send(["message",e])

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

def init(symbol,price):
	global data
	data[symbol] = {}
	d = data[symbol]

	d["price"]=price
	d["timestamp"] =0
	d["time"] = ""

	d["high"] = price
	d["low"] = price

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
		init(symbol,price)

	#here;s the false print check. 0.005
	d = data[symbol]

	now = datetime.now()
	print(now)
	print(now.hour,now.minute)
	cur =timestamp(str(now.hour)+":"+str(now.minute))
	print(cur)
	print(cur,timestamp)
	if d["timestamp"]!=0 and timestamp - d["timestamp"] >30:
		pipe.send(["Lagged",symbol])
		register(symbol)


	if abs(price-d["price"])/d["price"] < 0.005:

		d = data[symbol]

		d["timestamp"] = timestamp
		d["time"] = time
		d["price"] = price
		d["open"] = open_

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

		else:
			d["high"] = high
			d["low"] = low

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


		pipe.send([status,symbol,price,time,timestamp,d["high"],d["low"],\
		d["range"],d["last_5_range"],d["vol"],d["open"],d["oh"],d["ol"],
		d["f5r"],d["f5v"]])

	lock[symbol] = False

def getinfo(symbol,pipe):
	
	global black_list

	global connection_error

	if not connection_error:

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

					#print(time,Bidprice,Askprice,open_,high,low,vol,price)
					ts = timestamp(time[:5])

					process_and_send(["Connected",symbol,time,ts,price,open_,high,low,vol],pipe)

				#pipe.send(output)

			except Exception as e:
				print("Get info error:",e)
				connection_error = True
				pipe.send(["Ppro Error",symbol])
				lock[symbol] = False



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

# i may need to come up with a new strucutre.
# now its like. iterate through each symbols. and wait for some seconds. do it again.

# new structure:
# Access the 

# turn someone into a single process. 

#  > link:
#  > link:

# Want: all the information are processed locally. only update is sent. 


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

