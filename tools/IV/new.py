import tkinter as tk   
from tkinter import ttk                  
import csv
import json
import time
import multiprocessing
import threading
import requests
import socket
from datetime import datetime
from psutil import process_iter
import psutil
import pickle
import os
import pandas as pd

import pandas as pd
import numpy as np
import requests
import json
import datetime
import itertools
from io import StringIO




def process_symbol_data(symbol,df,ndf):
  ########## PROCESS ##################

  df['symbol'] = symbol

  df['pc'] = df['close'].shift(1)
  df['po'] = df['open'].shift(1)

  df['log_ret'] = np.log(df['close']) - np.log(df['open'])

  df['std_14d'] = df['log_ret'].rolling(14).std().shift(1)
  df['std_30d'] = df['log_ret'].rolling(30).std().shift(1)
  df['std_60d'] = df['log_ret'].rolling(60).std().shift(1)

  df['gain_norm_60d'] = df['log_ret']/df['std_60d']
  df['pgain_norm_60d'] = df['log_ret'].shift(1)/df['std_60d']

  df['p2gain_norm_60d'] = (df['log_ret'].shift(1)+df['log_ret'].shift(2))/df['std_60d']
  df['gap_norm_60d'] =  (np.log(df['open']) - np.log(df['pc']))/df['std_60d']
  df['utg_norm_60d'] =  (np.log(df['open']) - np.log(df['po']))/df['std_60d']

  df['std_14_rps'] = df['pc']*df['std_14d']
  df['std_30_rps'] = df['pc']*df['std_30d']
  df['std_60_rps'] = df['pc']*df['std_60d']

  # df['bw_relv'] = df['volume']/df['volume'].shift(1).rolling(10).mean()
  # df['m_relv'] = df['volume']/df['volume'].shift(1).rolling(20).mean()
  # df['q_relv'] = df['volume']/df['volume'].shift(1).rolling(60).mean()
  # df['hy_relv'] = df['volume']/df['volume'].shift(1).rolling(120).mean()
  # df['y_relv'] = df['volume']/df['volume'].shift(1).rolling(252).mean()

  if len(ndf)!=0:
    l =ndf['open'].to_numpy().reshape(len(df),len(ndf)//len(df))
    # v = ndf['acc_vol'].to_numpy().reshape(len(df),len(ndf)//len(df))
    # bv = ndf['volume'].to_numpy().reshape(len(df),len(ndf)//len(df))
    ts = [945, 946, 947, 948, 949, 950, 951, 952, 953, 954, 955,956, 957, 958, 959, 960]
    com = ["g"+str(i) for i in ts]

    df[com] = l[:len(df)]

    # v_part = ["accv"+str(i) for i in ts]
    # df[v_part] = v

    # bv_part = ["bv"+str(i) for i in ts]
    # df[bv_part] = bv

  df['itc'] = np.log(df['g950']) - np.log(df['g960'])
  df['itc_std'] = df['itc'].rolling(60).std().shift(1)

  df['itc_rps'] = df['pc']*df['itc_std']

  df = df[['day','symbol','open','itc_std','itc_rps']]

  # for i in [0,1,2,3,4,5,6,7,8]:
  #   df['imb'+str(i)] = 0
    # df['95095'+str(i)+'g'] = (np.log(df['g95'+str(i)]) - np.log(df['g950']))/df['itc_std']
    # df['itc95'+str(i)+'g'] = (np.log(df['close']) - np.log(df['g95'+str(i)]))/df['itc_std']
  return df.iloc[-1]

def get_symbol_data(symbol):

  days = 90

  postbody = "http://api.kibot.com/?action=history&symbol="+symbol+"&interval="+str(10)+"&period="+str(days)+"&regular=1&user=sajali26@hotmail.com&password=guupu4upu"
  r= requests.post(postbody)

  ndf  = pd.read_csv(StringIO(r.text),names=["day","time","open","high","low","close","volume"])

  ndf = ndf.loc[ndf['time']=="15:50"]

  df =ndf
  df['itc'] = np.log(df['close']) - np.log(df['open'])
  df['itc_std'] = df['itc'].rolling(60).std().shift(1)
  df['pc'] = df['close'].shift(1)
  df['itc_rps'] = df['pc']*df['itc_std']

  return df.iloc[-1]['itc_rps']
def get_symbol_data_TO(symbol):

  total = []

  #print(days)
  days=120
  for i in range(days//5):

    start = datetime.datetime.today() - datetime.timedelta(days=6*i)
    end = start - datetime.timedelta(days=5)

    start = start.strftime('%Y-%m-%d')
    end = end.strftime('%Y-%m-%d')

    postbody = "https://financialmodelingprep.com/api/v3/historical-chart/5min/"+symbol+"?from="+end+"&to="+start+"&apikey=a901e6d3dd9c97c657d40a2701374d2a"

    r= requests.get(postbody)

    d = json.loads(r.text)
    d = pd.DataFrame.from_dict(d)
    total.append(d)

  d = pd.concat(total)

  d['date'] = pd.to_datetime(d['date'])
  d['time'] = d['date'].dt.strftime('%H:%M')
  d = d.sort_values(by=['date']).reset_index(drop=True)

  d = d.loc[d['time']=="15:45"]

  d['itc'] = np.log(d['close']) - np.log(d['open'])
  d['itc_std'] = d['itc'].rolling(60).std().shift(1)
  d['itc_rps'] = d['open']*d['itc_std']

  return d

def sending_close_algo(algo,symbols):

    cmdstr =  "https://tnv.ngrok.io/Basket="+algo+",Order=*"

    for symbol,share in symbols.items():
      cmdstr += symbol+str(int(share))+","

    cmdstr= cmdstr[:-1]
    cmdstr+="*"

    #print(cmdstr)
    requests.get(cmdstr)
    #print(cmdstr)
    return cmdstr

def long_algo(df,name,risk):

  orders = {}
  df['share'] = (risk//df['itc_std']).astype(int)

  for symbol,row in df.iterrows():

    share = row['share']
    orders[symbol] = share 

  sending_close_algo(name,orders)


def short_algo(df,name,risk):

  orders = {}
  df['share'] = (-risk//df['itc_std']).astype(int)

  for symbol,row in df.iterrows():
    share = row['share']
    orders[symbol] = share 

  sending_close_algo(name,orders)

def update_imbalance(symbol,ts,v,side,cts,df,update):

  if side =="S":
    v = -v
    
  # update cur.
  if symbol in update:
    update[symbol] = v 

  #print(ts,cts)
  # check global event
  if ts>cts:
    print("cts:",cts)

    if cts in df:
      df[cts] = list(update.values())
      algo(cts,df)

      keys =df.index.to_list()

      for key in keys:
        update[key] = 0

      #display(df)
    cts=ts

    df.to_csv("imb_test.csv")
  
  return cts
  
def algo(cts,df):

  # if 15:50 more than up or down 0.5m , take it
  risk = 5
  select = df.loc[df[cts]>250000]

  name = "DC"+str(cts)
  if len(select)>0:
    #print("select",long_algo(select,risk))
    name+="L_"
    long_algo(select,name,risk)
    

  select = df.loc[df[cts]<-250000]

  if len(select)>0:
    #print("select",short_algo(select,risk))
    name+="S_"
    short_algo(select,name,risk)

def init_close_df(symbols):
  d= {}

  for symbol in symbols:

    d[symbol] = {}
    sym = symbol.split(".")[0]
    d[symbol]['itc_std'] = get_symbol_data(sym)
    if symbol[-2:]=="TO":
      d[symbol]['itc_std'] =get_symbol_data_TO(symbol)
    
    for i in [950,951,952,953,954,955,956,957,958,959]:
      d[symbol][i] = 0

  df = pd.DataFrame.from_dict(d,orient='index')
  return df

def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data
def timestamp_seconds(s):

	p = s[:-4].split(":")
	dec = s.split(".")
	try:
		x = int(p[0])*3600+int(p[1])*60+int(p[2])+int(dec[1])/1000
		#print(x)
		return x
	except Exception as e:
		print("Timestamp conversion error:",e,int(dec[1])/1000)
		return 0
def timestamp(s):
	p = s.split(":")
	try:
		x = int(p[0])*60+int(p[1])
		return x
	except Exception as e:
		print("Timestamp conversion error:",e)
		return 0

##############################
### START A SIMPLE VERSION ###
##############################


earning_list = []

class processor:

	def __init__(self):

		# with open("data.json") as f:
		# 	self.data = json.load(f)

		# self.etfs_names = self.data["all_etfs"]
		# self.symbols= self.data.keys()
		# self.sendpipe = send_pipe
		#print(self.etfs,self.symbols)

		"""For each etf, create a data object """
		# self.etfs = {}

		#additionals = ["FXI","USO","GLD"]
		self.all_symbols = ["FXI","USO","GLD"]
		
		# open db folder . find each file. 


		self.all_symbols = list(set(self.all_symbols))

		self.registered = True 
		self.termination = True 

		now = datetime.now()
		ts = now.hour*60 + now.minute

		c = 0
		k = 0 

		self.registered = False 


		register_ts = 0
		while True:

			try:
				now = datetime.now()
				ts = now.hour*60 + now.minute

				if (ts >=525 and ts<=530) or (ts>935 and ts<940):
					k = 0 
					self.registered = False 
					self.termination = False 
				else:
					k +=1 

				if k>1 and self.registered==False:

					earning_list = earning_tracking()

					force_close_port(4135)
					postbody = "http://localhost:8080/SetOutput?symbol=*.NQ,*.AM,*.NY&feedtype=IMBALANCE&output=4135&status=on"

					try:
						r= requests.post(postbody)
					except Exception as e:
						print(e)

					send_pipe, receive_pipe = multiprocessing.Pipe()

					process_ppro = multiprocessing.Process(target=running_mode, args=(send_pipe,),daemon=True)
					process_ppro.daemon=True
					process_ppro.start()

					process_ppro2 = multiprocessing.Process(target=writer, args=(receive_pipe,),daemon=True)
					process_ppro2.daemon=True
					process_ppro2.start()

					self.registered=True

				if k>5 and self.registered==True and self.termination==False:
					postbody =  "http://localhost:8080/SetOutput?symbol=*.NQ,*.AM,*.NY&feedtype=IMBALANCE&output=4135&status=on"

					try:
						r= requests.post(postbody)
					except Exception as e:
						print(e)

				if k>40 and self.termination==False:


					print("terminating....")

					send_pipe.send("good")
					time.sleep(5)
					process_ppro.terminate()
					process_ppro.join()
					process_ppro2.terminate()
					process_ppro2.join()				

					self.termination = True 

				print("current ts:",ts,	self.registered,self.termination,k)

				time.sleep(60)

			except Exception as e :
				print(e)

	def open_file(self):

		try:
			self.f = open("saves/"+datetime.now().strftime("%m-%d")+".csv", "x")
		except:
			self.f = open("saves/"+datetime.now().strftime("%m-%d")+".csv", "w")

		self.f.close()


def force_close_port(port, process_name=None):
	"""Terminate a process that is bound to a port.
	
	The process name can be set (eg. python), which will
	ignore any other process that doesn't start with it.
	"""
	print("killing 4135",port)
	for proc in psutil.process_iter():
		for conn in proc.connections():
			if conn.laddr[1] == port:
				#Don't close if it belongs to SYSTEM
				#On windows using .username() results in AccessDenied
				#TODO: Needs testing on other operating systems
				try:
					proc.username()
				except psutil.AccessDenied:
					pass
				else:
					if process_name is None or proc.name().startswith(process_name):
						try:
							proc.kill()
						except (psutil.NoSuchProcess, psutil.AccessDenied):
							pass 


def writer(receive_pipe):

	nyse_long = []
	nyse_short = []

	nq_long = []
	nq_short = []

	already_sent_long = []
	already_sent_short = []


	earning_long = []
	earning_short = []

	lst  = ["LocalTime=",
	"MarketTime=",
	"Side=",
	"Type=",
	"Status=",
	"Symbol=",
	"Price=",
	"Volume=",
	"Source=",
	"AuctionPrice=",
	"ContinuousPrice=",
	"PairedVolume=",
	"MktOrdVolume=",
	"MktOrdSide=",
	"NearIndicativeClosingPx=",
	"FarIndicativeClosingPx=",
	"PxVariation=",]
	header = [i[:-1] for i in lst]
	count = 0

	now = datetime.now()
	ts = now.hour*60 + now.minute


	file = ""
	if ts<800:
		file = "saves/M_"+datetime.now().strftime("%m-%d")+".csv"
	else:
		file = "saves/N_"+datetime.now().strftime("%m-%d")+".csv"

	print("Writer functional",file)

	print("earning list:",earning_list)

	coefficient = 1

	prev_time = 0

	moo_release = False

	############ DF BLOCK ################################

	update = {}
	symbols = ['QQQ.NQ','TQQQ.NQ','UVXY.AM','SQQQ.NQ','SPY.AM',"XLY.AM", "XLC.AM", "XLP.AM" ,"XLE.AM" ,"XLF.AM", "XLV.AM", "XLI.AM", "XLB.AM", "XLRE.AM", "XLK.AM", "XLU.AM"]

	df = init_close_df(symbols)

	keys =df.index.to_list()
	for key in keys:
	  update[key] = 0

	cts = 950

	########################################################

	with open(file, 'a+',newline='') as csvfile2:
		writer = csv.writer(csvfile2)
		writer.writerow(header)
		while True:
			r = receive_pipe.recv()
			count+=1
			if r =="good":
				break

			d=[]
			for i in lst:
				if i in ["Price=","Volume=","AuctionPrice=","ContinuousPrice=","PairedVolume=","MktOrdVolume="]:
					try:
						d.append(float(find_between(r,i,",")))
					except:
						print(len(row))
				elif i in ["LocalTime=","MarketTime="]:
				  d.append(timestamp_seconds(find_between(r, i, ",")))
				elif i =="PxVariation=":
				  d.append(float(find_between(r,i,"\\")))
				  #print(find_between(r,i,"\\"))
				else:
				  d.append(find_between(r,i,","))


			try:
				symbol = find_between(r,"Symbol=",",")
				pair = float(find_between(r,"PairedVolume=",","))

				price =  float(find_between(r,"AuctionPrice=",","))

				size = float(find_between(r,"Volume=",","))
				time_ = timestamp_seconds(find_between(r, "MarketTime=", ","))

				side = find_between(r,"Side=",",")

				if time_>57000:
					ts = int(time_//60)
					cts = update_imbalance(symbol,ts,size,side,cts,df,update)

				# 09:25
				if time_>=33900 and time_ <= 33930 and symbol[-2:]=="NQ":

						# print(time_,symbol,side,pair,size)
						# if side =="B":
						# 	earning_long.append(symbol)
						# else:
						# 	earning_short.append(symbol)

					if symbol[:-3] in earning_list: #if size >250000:

						#print(symbol,pair,size,side)

						if side =="B":
							if symbol not in nq_long and price>1:
								print(time_,symbol,side,pair,size)
								nq_long.append(symbol)
						elif side =="S":
							if symbol not in nq_short and price>1:
								nq_short.append(symbol)
								print(time_,symbol,side,pair,size)

						name = "IMB_MOO_925L"
						cmdstr =  "https://tnv.ngrok.io/Basket="+name+",Order=*"
						added = False


						money = 1000
						if len(nq_long)>0:
							for symbol in nq_long:
								if symbol not in already_sent_long:
									share = int(money/price)

									if share>1000:
										share = 1000

									if share<10:
										share =10

									cmdstr += symbol+":"+str(share)+","
									already_sent_long.append(symbol)
									added = True 

						if added:
							cmdstr= cmdstr[:-1]
							cmdstr+="*"
							print(cmdstr)
							requests.get(cmdstr)
							moo_release= True 

						name = "IMB_MOO_925S"
						cmdstr =  "https://tnv.ngrok.io/Basket="+name+",Order=*"
						added = False
						if len(nq_short)>0:
							for symbol in nq_short:
								if symbol not in already_sent_short:

									share = int(money/price)
									if share>1000:
										share = 1000
									if share<10:
										share = 10 
										
									cmdstr += symbol+":"+str(-1*share)+","
									already_sent_short.append(symbol)
									added = True 

						if added:
							cmdstr= cmdstr[:-1]
							cmdstr+="*"
							print(cmdstr)
							requests.get(cmdstr)
							moo_release= True 


				if time_>57390 and time_< 57500 and symbol[-2:]=="NY":#57390
					moo_release = False
					if pair>1000000 or size >800000:

						print(symbol,pair,size,side)

						if side =="B":
							if symbol not in nyse_short:
								nyse_short.append(symbol)
						elif side =="S":
							if symbol not in nyse_long:
								nyse_long.append(symbol)

					if time_ - prev_time >10:

						prev_time = time_
						coefficient+=10

						if coefficient>=100:
							coefficient = 100

						name = "NYCLOSE1"
						cmdstr =  "https://tnv.ngrok.io/Basket="+name+",Order=*"

						for symbol in nyse_long:
							cmdstr += symbol+":"+str(coefficient)+","

						cmdstr= cmdstr[:-1]
						cmdstr+="*"
						print(cmdstr)
						requests.get(cmdstr)
						# send orders. 

						name = "NYCLOSE2"
						cmdstr =  "https://tnv.ngrok.io/Basket="+name+",Order=*"

						for symbol in nyse_short:
							cmdstr += symbol+":"+str(coefficient*-1)+","

						cmdstr= cmdstr[:-1]
						cmdstr+="*"
						requests.get(cmdstr)
						print(cmdstr)
			except Exception as e:
				print(e)
			writer.writerow(d)
			if count%1000==0:
				print("writer:",count)

	print("writer finished")

def running_mode(send_pipe):

	try:
		print("running mode starts ")

		postbody =  "http://localhost:8080/SetOutput?symbol=*.NQ,*.AM,*.NY&feedtype=IMBALANCE&output=4135&status=on"
		r= requests.post(postbody)


		while r.status_code !=200:
			r= requests.post(postbody)
			print("request failed")
			break
			
		print("request successful")
		UDP_IP = "localhost"
		UDP_PORT = 4135

		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind((UDP_IP, UDP_PORT))

		count = 0

		while True:
			data, addr = sock.recvfrom(1024)
			row = str(data)
			#writer.writerow([row])

			## TOSS IT ONTO THE THREAD VIA PIPE>
			#process_data(row,writer,all_symbols)
			send_pipe.send(row)

			count+=1

			if count%1000==0:
				print("reader:",count)

	except Exception as e:
		print(e)


# from datetime import datetime
import datetime
import requests 
from datetime import date, timedelta,datetime

import json 

def get_open_price(symbols):
  nyc_datetime = datetime.now()
  ts =  nyc_datetime.hour*60+nyc_datetime.minute

  r = "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?include_otc=false&apiKey=ezY3uX1jsxve3yZIbw2IjbNi5X7uhp1H"
  r = requests.get(r)
  d = json.loads(r.text)

  gap = {}

  ### NEED TO MAKE SURE THESE VAL ARE NON 0 .
  for i in d['tickers']:
    if i['ticker'] in symbols:
      gap[i['ticker']] = i['todaysChangePerc']

  return gap

def earning_tracking():
  asset = "QQQ"
  day = 1
  postbody ="https://financialmodelingprep.com/api/v3/earning_calendar?from="+(date.today()-timedelta(days = day)).strftime("%Y-%m-%d")+ "&to="+ date.today().strftime("%Y-%m-%d")+"&apikey=a901e6d3dd9c97c657d40a2701374d2a"
  r= requests.get(postbody)
  earning = json.loads(r.text)

  etf = []
  postbody = "https://financialmodelingprep.com/api/v3/etf-holder/"+asset+"?apikey=a901e6d3dd9c97c657d40a2701374d2a"

  r= requests.get(postbody)
  d = json.loads(r.text)

  for i in d:
    etf.append(i['asset'])

  tracking = []
  for i in earning:
    if i['symbol'] in etf:
      tracking.append(i['symbol'])

  longs = []
  shorts = []
  total = []
  for symbol,gap in get_open_price(tracking).items():
    if gap>2:
      longs.append(symbol)
    if gap<-2:
      shorts.append(symbol)
      #print(symbol,round(gap,2))

  total = longs + shorts

  return total 
if __name__ == '__main__':


	#print(earning_tracking())
	multiprocessing.freeze_support()
	processor()




	# send_pipe, receive_pipe = multiprocessing.Pipe()

	# process_ppro2 = multiprocessing.Process(target=writer, args=(receive_pipe,),daemon=True)
	# process_ppro2.daemon=True
	# process_ppro2.start()

	# running_mode(send_pipe)

