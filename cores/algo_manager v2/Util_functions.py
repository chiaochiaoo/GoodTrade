from datetime import datetime

import linecache
import sys

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
import matplotlib.pyplot as plt


def convert(df):
	
	algos = df.ALGO.unique()
	dates = df.DATE.unique()
	treal = pd.DataFrame(index=dates)
	trisk = pd.DataFrame(index=dates)
	for algo in algos:
		#print(algo)
		a = []
		b = []
		for date in dates:
			a.append(sum(df.loc[(df["DATE"]==date)&(df["ALGO"]==algo)]["REALIZED"].tolist()))
			b.append(sum(df.loc[(df["DATE"]==date)&(df["ALGO"]==algo)]["RISK"].tolist()))
		treal[algo] = a#r.loc[r.ALGO==algo].groupby(['DATE']).sum()["REALIZED"].tolist()
		trisk[algo] = b
	return treal,trisk


def graphweekly():


	now = datetime.now()
	monday = now - timedelta(days = now.weekday())
	file = monday.strftime("%Y_%m_%d")+".csv"

	r = pd.read_csv("../../algo_records/"+file)



	algos = r.ALGO.unique()


	fig, axs = plt.subplots(3,2,figsize=(20,15))
	#fig.suptitle('Vertically stacked subplots')

	r.groupby(['DATE']).sum().plot(ax=axs[0,0],kind='bar')

	axs[0,0].axhline(0,linestyle="--")
	axs[0,0].xaxis.set_tick_params(rotation=1)      
	axs[0,0].yaxis.set_major_formatter(ticker.FormatStrFormatter('$%.f'))
	axs[0,0].set_title("Total by date")

	tr,trk = convert(r)

	tr.plot(ax=axs[1,0],kind='bar')
	axs[1,0].axhline(0,linestyle="--")
	axs[1,0].xaxis.set_tick_params(rotation=1)      
	axs[1,0].yaxis.set_major_formatter(ticker.FormatStrFormatter('$%.f'))
	axs[1,0].set_title("Total Realized by algo by date")


	trk.plot(ax=axs[2,0],kind='bar')
	axs[2,0].axhline(0,linestyle="--")
	axs[2,0].xaxis.set_tick_params(rotation=1)      
	axs[2,0].yaxis.set_major_formatter(ticker.FormatStrFormatter('$%.f'))
	axs[2,0].set_title("Total Risk by algo by date")


	r.groupby(['ALGO'])["RISK"].sum().plot(ax=axs[0,1],kind='bar')
	axs[0,1].axhline(0,linestyle="--")
	axs[0,1].xaxis.set_tick_params(rotation=1)      
	axs[0,1].yaxis.set_major_formatter(ticker.FormatStrFormatter('$%.f'))
	axs[0,1].set_title("Total Risk by Algo")

	r.groupby(['ALGO'])["REALIZED"].sum().plot(ax=axs[1,1],kind='bar')
	axs[1,1].axhline(0,linestyle="--")
	axs[1,1].xaxis.set_tick_params(rotation=1)      
	axs[1,1].yaxis.set_major_formatter(ticker.FormatStrFormatter('$%.f'))
	axs[1,1].set_title("Total Realized by Algo")

	r.groupby(['SYMBOL'])["REALIZED"].sum().sort_values(ascending=False)[:10].plot(ax=axs[2,1],kind='bar')
	axs[2,1].axhline(0,linestyle="--")
	axs[2,1].xaxis.set_tick_params(rotation=1)      
	axs[2,1].yaxis.set_major_formatter(ticker.FormatStrFormatter('$%.f'))
	axs[2,1].set_title("Total Realized by Symbol")

	plt.tight_layout()
	plt.show()
	
def PrintException(info):
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    log_print (info+'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def log_print(*args):
	"""My custom log_print() function."""
	# Adding new arguments to the log_print function signature 
	# is probably a bad idea.
	# Instead consider testing if custom argument keywords
	# are present in kwargs

	#send this via a pipe to another processor 

	try:
		listToStr = ' '.join([str(elem) for elem in args])

		if len(listToStr)>5:
			f = open("../../algo_logs/"+datetime.now().strftime("%m-%d")+".txt", "a+")
			time_ = datetime.now().strftime("%H:%M:%S : ")
			f.write("\n"+time_+listToStr)
			f.close()
			print(time_,*args)
	except Exception as e:
		print(*args,e,"failed to write")



def hexcolor_green_to_red(level):

	if level>0:
		code = int(510*(level))
		#print(code,"_")
		if code >255:
			first_part = code-255
			return "#FF"+hex_to_string(255-first_part)+"00"
		else:
			return "#FF"+"FF"+hex_to_string(255-code)

	else:
		code = int(255*(abs(level)))
		first_part = 255-code

		return "#"+hex_to_string(first_part)+"FF"+hex_to_string(first_part)

def timestamp_seconds(s):

	p = s.split(":")
	try:
		x = int(p[0])*3600+int(p[1])*60+int(p[2])
		return x
	except Exception as e:
		print("Timestamp conversion error:",e)
		return 0

def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data

def hex_to_string(int):
	a = hex(int)[-2:]
	a = a.replace("x","0")

	return a

#1-5 is good 
def hexcolor_red(level):
	code = int(510*(level))
	if code >255:
		first_part = code-255
		return "#FF"+hex_to_string(255-first_part)+"00"
	else:
		return "#FF"+"FF"+hex_to_string(255-code)

#COLOR CODING TEST
# if __name__ == '__main__':

# 	import tkinter as tk
# 	root = tk.Tk() 

# 	for i in range(0,13):

# 		tk.Label(text="",background=hexcolor_red(i/10),width=10).grid(column=i,row=1)

# 	root.mainloop()