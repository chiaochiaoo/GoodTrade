
import time
import pandas as pd 
import requests
import json
import datetime
from datetime import date
import os.path
import numpy as np
import pickle
import socket

try:
    from finviz.screener import Screener
except ImportError:
    pip.main(['install', 'finviz'])
    from finviz.screener import Screener


rel_v = "rel_volume"

open_high_range ="open_high_range"
open_high_val ="open_high_val"
open_high_std ="open_high_std"

open_low_range ="open_low_range"
open_low_val ="open_low_val"
open_low_std ="open_low_std"

high_low_range ="high_low_range"
high_low_val ="high_low_val"
high_low_std ="high_low_std"

first_5_range ="first_5_range"
first_5_val ="first_5_val"
first_5_std ="first_5_std"

first_5_vol_range ="first_5_vol_range"
first_5_vol_val ="first_5_vol_val"
first_5_vol_std ="first_5_vol_std"

normal_5_range ="normal_5_range"
normal_5_val ="normal_5_val"
normal_5_std ="normal_5_std"

normal_5_vol_range ="normal_5_vol_range"
normal_5_vol_val ="normal_5_vol_val"
normal_5_vol_std ="normal_5_vol_std"

prev_close_range ="prev_close_range"
prev_close_val ="prev_close_val"
prev_close_std ="prev_close_std"

symbol_data_ATR ="symbol_data_ATR"

expected_momentum = "expected_momentum"

def l(v):
	z=[]
	for i in v:
		z.append(chr(i))

	return (''.join(map(str, z)))

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

def database_handler(symbols):

	total = {}	

	for i in symbols:
		symbol =i.split(".")[0]
		today = date.today().strftime("%m%d")
		file = "data/"+symbol+"_"+today+".txt"
		fail=0
		if os.path.isfile(file):
			#print(symbol,"already exisit, sending copy instd.")
			with open(file) as json_file:
				data = json.load(json_file)
				total[i] = data
		else:
			success = False
			try:
				data = fetch_data(symbol)
				if data != [symbol]:
					total[i] = data
					success = True
			except Exception as e:
				fail +=1
				#print("fetching failure..retrying.",e,symbol)
				time.sleep(4)
				if fail >=15:
					break
			if success:
				#print(i,"download success")
				with open(file, 'w') as outfile:
					json.dump(data, outfile)
			else:
				pass
				#print(i,"download failed")

	return total


def timestamp(st):

	h,m = st.split(":")

	return int(h)*60+int(m)

def fetch_data(symbol):

	i = symbol

	v= [38, 117, 115, 101, 114, 61, 115, 97, 106, 97, 108, 105, 50, 54, 64, 104, 111, 116, 109, 97, 105, 108, 46, 99, 111, 109, 38, 112, 97, 115, 115, 119, 111, 114, 100, 61, 103, 117, 117, 112, 117, 52, 117, 112, 117]

	postbody = "http://api.kibot.com/?action=history&symbol="+symbol+"&interval=daily&period=45&regularsession=1" +l(v)
	r= request(postbody, symbol)

	if r=="":

		return [symbol]

	else:
		O,H,L,C,V =1,2,3,4,5

		range_=[] #data.symbol_data_openhigh_dis[i]
		openhigh_=[] #data.symbol_data_openlow_dis[i]
		openlow_=[] #data.symbol_data_range_dis[i]

		EM = []
		ATR = []
		previous_close = []

		#d = r.splitlines()[-14:]

		prev_close = 0

		for line in r.splitlines():
			lst=line.split(",")
			EM.append(max(float(lst[H])-float(lst[O]),float(lst[O])-float(lst[L])))

		for line in r.splitlines()[-14:]:
			lst=line.split(",")
			range_.append(float(lst[H])-float(lst[L]))

			oh = np.log(float(lst[H]))-np.log(float(lst[O]))
			ol = np.log(float(lst[O]))-np.log(float(lst[L]))
			if oh>ol:
				openhigh_.append(oh)
			else:
				openlow_.append(ol)
			###ATR

			if prev_close!=0:
				gap = round(float(lst[O])-prev_close,2)
				previous_close.append(gap)

				ra =  float(lst[H])-float(lst[L])
				o =  abs(float(lst[H])-prev_close)
				c =  abs(float(lst[L])-prev_close)
				tr = max(ra,o,c)
				ATR.append(tr)

			prev_close = float(lst[C])

		openhigh_ = np.array(openhigh_)*prev_close
		openlow_ = np.array(openlow_)*prev_close
		openhigh_range=str(round(min(openhigh_),3))+"-"+str(round(max(openhigh_),3))
		openlow_range=str(round(min(openlow_),3))+"-"+str(round(max(openlow_),3))
		range_range=str(round(min(range_),3))+"-"+str(round(max(range_),3))
		prev_close_range_= str(round(min(previous_close),3))+" - "+str(round(max(previous_close),3))

		openhigh_val=round(np.mean(openhigh_),3)
		openlow_val=round(np.mean(openlow_),3)
		range_val=round(np.mean(range_),3)
		prev_close_val_ = round(np.mean(np.abs(previous_close)),3)

		openhigh_std=round(np.std(openhigh_),3)
		openlow_std=round(np.std(openlow_),3)
		range_std=round(np.std(range_),3)
		prev_close_std_ = round(np.std(np.abs(previous_close)),3)

		ATR = np.mean(ATR)
		ATR = round(ATR,2)


		expected_m = round(EMA(EM,7)[-2],2)


		###ADD the first 5 here. seperate them later.

		postbody = "http://api.kibot.com/?action=history&symbol="+symbol+"&interval=5&period=14&regularsession=0" +l(v)
	
		r= request(postbody, symbol)

		tod = datetime.date.today().strftime("%m/%d/%Y")

		
		if r!="":
			a=[]#data.symbol_data_first5_dis[i]
			b=[]#data.symbol_data_first5_vol_dis[i]

			c=[]#data.symbol_data_normal5_dis[i]
			d=[]#data.symbol_data_normal5_vol_dis[i]

			stamps = np.array([570+i*5 for i in range(79)])
			df = pd.DataFrame(columns = stamps)

			if r[:3]=="402":
				print("Not authorize to",symbol)
				a=[0]#data.symbol_data_first5_dis[i]
				b=[0]#data.symbol_data_first5_vol_dis[i]

				c=[0]#data.symbol_data_normal5_dis[i]
				d=[0]#data.symbol_data_normal5_vol_dis[i]


			else:
				for line in r.splitlines():
					
					lst=line.split(",")
					v = int(lst[6])
					date = lst[0]

					if date!=tod:

						ts = timestamp(lst[1])

						if date not in df.index:
							#print(date)
							df.loc[date] = [0 for i in range(len(stamps))]

							accv = v
						else:
							accv +=v 

						if ts>= 570 and ts<=961:

							df.loc[date,ts] = accv

							r = round(float(lst[3])-float(lst[4]),3)
							
							if lst[1]=='09:30':
								a.append(r)
								b.append(v)
							c.append(r)
							d.append(v)



			rel_vol = df.mean().tolist()


			p = np.poly1d(np.polyfit(np.arange(79)*5, rel_vol, 10))
	
			new = [i for i in range(391)]
			rel_vol = [int(t) for t in p(new)]  


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

			#data_list[symbol] = symbol
			data_list = {}

			data_list[rel_v] = rel_vol
			data_list[open_high_range] = openhigh_range
			data_list[open_high_val] = openhigh_val
			data_list[open_high_std]= openhigh_std

			data_list[open_low_range] = openlow_range
			data_list[open_low_val] = openlow_val
			data_list[open_low_std] = openlow_std

			data_list[high_low_range] = range_range
			data_list[high_low_val] = range_val
			data_list[high_low_std] = range_std

			data_list[first_5_range] = first5_range
			data_list[first_5_val] = first5_val
			data_list[first_5_std] = first5_std

			data_list[first_5_vol_range] = first5_vol_range
			data_list[first_5_vol_val] = first5_vol_val
			data_list[first_5_vol_std] = first5_vol_std

			data_list[normal_5_range] = normal5_range
			data_list[normal_5_val] = normal5_val
			data_list[normal_5_std] = normal5_std

			data_list[normal_5_vol_range] = normal5_vol_range
			data_list[normal_5_vol_val] = normal5_vol_val
			data_list[normal_5_vol_std] = normal5_vol_std

			data_list[prev_close_range] = prev_close_range_
			data_list[prev_close_val] = prev_close_val_
			data_list[prev_close_std] = prev_close_std_

			data_list[symbol_data_ATR] =ATR

			data_list[expected_momentum] = expected_m

			return data_list


# def fetch_data(lst,conn):
# 	d = database_handler(lst)
# 	data = pickle.dumps(["Database Response",d])
# 	conn.sendall(data)

def EMA(lst,n):

    ema = [lst[0]]
    for i in range(1,len(lst)):
        current = lst[i]
        new = (current - ema[i-1])*(2/(n+1)) + ema[i-1]
        ema.append(new)


    # ema[1:] = ema[:-1]
    # print(np.round(lst,2))
    # print(np.round(ema,2))
    return ema


def grab_finviz_list(cond,market_,type_,cap):

	market = ''
	cond2 = ''
	signal = ''

	if market_ == 'Nasdaq':
		market = 'exch_nasd'

	elif market_ =='NYSE':
		market = 'exch_nyse'

	elif market_ =='AMEX':
		market = 'exch_amex'

	if type_ == 'Most Active':
		signal = 'ta_mostactive'

	elif type_ =='Top Gainner':
		signal = 'ta_topgainers'

	elif type_ =='New Highs':
		signal = 'ta_newhigh'

	elif type_ =='Unusual Volume':
		signal = 'ta_unusualvolume'


	if cap =='Any':
		cond2 = ''
	elif cap == 'Mega':
		cond2 = 'cap_mega'
	elif cap =='Large':
		cond2 = 'cap_large'
	elif cap == 'Mid':
		cond2 = 'cap_mid'
	elif cap =='Small':
		cond2 = 'cap_small'
	elif cap =='Large+':
		cond2 = 'cap_largeover'
	elif cap =='Mid+':
		cond2 = 'cap_midover'
	elif cap =='Small+':
		cond2 = 'cap_smallover'

	#self.markcap.set('Any') 

	filters = [market,cond,cond2]  # Shows companies in NASDAQ which are in the S&P500

	print(filters)

	try:
		stock_list = Screener(filters=filters, table='Performance', signal=signal)  # Get the performance table and sort it by price ascending
	except:
		return []

	print(len(stock_list))

	return list(stock_list)

	# pannel.add_labels(stock_list)

	# pannel.status.set("Download compelted")
	# pannel.downloading = False
	# print("Scanner download complete")


def database_service(response):
	print("DB service online")
	while True:

		#receive the calls. 
		data = response.recv()

		d = database_handler(data)
		try:
			#send back the data. 
			response.send(["Database Response",d])
		except Exception as e:
			print(e)

if __name__ == '__main__':


	# s = " Last updated 3/29/2021 20:18:00"
	# print(s[-9:-3])

	#print(database_handler(["OCGN"]))

	
	file = fetch_data("AMD")
	print(file)

	with open("test.txt", 'w') as outfile:
		json.dump(file, outfile)

# df['y'] = 0
# df.loc[df['x'] < -2, 'y'] = 1
# df.loc[df['x'] > 2, 'y'] = -1

#conditonal assignment 
#df.loc[df['price']>5,'status'] = "No"
#df["status"] = "1" if 
#print(df.sort_values(by=['rank'],ascending=False))


################################
########## SEND   ##############
################################

### UPDATE LOGIC #####
### Couple lists.
### 4 lists? 

	# col  = np.array([1,2,3,4])

	# k = ["q","w","e"]

	# d = pd.DataFrame(columns=col)

	
	# for i in k:
	# 	if i not in d:
	# 		d.loc[i] = [0,0,0,0]

	# 		for j in col:
	# 			k = np.where(col<=j)[0]
	# 			d.loc[i,col[k]]+=1

	# print(d)
	# print(d.mean().tolist())
