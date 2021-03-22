import numpy as np
import pandas as pd
# import sys
# import os
import time

def get_min(time_str):
	"""Get Seconds from time."""
	h, m= time_str.split(':')
	#print(h,m)
	return int(h) * 60 + int(m)

def ts_to_str(timestamp):

	h= int(timestamp//60)
	m= int(timestamp%60)


	#chekc if they are 1 unit.

	if h//10 == 0:
		h = "0"+str(h)
	else:
		h = str(h)

	if m//10 == 0:
		m = "0"+str(m)
	else:
		m = str(m)


	return(h+":"+m)

def IQR(x):

	if len(x)> 5:
		q75, q25 = np.percentile(x, [75 ,25])
		iqr = (q75 - q25)*1.5
		### only take the good one.
		y = []
		for i in x:
			if (i <= q75 + iqr) and (i >= q25 - iqr):
				y.append(i)

		x = y[:]
		#print(q75,q25,iqr)

	return x

def pre_processor(s):
	Timestamps = []
	Volume5 = []
	Volume30 =[]
	VolumeAcc = []
	Range = []
	Range5 = []
	Range30 = []
	Roc=[]
	Roc5=[]
	Roc30=[]



	#1 st iteration: Append timestamp, range.

	for i in range(len(s)):
		Timestamps.append(get_min(s["time"][i]))
		R = s["high"][i]-s["low"][i]
	#     c = 1
	#     if s["close"][i]<s["open"][i]:
	#         c = -1
	#     R = R*c
		roc = s["close"][i]-s["open"][i]
		Range.append(R)
		Roc.append(roc)

	s.insert(2,"timestamp", Timestamps, True)

	#2 nditeration:  volume 5, volume30, volumeACC
	acc = 0
	for i in range(len(s)):
		#if time is 04:00, reset acc to 0
		if s["timestamp"][i]==240:
			acc = 0
		acc += s["volume"][i]

		#last 5.

		last_5 = s["timestamp"][i]-5
		j = i
		vol_5 = 0
		highs =[]
		lows = []

		Close =s["close"][i]

		#iterate backward.
		while j>= 0 and s["timestamp"][j]>last_5:
			vol_5 += s["volume"][j]
			highs.append(s["high"][j])
			lows.append(s["low"][j])
			j-=1
			if j<0:
				j = 0
				break
			else:
				if s["timestamp"][j+1] - s["timestamp"][j] <=0:
					break

		if j<0: j = 0
		Open = s["open"][j]

		roc5 = Close-Open
		R5 = max(highs) - min(lows)



		last_30 = s["timestamp"][i]-30
		j = i
		vol_30 = 0
		highs =[]
		lows = []

		Close =s["close"][i]

		#iterate backward.
		while  j>= 0 and s["timestamp"][j]>last_30:
			vol_30 += s["volume"][j]
			highs.append(s["high"][j])
			lows.append(s["low"][j])
			j-=1
			if j<0:
				j = 0
				break
			else:
				if s["timestamp"][j+1] - s["timestamp"][j] <=0:
					break


		Open = s["open"][j]

		roc30 = Close-Open
		R30 = max(highs) - min(lows)

		Roc5.append(roc5)
		Roc30.append(roc30)
		Range5.append(R5)
		Range30.append(R30)
		Volume5.append(vol_5)
		Volume30.append(vol_30)
		VolumeAcc.append(acc)

	i = 7
	s.insert(i,"roc", Roc, True)
	s.insert(i+1,"roc5", Roc5, True)
	s.insert(i+2,"roc30", Roc30, True)
	s.insert(i+3,"range", Range, True)
	s.insert(i+4,"range5", Range5, True)
	s.insert(i+5,"range30", Range30, True)
	s.insert(i+7,"volume5", Volume5, True)
	s.insert(i+8,"volume30", Volume30, True)
	s.insert(i+9,"volumeacc", VolumeAcc, True)


def find_between(data, first, last):
    try:
        start = data.index(first) + len(first)
        end = data.index(last, start)
        return data[start:end]
    except ValueError:
        return data



# This is for. Range, Volume . Distribution. etc. 
def stat_extractor(argv):
	if len(argv)<1:
		print("Stats Extractor: Need to pass in one or multiple file")
		return []
		#os._exit(1)

	else:

		file_created = []
		for i in range(len(argv)):
			file  = argv[i]
			symbol = find_between(file,"/",".")
			start = time.time()
			S =pd.read_csv(file,names=["day","time","open","high","low","close","volume"])

			print("Stats Extractor: Processing", file[:-4]," containing minutes:",len(S))
			#process

			if(len(S)>1):
				pre_processor(S)

				p=S.groupby(['timestamp'])

				vol=p["volume"].apply(list)
				vol5=p["volume5"].apply(list)
				vol30=p["volume30"].apply(list)
				volacc=p["volumeacc"].apply(list)

				r=p["range"].apply(list)
				r5=p["range5"].apply(list)
				r30=p["range30"].apply(list)

				roc=p["roc"].apply(list)
				roc5=p["roc5"].apply(list)
				roc30=p["roc30"].apply(list)

				process_list = [vol,vol5,vol30,volacc,r,r5,r30,roc,roc5,roc30]

				names = ["v1","v5","v30","vacc","r","r5","r30","roc","roc5","roc30"]


				# STEP 1 : first construct the DataFrame with timestamp and time

				timestamps = list(p.groups.keys())

				times = [ts_to_str(i) for i in timestamps]
				d = pd.DataFrame(timestamps,columns=["timestamp"])

				d.insert(len(d.columns),"time", times, True)


				# STEP 2.  For each of the item in processing list. Add them to the dataframe in a similar fashion.

				for i in range(len(process_list)):

					mean = [] #Avg
					distribution = []
					stds = []

					for key,value in process_list[i].items():
						distribution.append(value[:])
						l = IQR(value)

						if (len(l)<1):
							print(l,key,value)
						mean_ = round(np.mean(l),3)
						std_= round(np.std(l),3)
						if i <4:
							mean_ = int(mean_)
							std_ = int(std_)
						mean.append(mean_)
						stds.append(std_)

					d.insert(len(d.columns),names[i]+"m",mean, True)
					d.insert(len(d.columns),names[i]+"s",stds, True)
					d.insert(len(d.columns),names[i]+"d",distribution, True)


				d.to_csv("data/"+symbol+"stat.csv")
				end = time.time()
				print("Stats Extractor:: Meta file CSV export successful, time taken:"+str(round(end-start,2))+" seconds");
				file_created.append(file[:-4]+"stat.csv")

			else:
				print("Failed to process file data/",symbol,".txt Please check.")

		return file_created


