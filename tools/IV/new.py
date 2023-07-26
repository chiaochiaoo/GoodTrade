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

					force_close_port(4135)
					postbody = "http://localhost:8080/SetOutput?region=1&feedtype=IMBALANCE&output=4135&status=on"

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
					postbody = "http://localhost:8080/SetOutput?region=1&feedtype=IMBALANCE&output=4135&status=on"

					try:
						r= requests.post(postbody)
					except Exception as e:
						print(e)

				if k>50 and self.termination==False:


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

	### if morning 

	### if night 

	coefficient = 1
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
				size = float(find_between(r,"Volume=",","))
				time_ = timestamp_seconds(find_between(r, "MarketTime=", ","))
				side = find_between(r,"Side=",",")

				if time_>57000 and symbol[-2:]=="NY":#57390

					if pair>1000000 or size >800000:

						print(symbol,pair,size,side)

						if side =="B":
							if symbol not in nyse_short:
								nyse_short.append(symbol)
						elif side =="S":
							if symbol not in nyse_long:
								nyse_long.append(symbol)

					if int(time_)%20 ==0:
						coefficient+=1 

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
if __name__ == '__main__':

	multiprocessing.freeze_support()
	processor()




	# send_pipe, receive_pipe = multiprocessing.Pipe()

	# process_ppro2 = multiprocessing.Process(target=writer, args=(receive_pipe,),daemon=True)
	# process_ppro2.daemon=True
	# process_ppro2.start()

	# running_mode(send_pipe)

