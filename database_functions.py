import requests 
import numpy as np
import threading
from Symbol_data_manager import *

class database():

	def __init__(self,s: Symbol_data_manager):
		self.data = s
		self.symbols = s.get_list()
		self.reg_list = []
		self.black_list = []
		self.lock = {}

	def start(self):
		fetch = threading.Thread(target=self.update_info, daemon=True)
		fetch.start()

	def update_info(self):

		while True: #iterate through each symbol and grab them one by one 
			#print("symbols:",self.symbols)
			for i in self.symbols:
				if i not in self.black_list and i not in self.reg_list:
					fetch = threading.Thread(target=self.fetch_high_low, args=(i,), daemon=True)
					fetch.start()
					time.sleep(1)

	def request(self,req,symbol):

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


	def fetch_high_low(self,symbol):

		#put the lock first. 
		if symbol not in self.lock:
			self.lock[symbol] = False

			if self.lock[symbol]==False:
				self.lock[symbol] = True

				req = symbol.split(".")[0]
				i = symbol

			#range data.
			postbody = "http://api.kibot.com/?action=history&symbol="+req+"&interval=daily&period=14&regularsession=1&user=sajali26@hotmail.com&password=guupu4upu"
			r= self.request(postbody, symbol)
			
			if r=="":
				self.black_list.append(symbol)

			else:
				O,H,L,C,V =1,2,3,4,5
				data=self.data

				a=data.symbol_data_openhigh_dis[i]
				b=data.symbol_data_openlow_dis[i]
				c=data.symbol_data_range_dis[i]

				for line in r.splitlines():
					lst=line.split(",")
					a.append(float(lst[H])-float(lst[L]))
					b.append(float(lst[H])-float(lst[O]))
					c.append(float(lst[O])-float(lst[L]))

				print(symbol,"Fetch range data complete:",len(a),"days")


				#set the var.
				data.symbol_data_openhigh_range[i].set(str(round(min(a),3))+"-"+str(round(max(a),3)))
				data.symbol_data_openlow_range[i].set(str(round(min(b),3))+"-"+str(round(max(b),3)))
				data.symbol_data_range_range[i].set(str(round(min(c),3))+"-"+str(round(max(c),3)))

				data.symbol_data_openhigh_val[i].set(round(np.mean(a),3))
				data.symbol_data_openlow_val[i].set(round(np.mean(b),3))
				data.symbol_data_range_val[i].set(round(np.mean(c),3))

				data.symbol_data_openhigh_std[i].set(round(np.std(a),3))
				data.symbol_data_openlow_std[i].set(round(np.std(b),3))
				data.symbol_data_range_std[i].set(round(np.std(c),3))



				###ADD the first 5 here. seperate them later. 

				postbody = "http://api.kibot.com/?action=history&symbol="+symbol+"&interval=5&period=14&regularsession=1&user=sajali26@hotmail.com&password=guupu4upu"
				r= self.request(postbody, symbol)

				if r!="":
					
					a=data.symbol_data_first5_dis[i]
					b=data.symbol_data_first5_vol_dis[i]

					for line in r.splitlines():
						lst=line.split(",")
						if lst[1]=='09:30':
							a.append(round(float(lst[3])-float(lst[4]),3))
							b.append(int(lst[6]))


					print(symbol,"Fetch first 5  data complete:",len(a),"days")


					#set the var.
					data.symbol_data_first5_range[i].set(str(round(min(a),3))+"-"+str(round(max(a),3)))

					data.symbol_data_first5_vol_range[i].set(str(int(min(b)//1000))+"k-"+str(int(max(b)/1000))+"k")


					data.symbol_data_first5_val[i].set(round(np.mean(a),3))
					data.symbol_data_first5_vol_val[i].set(int(np.mean(b)/1000))


					data.symbol_data_first5_std[i].set(round(np.std(a),3))
					data.symbol_data_first5_vol_std[i].set(int(np.std(b)/1000))


					######################



					data.data_ready[i].set(True)

					self.reg_list.append(i)

# def fetch_high_low(symbol,lst):
#     req = symbol.split(".")[0]
#     #print(symbol)
#     postbody = "http://api.kibot.com/?action=history&symbol="+req+"&interval=daily&period=14&regularsession=1&user=sajali26@hotmail.com&password=guupu4upu"
#     r= requests.post(postbody)

#     r= r.text

#     if r[:3] == "404" or r[:3] =="405":
#         print(symbol,"Not found")

#     else:
#         O =1
#         H =2
#         L =3
#         C =4
#         V =5

#         i = symbol
#         a=[]
#         b=[]
#         c=[]

#         for line in r.splitlines():
#             lst=line.split(",")
#             a.append(float(lst[H])-float(lst[L]))
#             b.append(float(lst[H])-float(lst[O]))
#             c.append(float(lst[O])-float(lst[L]))

#         print(symbol,"Fetch range data complete:",len(a),"days")


#         #set the var.
#         print(lst[0])
#         lst[0].set(str(round(max(a),3))+"-"+str(round(min(a),3)))
#         lst[1].set(str(round(max(b),3))+"-"+str(round(min(b),3)))
#         lst[2].set(str(round(max(c),3))+"-"+str(round(min(c),3)))

#         # data.symbol_data_openhigh_val[i].set(round(np.mean(a),3))
#         # data.symbol_data_openlow_val[i].set(round(np.mean(b),3))
#         # data.symbol_data_range_val[i].set(round(np.mean(c),3))

#         # data.symbol_data_openhigh_std[i].set(round(np.std(a),3))
#         # data.symbol_data_openlow_std[i].set(round(np.std(b),3))
#         # data.symbol_data_range_std[i].set(round(np.std(c),3))

#         # data.symbol_loaded.append(i)
