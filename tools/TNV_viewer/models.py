import numpy as np
import time 
import threading
import requests 
import json
import numpy as np
import pytz
from datetime import datetime
from datetime import date
import pandas as pd 
from functools import reduce
import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

import tkinter as tk
from tkinter import ttk
import io 
import os
import traceback
def PrintException(info,additional="ERROR"):
    # exc_type, exc_obj, tb = sys.exc_info()
    # f = tb.tb_frame
    # lineno = tb.tb_lineno
    # filename = f.f_code.co_filename
    # linecache.checkcache(filename)
    # line = linecache.getline(filename, lineno, f.f_globals)
    # log_print (info+'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(additional,info,exc_type, fname, exc_tb.tb_lineno,traceback.format_exc())


class model:

	def __init__(self):

		self.model_initialized = False 
		self.model = {}

		self.long_symbols =""
		self.short_symbols =""
		self.pnl = np.array([None for i in range(570,960)])
		self.ts  = np.array([i for i in range(570,960)])
		self.spread = 0
		self.cur = 0
		self.long = 0
		self.short =0
		self.e_pnl = []
		self.e_ts  = []

		self.model_initialized = True 
		self.model_early_chart = False 
		self.historical_computed = False 

		self.historical_computed = False
		self.historical_plus = []
		self.historical_minus = []
		self.historical_fixpoint = 0

		self.name = []
		self.symbols =[]


		self.profit = tk.DoubleVar(value=0)
		self.stop = tk.DoubleVar(value=0)

	def model_init(self):
		pass
	def model_early_load(self):
		pass
	def model_load_early_chart(self):
		pass
	def model_update(self):
		pass
	def get_ts(self):
		return self.ts 

	def get_pnl(self):
		return self.pnl 

	def get_long(self):
		return self.long 

	def get_short(self):
		return self.short*-1

	def get_long_symbols(self):

		return self.long_symbols 
	def get_short_symbols(self):


		return self.short_symbols 
	def get_early_ts(self):
		return self.e_ts 

	def get_early_pnl(self):
		return self.e_pnl 

	def model_today_data(self):
		pass 

	def get_spread(self):

		return str(round(self.spread,2))

	def get_price(self):

		return  str(round(self.cur,2))


class quick_model(model):

	def __init__(self,name,model,historical_plus,historical_minus):

		super().__init__()

		self.model_initialized = True 
		self.model = {}

		self.pnl = np.array([None for i in range(570,960)])
		self.ts  = np.array([i for i in range(570,960)])
		self.spread = 0
		self.e_pnl = []
		self.e_ts  = []
		self.cur = 0
		self.model_initialized = True 
		self.model_early_chart = False 

		self.name = "TNV_Model_" + name #"QFAANG"

		self.model =  model 
		self.model_initialized = True 

		self.historical_computed = True 
		self.historical_plus = historical_plus
		self.historical_minus = historical_minus
		self.historical_fixpoint = 0


		self.model_init()

	def model_init(self):

		self.long_symbols = ""

		for symbol,share in self.model.items():

			if share>0:
				self.long_symbols += (str(symbol)+":"+str(share)+",")

		self.long_symbols  = self.long_symbols[:-1]

		self.short_symbols = ""

		for symbol,share in self.model.items():

			if share<0:
				self.short_symbols   += (str(symbol)+":"+str(share)+",")

		self.short_symbols  = self.short_symbols[:-1]

	def model_early_load(self):

		if self.model_initialized :
			d = threading.Thread(target=self.model_load_early_chart,daemon=True)
			d.start() 
		else:
			print(" Model not Init.")
	def model_buy(self):

		try:
			now = datetime.now()
			ts = now.strftime("_%H:%M")
			cmdstr =  "http://127.0.0.1:4440/Basket="+self.name+"_L"+ts+",Order=*"
			for symbol,share in self.model.items():
				cmdstr += symbol+":"+str(share)+","

			cmdstr= cmdstr[:-1]
			cmdstr+="*"


			cmdstr+="Infos=("
			if self.profit.get()>0:
				cmdstr+="Profit="+str(int(self.profit.get()))+","
			if self.stop.get()>0:	
				cmdstr+="Stop="+str(int(self.profit.get()))+","
			cmdstr+=")"
			print(cmdstr)
			requests.get(cmdstr)
		except Exception as e:
			PrintException(e)

	def model_sell(self):

		try:
			now = datetime.now()

			ts = now.strftime("_%H:%M")
			cmdstr =  "http://127.0.0.1:4440/Basket="+self.name+"_S"+ts+",Order=*"
			for symbol,share in self.model.items():
				cmdstr += symbol+":"+str(share*-1)+","

			cmdstr= cmdstr[:-1]
			cmdstr+="*"

			cmdstr+="Infos=("
			if self.profit.get()>0:
				cmdstr+="Profit="+str(int(self.profit.get()))+","
			if self.stop.get()>0:	
				cmdstr+="Stop="+str(int(self.stop.get()))+","
			cmdstr+=")"
			print(cmdstr)
			requests.get(cmdstr)

		except Exception as e:
			PrintException(e)

	def model_load_early_chart(self):

		try:
			print("loading start")
			dic = {}

			now = datetime.now(tz=pytz.timezone('US/Eastern'))
			ts = now.hour*60 + now.minute

			for key in self.model.keys():
			  postbody = "https://financialmodelingprep.com/api/v3/historical-chart/1min/"+key[:-3]+"?apikey=a901e6d3dd9c97c657d40a2701374d2a"
			  r= requests.get(postbody)
			  # print(r.text)

			  d = json.loads(r.text)
			  dic[key] = d 

			earlier_pnl = np.zeros((len(dic),ts-570+1))
			c = 0

			for symbol,share in self.model.items():

			  df = pd.DataFrame.from_dict(dic[symbol])

			  df['date']= pd.to_datetime(df['date']) 
			  df = df.loc[df['date']>pd.Timestamp(date.today())]
			  df['ts'] = df['date'].dt.hour*60 + df['date'].dt.minute-570

			  idx = df['ts'].tolist()[:ts-570]
			  p = df['open'].to_numpy()[:ts-570]

			  diff = p*share
			  earlier_pnl[c][idx] = diff
			  mask = earlier_pnl[c]==0

			  earlier_pnl[c][mask]= np.interp(np.flatnonzero(mask), np.flatnonzero(~mask),  earlier_pnl[c][~mask])

			  c+=1

			s = np.sum(earlier_pnl,axis=0)
			s = s - s[0]

			self.e_pnl = s
			self.e_ts  = [570+i for i in range(len(self.e_pnl))]

			self.model_early_chart = True 
			print("loading complete ")

		except Exception as e:
			PrintException(e)

	def model_update(self,data):

		try:
			c= 0
			self.long =0
			self.short = 0
			if self.model_initialized:
				spread = 0
				spreads = {}


				if self.historical_fixpoint==0:
					for key,share in self.model.items():
						key = key[:-3]
						self.historical_fixpoint +=  data[key]['day_open']*share


				for key,share in self.model.items():

					key = key[:-3]
					
					if key in data:
						result = (data[key]['day_current'] - data[key]['day_open'])*share
						c+=result

						if share>0:
							self.long += result 
						else:
							self.short += result

						spread+= (data[key]['ask'] - data[key]['bid'])*abs(share)

						spreads[key]=((data[key]['ask'] - data[key]['bid'])*abs(share))
						#print(key,round( (data[key]['ask'] - data[key]['bid'])*abs(share),1))
					else:
						print("no",key)



				print({k: v for k, v in sorted(spreads.items(), key=lambda item: item[1])})
				
				#print(np.mean(spreads))
				now = datetime.now(tz=pytz.timezone('US/Eastern'))
				ts = now.hour*60 + now.minute
				idx = ts-570

				# before = np.where(self.pnl==None)[0]
				# self.pnl[before[before<idx]]=0

				if c!=0:
					self.pnl[idx] = c
					self.spread = spread
					self.cur = c
			else:
				print("require init model.")
				pass
				pass#self.model_init()
		except Exception as e:
			PrintException(self.name,e)

class obq_model(quick_model):
	def __init__(self):

		super().__init__("OBQ",{},[],[])

		self.model_initialized = False 

	def model_init(self):

		d = threading.Thread(target=self.create_standard_obq_df,daemon=True)
		d.start() 


	def create_standard_obq_df(self):


			# STEP 1 , obtain symbols.
		try:
			print("loading OBQ")
			postbody = "https://financialmodelingprep.com/api/v3/nasdaq_constituent?apikey=a901e6d3dd9c97c657d40a2701374d2a"
			r= requests.get(postbody)
			d = json.loads(r.text)
			symbols = [i['symbol'] for i in d]

			print("symbol count:",symbols.__len__())

			# step 2, get the df. 

			k = []
			c=0
			skips = []
			for symbol in symbols:

			  try:
			    postbody = "http://api.kibot.com/?action=history&symbol="+symbol+"&interval=day&period=100&user=sajali26@hotmail.com&password=guupu4upu"
			    r= requests.post(postbody)

			    t_df = pd.read_csv(StringIO(r.text),names=["day","open","high","low","close","volume"])
			    t_df['day'] = pd.to_datetime(t_df['day'])
			    t_df[symbol+"_gain"] =  np.log(t_df["close"]) - np.log(t_df["open"])
			    t_df[symbol+"_gap"] =  np.log(t_df["open"]) - np.log(t_df.close.shift(1))
			    t_df[symbol+"_volume"] = t_df["volume"]
			 
			    t_df[symbol+"_std"] =0
			    t_df[symbol+"_current"] =0
			    t_df[symbol+"_ystd"] =0
			    t_df[symbol+"_ranking_norm"] =0
			    t_df[symbol+"_executing_norm"] =0
			    t_df[symbol+"_norm"] =0
			    
			    t_df.rename({'open': symbol+'_open', }, axis=1, inplace=True)
			    t_df.rename({'close': symbol+'_close', }, axis=1, inplace=True)

			    t_df = t_df.drop(["high","low","volume"],axis=1)

			    ####### EXCLUDE SYMBOL $500 and above ####

			    if t_df[symbol+"_open"].iloc[-1]>600:
			      skips.append(symbol)
			    else:
			      k.append(t_df)
			    c+=1
			  except Exception as e:
			    PrintException(symbol,e)

			df = reduce(lambda  left,right: pd.merge(left,right,on=['day'],how='outer'), k).fillna(0)
			print("actual:",k.__len__()," skipping:",skips)


			symbols = [x for x in symbols if x not in skips]



			### STEP 3 MODEL ####

			std_window1 = 50
			std_window2 = 25
			std_window3 = 5

			std1_weight= 0.2
			std2_weight= 0.2
			std3_weight= 0.6

			for symbol in symbols:
			  std1 = df[symbol+"_gain"].rolling(window=std_window1).std()
			  std2 = df[symbol+"_gain"].rolling(window=std_window2).std()
			  std3 = df[symbol+"_gain"].rolling(window=std_window3).std()

			  df[symbol+"_std"] = std1*std1_weight+ std2*std2_weight + std3*std3_weight

			  df[symbol+"_current"] = df[symbol+"_close"].shift(1)
			  df[symbol+"_ystd"] = df[symbol+"_std"].shift(1)

			  df[symbol+"_ystd"].replace(0, np.nan, inplace=True)

			  df[symbol+"_ranking_norm"] = df[symbol+"_gain"]/df[symbol+"_std"]
			  df[symbol+"_executing_norm"] = df[symbol+"_gain"]/df[symbol+"_ystd"]

			  df[symbol+"_norm"] = df[symbol+"_executing_norm"]

			# for symbol in symbols:
			#   print(symbol,df[symbol+"_std"].iloc[-1])


			### STEP 4 OUTPUT ###

			risk = 12 
			columns = [symbol+'_ranking_norm' for symbol in symbols]

			rename ={}
			for i in columns:
			  rename[i] = i[:-13]

			norm_df = df[columns].copy()
			rank_df =  df[columns].copy().rank(axis=1,method='min')
			rank_df.rename(rename, axis=1, inplace=True)
			predicted_rank = rank_df.shift(1)*0.7 + rank_df.shift(2)*0.3

			predicted_rank=predicted_rank.copy().rank(axis=1,method='min')
			top_x = 16

			selected={}
			val = (rank_df.iloc[-1]*0.7 + rank_df.iloc[-2]*0.3).rank(method='min')
			shorts = val.sort_values().iloc[:top_x].index
			longs =  val.sort_values().iloc[-top_x:].index


			selected['long_std'] = longs
			selected['long_open'] = longs +"_open"
			selected['short'] = shorts +"_std"

			l = {}
			s = {}
			t = {}
			for symbol in longs:
			  std = df.iloc[-1][symbol+"_std"]
			  share = int(int(round(risk/(std*df.iloc[-1][symbol+"_close"]),0)))
			  t[symbol+".NQ"] = share
			  symbol +=".NQ"

			  l[symbol] = share

			for symbol in shorts:
			  std = df.iloc[-1][symbol+"_std"]
			  share = -int(int(round(risk/(std*df.iloc[-1][symbol+"_close"]),0)))
			  t[symbol+".NQ"] = share
			  symbol +=".NQ"
			  s[symbol] = share

			self.model = t
			self.model_initialized = True 
			print("OBQ loading complete")

			super().model_init()
		except Exception as e:
			PrintException(e)
