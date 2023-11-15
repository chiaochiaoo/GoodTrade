from datetime import datetime

import linecache
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
import matplotlib.pyplot as plt
import traceback
import socket
import time
import json

def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data



def PrintException(folder,file,info,additional="ERROR"):
	# exc_type, exc_obj, tb = sys.exc_info()
	# f = tb.tb_frame
	# lineno = tb.tb_lineno
	# filename = f.f_code.co_filename
	# linecache.checkcache(filename)
	# line = linecache.getline(filename, lineno, f.f_globals)
	# log_print (info+'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
	exc_type, exc_obj, exc_tb = sys.exc_info()
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	log_print(folder,file,additional,info,exc_type, fname, exc_tb.tb_lineno,traceback.format_exc())

def log_print(folder,file,*args):
	"""My custom log_print() function."""
	# Adding new arguments to the log_print function signature 
	# is probably a bad idea.
	# Instead consider testing if custom argument keywords
	# are present in kwargs

	#send this via a pipe to another processor 

	try:
		listToStr = ' '.join([str(elem) for elem in args])

		if len(listToStr)>5:
			f = open(folder+"/"+file+"_"+datetime.now().strftime("%m-%d")+".txt", "a+")
			time_ = datetime.now().strftime("%H:%M:%S : ")
			f.write("\n"+time_+listToStr)
			f.close()
			print(time_,*args)
	except Exception as e:
		print(*args,e,"failed to write")


def logging(pipe):

	f = open(datetime.now().strftime("%d/%m")+".txt", "w")
	while True:
		string = pipe.recv()
		time_ = datetime.now().strftime("%H:%M:%S")
		log_print(string)
		f.write(time_+" :"+string)
	f.close()

#COLOR CODING TEST
# if __name__ == '__main__':

# 	import tkinter as tk
# 	root = tk.Tk() 

# 	for i in range(0,13):

# 		tk.Label(text="",background=hexcolor_red(i/10),width=10).grid(column=i,row=1)

# 	root.mainloop()


