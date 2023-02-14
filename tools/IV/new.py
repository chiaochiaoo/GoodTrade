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
		directory = os.fsencode("db")

		for file in os.listdir(directory):

			filename = os.fsdecode(file)

			# red it. gets the symbols. 

			symbol = filename.upper()[:-4]

			a=pd.read_csv("./db/"+filename)

			self.all_symbols.extend(a['Symbol'].tolist())


		self.all_symbols = list(set(self.all_symbols))



			# for index, row in a.iterrows():
			# #iterate through, add the 
			# 	print(row["Symbol"])
				# if str(type(row["Symbol"])) == "<class 'str'>":
				# 	if len(row["Symbol"])<10:
				# 		if row["Symbol"] not in d:
				# 			print(row["Symbol"])


		self.registered = False 
		self.processing = False 
		self.termination = False 

		c = 0
		while True:

			now = datetime.now()
			ts = now.hour*60 + now.minute

			if (ts >= 930 and ts<=940) and self.registered==False:

				print("registering",ts)
				force_close_port(4135)
				postbody = "http://localhost:8080/SetOutput?region=1&feedtype=IMBALANCE&output=4135&status=on"
				try:
					r= requests.post(postbody)
				except Exception as e:
					print(e)
				
				self.processing = False  
				self.registered = True 

			if ts >= 945 and self.processing == False:

				print("activating.....data collection")
				self.open_file()


				send_pipe, receive_pipe = multiprocessing.Pipe()

				process_ppro = multiprocessing.Process(target=running_mode, args=(send_pipe,),daemon=True)
				process_ppro.daemon=True
				process_ppro.start()

				process_ppro2 = multiprocessing.Process(target=writer, args=(receive_pipe,),daemon=True)
				process_ppro2.daemon=True
				process_ppro2.start()
				# open a multile processing 

				#print("saving",ts)

				self.registered = False 
				self.processing = True 
				self.termination = False 

			if ts>= 965 and self.termination == False:

				print("terminating....")

				send_pipe.send("good")
				time.sleep(5)
				process_ppro.terminate()
				process_ppro.join()
				process_ppro2.terminate()
				process_ppro2.join()				
				self.termination = True


			print("current ts:",ts,	self.registered ,self.processing,self.termination)

			time.sleep(60)

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


def process_data(row,writer,all_symbols):

				
	Symbol = find_between(row, "Symbol=", ",")
	symbol = Symbol[:-3]					

	### ONLY PROCEED IF IT IS IN THE SYMBOL LIST ###57000
	if symbol in all_symbols:
		
		writer.writerow([row])


		# market = Symbol[-2:]
		# source = find_between(row, "Source=", ",")
		# time_ = find_between(row, "MarketTime=", ",")[:-4]
		# ts=timestamp_seconds(time_)

		# cur_price = find_between(row, "Price=", ",")
		# auc_price = find_between(row, "AuctionPrice=", ",")
		# cont_price = find_between(row, "ContinuousPrice=", ",")
		# procced = False

		# if market =="NQ" and source =="NADQ"and ts>=50400: 
		# 	procced = True

		# elif  market =="NY" and source =="NYSE" and ts>=50400: 
		# 	procced = True

		# elif market =="AM" and ts>=50400:
		# 	proceed = True

		# if procced:
			
		# 	side = find_between(row, "Side=", ",")
		# 	volume =  int(find_between(row, "Volume=", ","))

		# 	data = self.data[symbol]

		# 	writer.writerow([row])


def writer(receive_pipe):
	print("Writer functional")
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
	with open("saves/"+datetime.now().strftime("%m-%d")+".csv", 'w',newline='') as csvfile2:
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


			writer.writerow(d)
			if count%1000==0:
				print("writer:",count)

	print("writer finished")

def running_mode(send_pipe):

	print("running mode starts ")

	postbody = "http://localhost:8080/SetOutput?region=1&feedtype=IMBALANCE&output=4135&status=on"
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


	with open("saves/"+datetime.now().strftime("%m-%d")+"_original.csv", 'w',newline='') as csvfile2:
		writer = csv.writer(csvfile2)
		while True:


			# #### TEST MODE ####
			# c= 0 
			# with open('test.csv', 'r', encoding='UTF8') as f:
			# 	spamreader = csv.reader(f, delimiter=' ', quotechar='|')
			# 	for row in spamreader:
			# 		r = "".join(row)
			# 		send_pipe.send(r)
			# 		writer.writerow([r])
			# 		c+=1
			# 		#print(c)
			# 		if c%1000==0:
			# 			print(c)
			# 	send_pipe.send("good")
				
			# print("all_finished")
			
			# time.sleep(10)
			# os._exit(1)
			# #######################

			data, addr = sock.recvfrom(1024)
			row = str(data)
			writer.writerow([row])

			## TOSS IT ONTO THE THREAD VIA PIPE>
			#process_data(row,writer,all_symbols)
			send_pipe.send(row)

			count+=1

			if count%1000==0:
				print("reader:",count)

if __name__ == '__main__':

	multiprocessing.freeze_support()
	processor()


	# send_pipe, receive_pipe = multiprocessing.Pipe()

	# process_ppro2 = multiprocessing.Process(target=writer, args=(receive_pipe,),daemon=True)
	# process_ppro2.daemon=True
	# process_ppro2.start()

	# running_mode(send_pipe)

	# df = pd.read_csv("saves/02-14.csv")
	# print(len(df))
	# df = pd.read_csv("saves/02-14_original.csv")
	# print(len(df))