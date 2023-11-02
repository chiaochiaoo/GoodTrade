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

class model:

	def __init__(self):

		self.model_initialized = False 
		self.model = {}

		self.pnl = np.array([None for i in range(570,960)])
		self.ts  = np.array([i for i in range(570,960)])
		self.spread = 0
		self.cur = 0
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

# class qfaang_model(model):

# 	def __init__(self):
# 		self.model_initialized = False 
# 		self.model = {}

# 		self.pnl = np.array([None for i in range(570,960)])
# 		self.ts  = np.array([i for i in range(570,960)])
# 		self.spread = 0
# 		self.e_pnl = []
# 		self.e_ts  = []
# 		self.cur = 0
# 		self.model_initialized = True 
# 		self.model_early_chart = False 

# 		self.historical_computed = True 
# 		self.historical_plus = [0.01,0.02,0.04]
# 		self.historical_minus = [-0.01,-0.02,-0.04]
# 		self.historical_fixpoint = 1200

# 		self.name = "TNV_Model_QFAANG"

# 		self.symbols =['MSFT','AAPL','AMZN','NFLX','GOOGL','META','QQQ']


# 	def model_init(self):

# 		self.model =  {'QQQ': 10, 'AAPL': -4, 'AMZN': -4, 'NFLX': -1, 'META': -1, 'GOOG': -4, }
# 		self.model_initialized = True 

# 	def model_early_load(self):

# 		d = threading.Thread(target=self.model_load_early_chart,daemon=True)
# 		d.start() 

# 	def model_buy(self):
# 		now = datetime.now()
# 		ts = now.strftime("_%H:%M")
# 		cmdstr =  "http://127.0.0.1:4440/Basket="+self.name+"_L"+ts+",Order=*"
# 		for symbol,share in self.model.items():
# 			cmdstr += symbol+".NQ:"+str(share)+","

# 		cmdstr= cmdstr[:-1]
# 		cmdstr+="*"

# 		print(cmdstr)
# 		requests.get(cmdstr)

# 	def model_sell(self):
# 		now = datetime.now()

# 		ts = now.strftime("_%H:%M")
# 		cmdstr =  "http://127.0.0.1:4440/Basket="+self.name+"_S"+ts+",Order=*"
# 		for symbol,share in self.model.items():
# 			cmdstr += symbol+".NQ:"+str(share*-1)+","

# 		cmdstr= cmdstr[:-1]
# 		cmdstr+="*"

# 		print(cmdstr)
# 		requests.get(cmdstr)

# 	def model_load_early_chart(self):
# 		print("loading start")
# 		dic = {}

# 		now = datetime.now(tz=pytz.timezone('US/Eastern'))
# 		ts = now.hour*60 + now.minute

# 		for key in self.model.keys():
# 		  postbody = "https://financialmodelingprep.com/api/v3/historical-chart/1min/"+key+"?apikey=a901e6d3dd9c97c657d40a2701374d2a"
# 		  r= requests.get(postbody)
# 		  # print(r.text)

# 		  d = json.loads(r.text)
# 		  dic[key] = d 

# 		earlier_pnl = np.zeros((len(dic),ts-570+1))
# 		c = 0

# 		for symbol,share in self.model.items():

# 		  df = pd.DataFrame.from_dict(dic[symbol])

# 		  df['date']= pd.to_datetime(df['date']) 
# 		  df = df.loc[df['date']>pd.Timestamp(date.today())]
# 		  df['ts'] = df['date'].dt.hour*60 + df['date'].dt.minute-570

# 		  idx = df['ts'].tolist()[:ts-570]
# 		  p = df['open'].to_numpy()[:ts-570]

# 		  diff = p*share
# 		  earlier_pnl[c][idx] = diff
# 		  mask = earlier_pnl[c]==0

# 		  earlier_pnl[c][mask]= np.interp(np.flatnonzero(mask), np.flatnonzero(~mask),  earlier_pnl[c][~mask])

# 		  c+=1

# 		s = np.sum(earlier_pnl,axis=0)
# 		s = s - s[0]

# 		self.e_pnl = s
# 		self.e_ts  = [570+i for i in range(len(self.e_pnl))]

# 		self.model_early_chart = True 
# 		print("loading complete ")

# 	def model_update(self,data):
# 		c= 0

# 		if self.model_initialized:
# 			spread = 0
# 			spreads = {}


# 			for key,share in self.model.items():

# 				if key in data:
# 					c+=(data[key]['day_current'] - data[key]['day_open'])*share

# 					spread+= (data[key]['ask'] - data[key]['bid'])*abs(share)

# 					spreads[key]=((data[key]['ask'] - data[key]['bid'])*abs(share))
# 					#print(key,round( (data[key]['ask'] - data[key]['bid'])*abs(share),1))
# 				else:
# 					print("no",key)

# 			print({k: v for k, v in sorted(spreads.items(), key=lambda item: item[1])})
			
# 			#print(np.mean(spreads))
# 			now = datetime.now(tz=pytz.timezone('US/Eastern'))
# 			ts = now.hour*60 + now.minute
# 			idx = ts-570

# 			# before = np.where(self.pnl==None)[0]
# 			# self.pnl[before[before<idx]]=0

# 			if c!=0:
# 				self.pnl[idx] = c
# 				self.spread = spread
# 				self.cur = c
# 		else:
# 			print("require init model.")
# 			pass
# 			pass#self.model_init()


# class obq_model(model):

# 	def __init__(self):
# 		self.model_initialized = False 
# 		self.model = {}
# 		self.cur = 0
# 		self.pnl = np.array([None for i in range(570,960)])
# 		self.ts  = np.array([i for i in range(570,960)])
# 		self.spread = 0
# 		self.e_pnl = []
# 		self.e_ts  = []
# 		self.model_initialized = False 
# 		self.model_early_chart = False 

# 		self.historical_computed = True 
# 		self.historical_plus = []
# 		self.historical_minus = []


# 		self.name = "TNV_Model_OBQ"

# 		self.symbols =['MSFT','AAPL','AMZN','NVDA','GOOGL','META','TSLA','AVGO','PEP','COST','CSCO','TMUS','ADBE','TXN','CMCSA','NFLX','AMD','QCOM','AMGN','INTC','HON','INTU','SBUX','GILD','AMAT','ADI','MDLZ','ISRG','ADP','REGN','PYPL','VRTX','MU','LRCX','ATVI','MELI','CSX','MRNA','PANW','CDNS','ASML','SNPS','ORLY','MNST','FTNT','CHTR','KLAC','MAR','KDP','KHC','AEP','ABNB','CTAS','LULU','DXCM','NXPI','AZN','MCHP','ADSK','EXC','BIIB','PDD','IDXX','WDAY','PAYX','XEL','SGEN','PCAR','ODFL','CPRT','ILMN','ROST','GFS','EA','MRVL','WBD','DLTR','CTSH','WBA','FAST','VRSK','CRWD','BKR','ENPH','CSGP','ANSS','FANG','ALGN','TEAM','EBAY','DDOG','ZM','JD','ZS','LCID','RIVN']

# 	def create_standard_obq_df(self):

# 		k = []
# 		c=0
# 		for symbol in self.symbols:

# 			try:
# 				postbody = "http://api.kibot.com/?action=history&symbol="+symbol+"&interval=day&period=250&user=sajali26@hotmail.com&password=guupu4upu"
# 				r= requests.post(postbody)

# 				t_df = pd.read_csv(StringIO(r.text),names=["day","open","high","low","close","volume"])
# 				t_df['day'] = pd.to_datetime(t_df['day'])
# 				t_df[symbol+"_gain"] =  np.log(t_df["close"]) - np.log(t_df["open"])
# 				t_df[symbol+"_gap"] =  np.log(t_df["open"]) - np.log(t_df.close.shift(1))
# 				t_df[symbol+"_volume"] = t_df["volume"]

# 				t_df.rename({'open': symbol+'_open', }, axis=1, inplace=True)
# 				t_df.rename({'close': symbol+'_close', }, axis=1, inplace=True)

# 				t_df = t_df.drop(["high","low","volume"],axis=1)
# 				k.append(t_df)
# 				c+=1
# 			except Exception as e:
# 				print(symbol,e)

# 		df = reduce(lambda  left,right: pd.merge(left,right,on=['day'],
# 																								how='outer'), k).fillna(0)

# 		return df

# 	def obq_original(self,df):

# 		std_window1 = 50
# 		std_window2 = 25
# 		std_window3 = 5

# 		std1_weight= 0.2
# 		std2_weight= 0.2
# 		std3_weight= 0.6

# 		for symbol in self.symbols:
# 			std1 = df[symbol+"_gain"].rolling(window=std_window1).std()
# 			std2 = df[symbol+"_gain"].rolling(window=std_window2).std()
# 			std3 = df[symbol+"_gain"].rolling(window=std_window3).std()

# 			df[symbol+"_std"] = std1*std1_weight+ std2*std2_weight + std3*std3_weight

# 			df[symbol+"_current"] = df[symbol+"_close"].shift(1)
# 			df[symbol+"_ystd"] = df[symbol+"_std"].shift(1)

# 			df[symbol+"_ystd"].replace(0, np.nan, inplace=True)

# 			df[symbol+"_ranking_norm"] = df[symbol+"_gain"]/df[symbol+"_std"]
# 			df[symbol+"_executing_norm"] = df[symbol+"_gain"]/df[symbol+"_ystd"]

# 			df[symbol+"_norm"] = df[symbol+"_executing_norm"]

# 		return df


# 	def output_to_tnv(self,df):

# 		risk = 12
# 		columns = [symbol+'_ranking_norm' for symbol in self.symbols]

# 		rename ={}
# 		for i in columns:
# 			rename[i] = i[:-13]

# 		norm_df = df[columns].copy()
# 		rank_df =  df[columns].copy().rank(axis=1,method='min')
# 		rank_df.rename(rename, axis=1, inplace=True)
# 		predicted_rank = rank_df.shift(1)*0.7 + rank_df.shift(2)*0.3

# 		predicted_rank=predicted_rank.copy().rank(axis=1,method='min')
# 		top_x = 16


# 		selected={}
# 		val = (rank_df.iloc[-1]*0.7 + rank_df.iloc[-2]*0.3).rank(method='min')
# 		shorts = val.sort_values().iloc[:top_x].index
# 		longs =  val.sort_values().iloc[-top_x:].index
# 		selected['long_std'] = longs
# 		selected['long_open'] = longs +"_open"
# 		selected['short'] = shorts +"_std"

# 		#cmdstr1 =  "https://tnv.ngrok.io/Basket="+name+",Order=*"

# 		l = {}
# 		s = {}
# 		t = {}
# 		for symbol in longs:
# 			std = df.iloc[-1][symbol+"_std"]
# 			share = int(int(round(risk/(std*df.iloc[-1][symbol+"_close"]),0)))
# 			t[symbol] = share
# 			symbol +=".NQ"
# 			#cmdstr1 += symbol+":"+str(share)+","
# 			l[symbol] = share

# 		for symbol in shorts:
# 			std = df.iloc[-1][symbol+"_std"]
# 			share = -int(int(round(risk/(std*df.iloc[-1][symbol+"_close"]),0)))
# 			t[symbol] = share
# 			symbol +=".NQ"
# 			#cmdstr1 += symbol+":"+str(share)+","

# 			s[symbol] = share

# 		return t

# 	def model_init(self):
# 		#self.model =  {'JD': 53, 'ADP': 4, 'CSCO': 32, 'SGEN': 9, 'VRTX': 5, 'CTAS': 3, 'MU': 12, 'TSLA': 2, 'NFLX': 3, 'INTC': 23, 'WBA': 21, 'MRNA': 7, 'CSX': 39, 'AAPL': 6, 'PDD': 11, 'ATVI': 62, 'LULU': -3, 'TMUS': -11, 'MNST': -19, 'MDLZ': -31, 'DDOG': -6, 'CSGP': -18, 'RIVN': -15, 'ABNB': -5, 'ANSS': -3, 'EBAY': -20, 'AMGN': -5, 'SBUX': -17, 'ZS': -3, 'GFS': -12, 'ALGN': -2, 'CDNS': -4}
		
# 		test = self.create_standard_obq_df()

# 		self.model = self.output_to_tnv(self.obq_original(test))

# 		print(self.model)
# 		self.model_initialized = True 
# 		self.model_early_chart = False 

# 	def model_early_load(self):

# 		d = threading.Thread(target=self.model_load_early_chart,daemon=True)
# 		d.start() 

# 	def model_buy(self):
# 		now = datetime.now()
# 		ts = now.strftime("_%H:%M")
# 		cmdstr =  "http://127.0.0.1:4440/Basket="+self.name+"_L"+ts+",Order=*"
# 		for symbol,share in self.model.items():
# 			cmdstr += symbol+".NQ:"+str(share)+","

# 		cmdstr= cmdstr[:-1]
# 		cmdstr+="*"

# 		print(cmdstr)
# 		requests.get(cmdstr)
# 	def model_sell(self):
# 		now = datetime.now()

# 		ts = now.strftime("_%H:%M")
# 		cmdstr =  "http://127.0.0.1:4440/Basket="+self.name+"_S"+ts+",Order=*"
# 		for symbol,share in self.model.items():
# 			cmdstr += symbol+".NQ:"+str(share*-1)+","

# 		cmdstr= cmdstr[:-1]
# 		cmdstr+="*"

# 		print(cmdstr)
# 		requests.get(cmdstr)

# 	def model_load_early_chart(self):
# 		print("loading start")
# 		dic = {}

# 		now = datetime.now(tz=pytz.timezone('US/Eastern'))
# 		ts = now.hour*60 + now.minute

# 		for key in self.model.keys():
# 		  postbody = "https://financialmodelingprep.com/api/v3/historical-chart/1min/"+key+"?apikey=a901e6d3dd9c97c657d40a2701374d2a"
# 		  r= requests.get(postbody)
# 		  # print(r.text)

# 		  d = json.loads(r.text)
# 		  dic[key] = d 

# 		earlier_pnl = np.zeros((len(dic),ts-570+1))
# 		c = 0

# 		for symbol,share in self.model.items():

# 		  df = pd.DataFrame.from_dict(dic[symbol])

# 		  df['date']= pd.to_datetime(df['date']) 
# 		  df = df.loc[df['date']>pd.Timestamp(date.today())]
# 		  df['ts'] = df['date'].dt.hour*60 + df['date'].dt.minute-570

# 		  idx = df['ts'].tolist()[:ts-570]
# 		  p = df['open'].to_numpy()[:ts-570]

# 		  diff = p*share
# 		  earlier_pnl[c][idx] = diff
# 		  mask = earlier_pnl[c]==0

# 		  earlier_pnl[c][mask]= np.interp(np.flatnonzero(mask), np.flatnonzero(~mask),  earlier_pnl[c][~mask])

# 		  c+=1

# 		s = np.sum(earlier_pnl,axis=0)
# 		s = s - s[0]

# 		self.e_pnl = s
# 		self.e_ts  = [570+i for i in range(len(self.e_pnl))]

# 		self.model_early_chart = True 
# 		print("loading complete ")



# 	def model_update(self,data):
# 		c= 0

# 		if self.model_initialized:
# 			spread = 0
# 			spreads = {}


# 			for key,share in self.model.items():

# 				if key in data:
# 					c+=(data[key]['day_current'] - data[key]['day_open'])*share

# 					spread+= (data[key]['ask'] - data[key]['bid'])*abs(share)

# 					spreads[key]=((data[key]['ask'] - data[key]['bid'])*abs(share))
# 					#print(key,round( (data[key]['ask'] - data[key]['bid'])*abs(share),1))
# 				else:
# 					print("no",key)

# 			print({k: v for k, v in sorted(spreads.items(), key=lambda item: item[1])})
			
# 			#print(np.mean(spreads))
# 			now = datetime.now(tz=pytz.timezone('US/Eastern'))
# 			ts = now.hour*60 + now.minute
# 			idx = ts-570

# 			# before = np.where(self.pnl==None)[0]
# 			# self.pnl[before[before<idx]]=0

# 			if c!=0:
# 				self.cur = c
# 				self.pnl[idx] = c
# 				self.spread = spread
# 		else:
# 			print("require init model.")
# 			pass
# 			pass#self.model_init()

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

	def model_early_load(self):

		d = threading.Thread(target=self.model_load_early_chart,daemon=True)
		d.start() 

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
			print(e)

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
			print(e)

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
			print(e)

	def model_update(self,data):

		try:
			c= 0

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
						c+=(data[key]['day_current'] - data[key]['day_open'])*share

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
			print(e)

class obq_model(quick_model):
	def __init__(self):

		super().__init__("OBQ",{},[],[])

		self.model_initialized = False 

	def model_init(self):

		self.model = self.create_standard_obq_df()
		self.model_initialized = True 

	def create_standard_obq_df(self):

		postbody = "https://financialmodelingprep.com/api/v3/nasdaq_constituent?apikey=a901e6d3dd9c97c657d40a2701374d2a"
		r= requests.get(postbody)
		d = json.loads(r.text)
		symbols = [i['symbol'] for i in d]

		k = []
		c=0
		for symbol in symbols:

			try:
				postbody = "http://api.kibot.com/?action=history&symbol="+symbol+"&interval=day&period=250&user=sajali26@hotmail.com&password=guupu4upu"
				r= requests.post(postbody)

				t_df = pd.read_csv(StringIO(r.text),names=["day","open","high","low","close","volume"])
				t_df['day'] = pd.to_datetime(t_df['day'])
				t_df[symbol+"_gain"] =  np.log(t_df["close"]) - np.log(t_df["open"])
				t_df[symbol+"_gap"] =  np.log(t_df["open"]) - np.log(t_df.close.shift(1))
				t_df[symbol+"_volume"] = t_df["volume"]

				t_df.rename({'open': symbol+'_open', }, axis=1, inplace=True)
				t_df.rename({'close': symbol+'_close', }, axis=1, inplace=True)

				t_df = t_df.drop(["high","low","volume"],axis=1)
				k.append(t_df)
				c+=1
			except Exception as e:
				print(symbol,e)

		df = reduce(lambda  left,right: pd.merge(left,right,on=['day'],
																								how='outer'), k).fillna(0)
		####### MODEL ####

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


		###### OUTPUT ########

		risk = 15 
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

		return t
