import requests 
import numpy as np
import threading
import multiprocessing
import os.path
from datetime import date
import json
import time

from Symbol_data_manager import *


#Cost - one thread.
class database_process_manager:

	#fetch, then assign. 

	#Note. This is not auto run. 
	# Each time a new symbol is added, it gets appended to the list. 

	def __init__(self,request_pipe):

		self.request = request_pipe

		self.reg_list = []
		self.black_list = []
		self.lock = {}
		# self.request_number = 0
		# self.receive_number = 0
		self.init = False

	def set_symbols_manager(self,s: Symbol_data_manager):

		self.data_status = s.data_ready
		self.data = s.data_list
		self.symbols = s.get_list()

		for i in self.symbols:
			self.send_request(i)

		self.receive_start()
		self.init = True

	def receive_start(self):
		receive = threading.Thread(name="Thread: Database info receiver",target=self.receive_request, daemon=True)
		receive.daemon = True
		receive.start()

	def send_request(self,symbol):
		self.request.send(symbol)

	def receive_request(self):

		#need to add a while loop to count how many has received.
		#deactivate it when it gets nothing to receive.

		print("Database Online: Receiving Starts")
		time.sleep(5)
		while True:
			d = self.request.recv()

			#print("receive")
			#print(d)

			symbol = d[0]

			#nothing is returned.
			if (len(d)==1):
				self.black_list.append(symbol)
			else:
				if len(d)-1 == len(self.data):
					for i in range(len(self.data)):
						self.data[i][symbol].set(d[i+1])

					self.reg_list.append(symbol)
					self.data_status[symbol].set(True)
					print(symbol," setting complete")

				else:
					print("Data length mismatch:",len(d)-1,len(self.data))


		### Upon receive, set the properties for each.
		### What if i have many symbols at the same time?


#I may not need a database-manager. Oh i still need for setting things;; we'll see?

def multi_processing_database(pipe_receive):

	print("Database for Database online")
	today = date.today().strftime("%m%d")

	while True:
		symbol = pipe_receive.recv()
		#unpack.
		print("Database processing:",symbol)

		file = "data/"+symbol+"_"+today+".txt"

		if os.path.isfile(file):
			with open(file) as json_file:
				data = json.load(json_file)
			#time.sleep(0.1)
		else:
			data = fetch_data(symbol)
			with open(file, 'w') as outfile:
				json.dump(data, outfile)

		#data append the yahooooo data.

		pipe_receive.send(data)


def request(req,symbol):
	try:
		r= requests.post(req)
		r= r.text

		if r[:3] == "404" or r[:3] =="405":
			print(symbol,"Not found")
			return ""
		else:
			return r

	except Exception as e:
		print(e)
		return ""

#result: black list or reg list. 
# {symbol:,status:,data:{}}
def fetch_data(symbol):

	#put the lock first. 
	# if symbol not in self.lock:
	# 	self.lock[symbol] = False

	# 	if self.lock[symbol]==False:
	# 		self.lock[symbol] = True

	req = symbol.split(".")[0]
	i = symbol

	#range data.
	postbody = "http://api.kibot.com/?action=history&symbol="+req+"&interval=daily&period=30&regularsession=1&user=sajali26@hotmail.com&password=guupu4upu"
	r= request(postbody, symbol)

	if r=="":

		return [symbol]
		##write shit. return nothing.
		#self.black_list.append(symbol)

	else:
		O,H,L,C,V =1,2,3,4,5


		range_=[] #data.symbol_data_openhigh_dis[i]
		openhigh_=[] #data.symbol_data_openlow_dis[i]
		openlow_=[] #data.symbol_data_range_dis[i]

		ATR = []
		previous_close = []

		d = r.splitlines()[-14:]

		prev_close = 0

		for line in d:
			lst=line.split(",")
			range_.append(float(lst[H])-float(lst[L]))
			openhigh_.append(float(lst[H])-float(lst[O]))
			openlow_.append(float(lst[O])-float(lst[L]))

			###ATR
			ra =  float(lst[H])-float(lst[L])
			o =  abs( float(lst[H])-float(lst[C]))
			c =  abs( float(lst[L])-float(lst[C]))
			tr = max(ra,o,c)
			ATR.append(tr)

			if prev_close!=0:
				gap = round(float(lst[O])-prev_close,2)
				previous_close.append(gap)

			prev_close = float(lst[C])


		print(symbol,"Fetch range data complete:",len(range_),"days")


		#set the var.
		openhigh_range=str(round(min(openhigh_),3))+"-"+str(round(max(openhigh_),3))
		openlow_range=str(round(min(openlow_),3))+"-"+str(round(max(openlow_),3))
		range_range=str(round(min(range_),3))+"-"+str(round(max(range_),3))
		prev_close_range= str(round(min(previous_close),3))+" - "+str(round(max(previous_close),3))

		openhigh_val=round(np.mean(openhigh_),3)
		openlow_val=round(np.mean(openlow_),3)
		range_val=round(np.mean(range_),3)
		prev_close_val = round(np.mean(np.abs(previous_close)),3)

		openhigh_std=round(np.std(openhigh_),3)
		openlow_std=round(np.std(openlow_),3)
		range_std=round(np.std(range_),3)
		prev_close_std = round(np.std(np.abs(previous_close)),3)

		ATR = np.mean(ATR)

		###ADD the first 5 here. seperate them later.

		postbody = "http://api.kibot.com/?action=history&symbol="+req+"&interval=5&period=14&regularsession=1&user=sajali26@hotmail.com&password=guupu4upu"
		r= request(postbody, symbol)

		if r!="":
			a=[]#data.symbol_data_first5_dis[i]
			b=[]#data.symbol_data_first5_vol_dis[i]

			c=[]#data.symbol_data_normal5_dis[i]
			d=[]#data.symbol_data_normal5_vol_dis[i]

			if r[:3]=="402":
				print("Not authorize to",symbol)
				a=[0]#data.symbol_data_first5_dis[i]
				b=[0]#data.symbol_data_first5_vol_dis[i]

				c=[0]#data.symbol_data_normal5_dis[i]
				d=[0]#data.symbol_data_normal5_vol_dis[i]
			else:
				for line in r.splitlines():
					lst=line.split(",")
					r = round(float(lst[3])-float(lst[4]),3)
					v = int(lst[6])
					if lst[1]=='09:30':
						a.append(r)
						b.append(v)
					c.append(r)
					d.append(v)


			print(symbol,"Fetch 5-min  data complete:",len(a),"days")


			#set the var.
			first5_range=str(round(min(a),3))+"-"+str(round(max(a),3))
			first5_vol_range=str(int(min(b)//1000))+"k-"+str(int(max(b)/1000))+"k"

			first5_val=round(np.mean(a),3)
			first5_vol_val=int(np.mean(b)/1000)

			first5_std=round(np.std(a),3)
			first5_vol_std=int(np.std(b)/1000)

			#######
			normal5_range=str(round(min(c),3))+"-"+str(round(max(c),3))
			normal5_vol_range=str(int(min(d)//1000))+"k-"+str(int(max(d)/1000))+"k"

			normal5_val=round(np.mean(c),3)
			normal5_vol_val=int(np.mean(d)/1000)

			normal5_std=round(np.std(c),3)
			normal5_vol_std=int(np.std(d)/1000)

			######################


			data_list = [symbol,openhigh_range,openlow_range,range_range,first5_range,first5_vol_range,normal5_range,normal5_vol_range,
					 openhigh_val,openlow_val,range_val,first5_val,first5_vol_val,normal5_val,normal5_vol_val,
					 openhigh_std,openlow_std,range_std,first5_std,first5_vol_std,normal5_std,normal5_vol_std,
					 prev_close_val,prev_close_range,prev_close_std,ATR]

			return data_list



# if __name__ == '__main__':

	# multiprocessing.freeze_support()
	# request_pipe, receive_pipe = multiprocessing.Pipe()
	# p = multiprocessing.Process(target=multi_processing_database, args=(receive_pipe,),daemon=True)
	# p.daemon=True
	# p.start()

	# t = database_process_manager(request_pipe)
	# t.send_request("AAPl")
	# t.receive_request()

	# while True:
	# 	a = 1

	# file = "data/BNGO.NQ_0106.txt"

	# if os.path.isfile(file):
	# 	with open(file) as json_file:
	# 		data1 = json.load(json_file)
	
	# data2 = fetch_data("BNGO.NQ")

	# print(data1)
	# print(data2)
	# print(data1==data2)


# symbol = "USO"
# req = "USO"
# postbody = "http://api.kibot.com/?action=history&symbol="+req+"&interval=daily&period=30&regularsession=1&user=sajali26@hotmail.com&password=guupu4upu"
# r= request(postbody, symbol)


# O,H,L,C,V =1,2,3,4,5


# range_=[] #data.symbol_data_openhigh_dis[i]
# openhigh_=[] #data.symbol_data_openlow_dis[i]
# openlow_=[] #data.symbol_data_range_dis[i]

# ATR = []
# previous_close = []

# d = r.splitlines()[-14:]

# prev_close = 0

# for line in d:
# 	lst=line.split(",")
# 	range_.append(round(float(lst[H])-float(lst[L]),2))
# 	openhigh_.append(float(lst[H])-float(lst[O]))
# 	openlow_.append(float(lst[O])-float(lst[L]))

# 	###ATR
# 	ra =  float(lst[H])-float(lst[L])

# print("Ranges from last 14 days:",range_)
# print("Avg",round(np.mean(range_),2))
# print("Std",round(np.std(range_),2))