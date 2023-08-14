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

		self.registered = True 
		self.termination = True 

		c = 0
		k = 0 

		self.registered = False 

		self.symbols = ['SPY.AM','QQQ.NQ','IWM.AM']
		

		register_ts = 0
		while True:

			try:
				now = datetime.now()
				ts = now.hour*60 + now.minute

				if (ts >=400 and ts<=1000) and self.registered==False:

					force_close_port(6666)

					#### L1s .
					#postbody = "http://localhost:8080/SetOutput?region=1&feedtype=IMBALANCE&output=6666&status=on"
					postbody1 = "http://localhost:8080/SetOutput?symbol=QQQ.NQ&feedtype=L1&output=6666&status=on"
					postbody2 = "http://localhost:8080/SetOutput?symbol=QQQ.NQ&feedtype=L2&output=6666&status=off"
					postbody3 = "http://localhost:8080/SetOutput?symbol=QQQ.NQ&feedtype=TOS&output=6666&status=on"

					ps = [postbody1,postbody2,postbody3]
					####
					for postbody in ps:
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
					#postbody = "http://localhost:8080/SetOutput?region=1&feedtype=IMBALANCE&output=6666&status=on"
					postbody = "http://localhost:8080/SetOutput?symbol=QQQ.NQ&feedtype=L1&output=6666&status=on"
					try:
						r= requests.post(postbody)
					except Exception as e:
						print(e)

				if ts>1000:


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
				k+=1

			except Exception as e :
				print(e)

	# def open_file(self):

	# 	try:
	# 		self.f = open("l1/"+datetime.now().strftime("%m-%d")+".csv", "x")
	# 	except:
	# 		self.f = open("l1/"+datetime.now().strftime("%m-%d")+".csv", "w")

	# 	self.f.close()





def force_close_port(port, process_name=None):
	"""Terminate a process that is bound to a port.
	
	The process name can be set (eg. python), which will
	ignore any other process that doesn't start with it.
	"""
	print("killing 6666",port)
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

	l1  = ["MarketTime=","Symbol=",
	"BidPrice=","BidSize=","AskPrice=","AskSize="]
	l1_header = [i[:-1] for i in l1]


	# l2  = ["MarketTime=","Symbol=",
	# "Side=","Price=","Volume="]
	# l2_header = [i[:-1] for i in lst]

	tos  = ["MarketTime=","Symbol=",
	"Price=","Size="]
	tos_header = [i[:-1] for i in tos]


	count = 0

	now = datetime.now()
	ts = now.hour*60 + now.minute

	l1_file = "l1/"+datetime.now().strftime("%y-%m-%d")+".csv"
	tos_file = "tos/"+datetime.now().strftime("%y-%m-%d")+".csv"
	#l2_file = "l2/"+datetime.now().strftime("%y-%m-%d")+".csv"

	print("Writer functional",file)

	### if morning 

	### if night 


	prev_time = 0

	#my_file = open("hello.txt")
	l1 = open(l1_file, 'a+',newline='') 
	#l2 =open(l2_file, 'a+',newline='') 
	tos =open(tos_file, 'a+',newline='') 

	l1_writer = csv.writer(l1)
	#l2_writer = csv.writer(l2)
	tos_writer = csv.writer(tos)

	l1_writer.writerow(l1_header)
	tos_writer.writerow(tos_header)


	while True:
		r = receive_pipe.recv()
		count+=1
		if r =="good":
			break

		d=[]

		type_ = find_between(r,"Message=",",")
		

		if type_ =="L1":

		for i in lst:
			if i in ["BidPrice=","BidSize=","AskPrice=","AskSize="]:
				try:
					d.append(float(find_between(r,i,",")))
				except Exception as e:
					print(len(i),e)
			elif i in ["LocalTime=","MarketTime="]:
			  d.append(timestamp_seconds(find_between(r, i, ",")))
			else:
			  d.append(find_between(r,i,","))

			l1_writer.writerow(d)
		elif type_ =="TOS":


			for i in lst:
				if i in ["Price"]:
					try:
						d.append(float(find_between(r,i,",")))
					except Exception as e:
						print(len(i),e)
				elif i in ["LocalTime=","MarketTime="]:
				  d.append(timestamp_seconds(find_between(r, i, ",")))
				else:
				  d.append(find_between(r,i,","))


			tos_writer.writerow(d)
		if count%1000==0:
			print("writer:",count)

	print("writer finished")

def running_mode(send_pipe):

	try:
		print("running mode starts ")

		postbody = "http://localhost:8080/SetOutput?symbol=QQQ.NQ&feedtype=L1&output=6666&status=on" 
		#"http://localhost:8080/SetOutput?region=1&feedtype=IMBALANCE&output=6666&status=on"
		#
		r= requests.post(postbody)


		while r.status_code !=200:
			r= requests.post(postbody)
			print("request failed")
			break
			
		print("request successful")
		UDP_IP = "localhost"
		UDP_PORT = 6666

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

