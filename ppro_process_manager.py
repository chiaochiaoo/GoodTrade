import requests
import multiprocessing
import threading
import time
import json
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

def round_up(i):

	if i<1:
		return round(i,3)
	else:
		return round(i,2)

def fetch_yahoo(symbol):
	url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-chart"

	querystring = {"region":"US","interval":"1m","symbol":symbol,"range":"1d"}

	headers = {
		'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
		'x-rapidapi-key': "ecb76c89e1mshc1fe02b7259bd58p19ddf6jsnaad53d5c4ecb"
		}

	response = requests.request("GET", url, headers=headers, params=querystring)
	res = json.loads(response.text)

	ts =[]
	#print(res['chart']['result'][0]['indicators']['quote'][0])
	for i in res['chart']['result'][0]['timestamp']:
		ts.append(datetime.fromtimestamp(i).strftime('%H:%M'))

	#if it has 09:30. 
	high,low,m_high,m_low,f5,f5v = 0,0,0,0,0,0
	if "09:30" in ts:
		start = ts.index("09:30")
		
		high = np.array(res['chart']['result'][0]['indicators']['quote'][0]["high"][:start])
		low = np.array(res['chart']['result'][0]['indicators']['quote'][0]["low"][:start])

		high = np.max(high[high != np.array(None)])
		low = np.min(low[low != np.array(None)])


		m_high = np.array(res['chart']['result'][0]['indicators']['quote'][0]["high"][start:])
		m_low = np.array(res['chart']['result'][0]['indicators']['quote'][0]["low"][start:])

		m_high = round_up(np.max(m_high[m_high != np.array(None)]))
		m_low = round_up(np.min(m_low[m_low != np.array(None)]))


		f5_high = np.array(res['chart']['result'][0]['indicators']['quote'][0]["high"][start:start+6])
		f5_low = np.array(res['chart']['result'][0]['indicators']['quote'][0]["low"][start:start+6])

		f5_high = round_up(np.max(f5_high[f5_high != np.array(None)]))
		f5_low = round_up(np.min(f5_low[f5_low != np.array(None)]))


		f5_v = np.array(res['chart']['result'][0]['indicators']['quote'][0]["volume"][start:start+6])
		
		f5 = round_up(f5_high-f5_low) 

		f5v = np.sum(f5_v[f5_v != np.array(None)])/1000

	

	else:
		high = np.array(res['chart']['result'][0]['indicators']['quote'][0]["high"])
		low = np.array(res['chart']['result'][0]['indicators']['quote'][0]["low"])

		high = round_up(np.max(high[high != np.array(None)]))
		low = round_up(np.min(low[low != np.array(None)]))
		m_high=high
		m_low=low



	return high,low,m_high,m_low,f5,f5v
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

		if symbol not in reg_list:
			reg_list.append(symbol)

		if symbol not in lock:
			lock[symbol] = False
		else:
			lock[symbol] = False

		#append it to the list.
	except Exception as e:
		#means cannot connect.
		print("Register,",e)

		#it could be database not linked 


def deregister(symbol):
	global reg_count
	global reg_list
	#try:
	p="http://localhost:8080/Deregister?symbol="+symbol+"&feedtype=L1"
	r= requests.get(p)
	p="http://localhost:8080/Deregister?symbol="+symbol+"&feedtype=TOS"
	r= requests.get(p)
	reg_count-=1
	print(symbol,"deregister","total:",reg_count)
	reg_list.remove(symbol)

	# except Exception as e:
	# 	print("Dereg",symbol,e)

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

				#if prev thread didn't die, kill it and start a new one. 
				#print("sending",i)
				info = threading.Thread(target=getinfo,args=(i,pipe_receive,), daemon=True)
				info.start()

			#print("Registed list:",reg_list)
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
		print("Timestamp conversion error:",e)
		return 0

def timestamp_seconds(s):

	p = s.split(":")
	try:
		x = int(p[0])*3600+int(p[1])*60+int(p[2])
		return x
	except Exception as e:
		print("Timestamp conversion error:",e)
		return 0
#IF STILL THE SAME TIME, TRY TO reregister?

def init(symbol,price):

	global data

	#PH,PL,H,L
	range_data=[]
	try:
		#range_data=fetch_yahoo(symbol.split(".")[0])
		range_data=[price,price,0,0,0,0]
	except:
		print("Yahoo fetching",symbol,"error")
		range_data=[price,price,0,0,0,0]
	
	data[symbol] = {}
	d = data[symbol]

	d["price"]=price
	d["timestamp"] =0
	d["time"] = ""

	d["timestamps"] = []
	d["highs"] = []
	d["lows"] = []
	d["vols"]=[]

	#here I need to access the data from database. 
	d["high"] = range_data[2]
	d["low"] = range_data[3]

	d["phigh"] = range_data[0]
	d["plow"] =range_data[1]

	d["range"] = 0
	d["last_5_range"] = 0

	d["prev_close"] = 0
	d["prev_close_gap"] = 0

	d["volume"] = 0
	#only after open
	d["open"] = 0
	d["oh"] = 0
	d["ol"] = 0

	d["f5r"] = range_data[4]
	d["f5v"] = range_data[5]



def process_and_send(lst,pipe):

	global lock
	status,symbol,time,timestamp,price,high,low,open_,vol,prev_close  = lst[0],lst[1],lst[2],lst[3],lst[4],lst[5],lst[6],lst[7],lst[8],lst[9]

	global data

	if symbol not in data:
		init(symbol,price)

	#here;s the false print check. 0.005
	d = data[symbol]

	now = datetime.now()

	ts = now.hour*3600 + now.minute*60 + now.second
	t = str(now.minute) +":" + str(now.second)
	rec = timestamp_seconds(time)
	ms = now.hour*60 + now.minute
	latency = ts-rec

	#if abs(price-d["price"])/d["price"] < 0.02:

	d = data[symbol]

	d["timestamp"] = timestamp
	d["time"] = time
	d["price"] = price
	d["open"] = open_
	d["prev_close"] = prev_close

	#else:
	#here I set them. 

	d["high"] =high
	d["low"] = low

	if price > d["high"]:
		d["high"] = price

	if price < d["low"]:
		d["low"] = price			

	if timestamp <570:
		d["phigh"] = d["high"]
		d["plow"] = d["low"]

	d["range"] = round(d["high"] - d["low"],3)
	#print("check",d["range"],d["high"],d["low"],d["phigh"],d["plow"])

	if timestamp <570:
		d["open"] = 0
		d["oh"] = 0
		d["ol"] = 0
	else:
		d["oh"] = round(d["high"] - open_,3)
		d["ol"] = round(open_ - d["low"],3)


	d["prev_close_gap"] = round(price-prev_close,3)

	# now update the datalists.
	if timestamp not in d["timestamps"]:
		if len(d["timestamps"])==0:
			d["timestamps"].append(timestamp-1)
		else:
			d["timestamps"].append(timestamp)
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


	#check if the data is lagged. Premarket. Real. Aftermarket.
	register_again = False
	#normal
	if ms<570 or ms>960:
		if latency >60:
			status = "Lagged"
			register_again = True
	#premarket
	else:
		if latency >30:
			status = "Lagged"
			register_again = True

	pipe.send([status,symbol,price,time,timestamp,d["high"],d["low"],d["phigh"],d["plow"],\
		d["range"],d["last_5_range"],d["vol"],d["open"],d["oh"],d["ol"],
		d["f5r"],d["f5v"],d["prev_close"],d["prev_close_gap"]])

	#print("sent",symbol)

	if register_again:
		register(symbol)

	lock[symbol] = False

def getinfo(symbol,pipe):

	global black_list

	global connection_error

	if not connection_error:

		if not lock[symbol]:
			#try:
			#######################################################################
			lock[symbol] = True
			p="http://localhost:8080/GetLv1?symbol="+symbol
			r= requests.get(p,timeout=2)

			if(r.text =='<Response><Content>No data available symbol</Content></Response>'):
				print("No symbol found")
				black_list.append(symbol)
				pipe.send(["Unfound",symbol])
				lock[symbol] = False
			else:

				time=find_between(r.text, "MarketTime=\"", "\"")[:-4]

				open_ = float(find_between(r.text, "OpenPrice=\"", "\""))

				high = float(find_between(r.text, "HighPrice=\"", "\""))
				low = float(find_between(r.text, "LowPrice=\"", "\""))

				vol = int(find_between(r.text, "Volume=\"", "\""))
				prev_close = float(find_between(r.text, "ClosePrice=\"", "\""))

				Bidprice= float(find_between(r.text, "BidPrice=\"", "\""))
				Askprice= float(find_between(r.text, "AskPrice=\"", "\""))
				price = round((Bidprice+Askprice)/2,4)

				#price = float(find_between(r.text, "LastPrice=\"", "\""))

				if price<1:
					price = round(price,3)
				else:
					price = round(price,2)

				#print(time,Bidprice,Askprice,open_,high,low,vol,price)
				ts = timestamp(time[:5])

				process_and_send(["Connected",symbol,time,ts,price,high,low,open_,vol,prev_close],pipe)

				try:
					pass
					#process_and_send(["Connected",symbol,time,ts,price,high,low,open_,vol,prev_close],pipe)
				except Exception as e:
					print("PPro Process error",e)
					lock[symbol] = False
			#pipe.send(output)

			# except Exception as e:
			# 	print("Get info error:",e)
			# 	connection_error = True
			# 	pipe.send(["Ppro Error",symbol])
			# 	lock[symbol] = False

		else:
			print(symbol,"blocked call")



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


# print(fetch_yahoo("aapl"))



# on one hand, takes in new symbol and register. other hand, get current. ? 

# for every itertaions:
# 1. check if pipe/queue is empty.
	 #if not, register/deregister these symbols. 
# 2. For each of these register symbols,fetch the updates for it! 
