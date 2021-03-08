import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
import os
import time
import threading
import sys

from alerts import *
from pannel import *
from Symbol_data_manager import *

from scanner import *
from scanner_process_manager import *
from database_process_manager import *
from tkinter import messagebox
from ppro_process_manager import *
#from cores.algo_manager_comms import *


class viewer:

	def __init__(self,root,scanner_process,database_process,ppro_process,algo_comm,authen_comm):

		self.data = Symbol_data_manager()

		self.db = database_process
		self.db.set_symbols_manager(self.data)

		self.ppro = ppro_process
		self.ppro.set_symbols_manager(self.data)

		self.data.set_database_manager(self.db)
		self.data.set_ppro_manager(self.ppro)

		self.listening = ttk.LabelFrame(root,text="Listener") 
		self.listening.place(x=600,rely=0.05,relheight=1,width=1300)

		self.tabControl = ttk.Notebook(self.listening)
		self.tab1 = tk.Canvas(self.tabControl)
		self.tab2 = tk.Canvas(self.tabControl)
		self.tab3 = tk.Canvas(self.tabControl)
		self.tab4 = tk.Canvas(self.tabControl)
		self.tab5 = tk.Canvas(self.tabControl)
		self.tab6 = tk.Canvas(self.tabControl)
		self.tab7 = tk.Canvas(self.tabControl)
		self.tab8 = tk.Canvas(self.tabControl)
		self.tab9 = tk.Canvas(self.tabControl)
		self.tab10 = tk.Canvas(self.tabControl)
		self.tab11 = tk.Canvas(self.tabControl)


		self.tabControl.add(self.tab1, text ='Tickers Manager') 
		self.tabControl.add(self.tab8, text ='All alerts') 
		self.tabControl.add(self.tab11, text ='Alerts map') 
		self.tabControl.add(self.tab10, text ='Prev Close') 
		self.tabControl.add(self.tab5, text ='High-Low')
		self.tabControl.add(self.tab6, text ='Open-High')
		self.tabControl.add(self.tab7, text ='Open-Low')
		self.tabControl.add(self.tab2, text ='Extreme Range') 
		self.tabControl.add(self.tab3, text ='Extreme Volume') 
		self.tabControl.add(self.tab4, text ='First five minutes')
		self.tabControl.add(self.tab9, text ='Premarket Breakout')
		self.tabControl.pack(expand = 1, fill ="both") 

		#self.ticker_management_init(self.tab1)
		self.all_alerts = all_alerts(self.tab8)

		self.open_high_pannel = openhigh(self.tab6,self.data,self.all_alerts)

		self.high_low_pannel = highlow(self.tab5,self.data,self.all_alerts)
		self.open_low_pannel = openlow(self.tab7,self.data,self.all_alerts)

		self.first_5 = firstfive(self.tab4,self.data,self.all_alerts)
		self.er = extremrange(self.tab2,self.data,self.all_alerts)
		self.ev = extremevolume(self.tab3,self.data,self.all_alerts)

		self.pv = prevclose(self.tab10,self.data,self.all_alerts)

		self.br = breakout(self.tab9,self.data)#algo_comm #self.all_alerts,algo_comm
		self.am = alert_map(self.tab11,self.data)
		#alerts  =[self.open_high_pannel]
		alerts = [self.high_low_pannel,self.open_high_pannel,self.open_low_pannel,self.first_5,self.er,self.ev,self.br,self.pv,self.am]

		self.tm = ticker_manager(self.tab1,self.data,alerts,authen_comm)
		

		self.scanner_pannel = scanner(root,self.tm,scanner_process,self.data)

		scanner_process.set_pannel(self.scanner_pannel)



class ticker_manager(pannel):
	def __init__(self,frame,data,alerts,authen_comm):
		super().__init__(frame)

		self.authen = authen_comm

		self.alerts = alerts

		self.Entry1 = tk.Entry(frame)
		self.Entry1.place(x=5, y=5, height=30, width=80, bordermode='ignore')
		self.Entry1.configure(background="white")
		self.Entry1.configure(cursor="fleur")
		self.Entry1.configure(disabledforeground="#a3a3a3")
		self.Entry1.configure(font="TkFixedFont")
		self.Entry1.configure(foreground="#000000")
		self.Entry1.configure(insertbackground="black")

		self.symbol = tk.Button(frame,command= lambda: self.add_symbol_reg_list(self.Entry1.get().upper())) #,command=self.loadsymbol
		self.symbol.place(x=105, y=5, height=30, width=80, bordermode='ignore')
		self.symbol.configure(activebackground="#ececec")
		self.symbol.configure(activeforeground="#000000")
		self.symbol.configure(background="#d9d9d9")
		self.symbol.configure(disabledforeground="#a3a3a3")
		self.symbol.configure(foreground="#000000")
		self.symbol.configure(highlightbackground="#d9d9d9")
		self.symbol.configure(highlightcolor="black")
		self.symbol.configure(pady="0")
		self.symbol.configure(text='''Add Symbol''')

		#"Ppro Status: "+"Connecting"
		self.ppro_status = ttk.Label(frame, textvariable=data.ppro_status)
		self.ppro_status.place(x = 200, y =12)
		#data.ppro_status.set("Hello")

		self.trader_stats = ttk.Label(frame, text="User Authentication:")
		self.trader_stats.place(x = 400, y =12)

		self.permission_stats = ttk.Label(frame, text="Permission Status:")
		self.permission_stats.place(x = 600, y =12)

		self.ticker_stats = ttk.Label(frame, text="Current Registered Tickers: "+str(self.ticker_count))
		#self.ticker_stats.place(x = 800, y =12)

		#############Registration Window ####################

		self.data = data


		self.width = [8,10,12,10,24,10,10]
		self.labels = ["Ticker","Status","Last update","Price","Last Alert","Last Alert time","Remove"]

		#init the labels. 
		self.labels_creator(self.frame)

		self.init_reg_list()

		data = threading.Thread(target=self.recv, daemon=True)
		data.start()

		
	def init_reg_list(self):

		ticks = self.data.get_list()

		for i in range(len(ticks)):
			self.add_symbol_label(ticks[i])

		self.tickers = self.data.get_list()
		self.rebind(self.canvas,self.frame)

	def delete_symbol_reg_list(self,symbol):

		if symbol in self.tickers:

			#1. remove it from the list.
			self.data.delete(symbol)

			for i in self.tickers_tracers[symbol]:
				#print("viewer removing",i[0].get(),i[1])
				i[0].trace_vdelete("w",i[1])


			for i in self.tickers_labels[symbol]:
				i.destroy()

			self.tickers_labels.pop(symbol,None)

			self.ticker_count -= 1
			self.ticker_stats["text"] = "Current Registered Tickers: "+str(self.ticker_count)

			self.rebind(self.canvas,self.frame)

		for i in self.alerts:
			i.delete_symbol(symbol)

		return True


	def add_symbol_label(self,symbol):

		# data = threading.Thread(target=self.data.data_request(symbol), daemon=True)
		# data.start()

		i = symbol
		l = self.label_count

		info = [symbol,\
				self.data.symbol_status[symbol],\
				self.data.symbol_update_time[symbol],\
				self.data.symbol_price[symbol],\
				self.data.symbol_last_alert[symbol],\
				self.data.symbol_last_alert_time[symbol],
				""]

		self.tickers_labels[i]=[]

		self.tickers_tracers[i] = []
		#add in tickers.
		for j in range(len(info)):
			if j == 0:
				self.tickers_labels[i].append(tk.Label(self.frame ,text=info[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

			elif j == 1:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=info[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
				m=info[j].trace('w', lambda *_, text=info[j],label=self.tickers_labels[i][j]: self.status_change_color(text,label))
				self.tickers_tracers[i].append((info[j],m))
			elif j != (len(info)-1):
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=info[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
			else:
				self.tickers_labels[i].append(tk.Button(self.frame ,text=info[j],width=self.width[j],command = lambda s=symbol: self.delete_symbol_reg_list(s)))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

		self.ticker_count +=1
		self.label_count +=1

		self.ticker_stats["text"] = "Current Registered Tickers: "+str(self.ticker_count)

		self.data.change_status(symbol, "Connecting")
		self.rebind(self.canvas,self.frame)

		for i in self.alerts:
			i.add_symbol(symbol)
		#print(self.ticker_index)

		#print(self.tickers)

	def add_symbol_reg_list(self,symbol):


		try:
			if symbol not in self.tickers:

				self.data.add(symbol)
				self.add_symbol_label(symbol)


		except Exception as e:
			print("Error",e)

	def recv(self):
		k=self.authen.recv()
		name=k[0]
		per=k[1]
		sta=k[2]
		self.trader_stats["text"]= "User Authentication: "+name
		self.permission_stats["text"]="Permission Status:"+per
#a seperate thread on its own. 

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        "Destroyed"


def authentication(pipe):
    k=""

    HOST = '10.29.10.135'  # Standard loopback interface address (localhost)
    PORT = 65400        # Port to listen on (non-privileged ports are > 1023)


    print("Trying to connect to the Authentication server")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = False

    while not connected:
        try:
            s.connect((HOST, PORT))
            connected = True
        except:
            #pipe.send(["msg","Cannot connected. Try again in 2 seconds."])
            print("Cannot connect Authentication server. Try again in 2 seconds.")
            time.sleep(2)


    connection = True
    #pipe.send(["msg","Connection Successful"])
    print("Authentication server Connection Successful")

    data=[]

    while connection:
        try:
            part = s.recv(2048)
        except:
            connection = False
            break
        #if not part: break 
        data.append(part)
        if len(part) < 2048:
            #try to assemble it, if successful.jump. else, get more. 
            try:
                k = pickle.loads(b"".join(data))
                #k = pd.read_pickle(b"".join(data))
                data=[]
                pipe.send(k)
            except:
                pass
    #pipe.send(["msg","Server disconnected"])
    # except Exception as e:
    #   pipe.send(["msg",e])
    #   print(e)
    #restarted the whole thing 


if __name__ == '__main__':

	#try:

	multiprocessing.freeze_support()


	#### SCANNER SUB PROCESS####
	request_scanner, receive_pipe = multiprocessing.Pipe()

	process_scanner = multiprocessing.Process(target=multi_processing_scanner, args=(receive_pipe,),daemon=True)
	process_scanner.daemon=True
	process_scanner.start()

	process_scanner_b = multiprocessing.Process(target=client_scanner, args=(receive_pipe,),daemon=True)
	process_scanner_b.daemon=True
	process_scanner_b.start()

	s = scanner_process_manager(request_scanner)

	#### DATABASE SUB PROCESS####

	request_database, receive_database = multiprocessing.Pipe()
	process_database = multiprocessing.Process(target=multi_processing_database, args=(receive_database,),daemon=True)
	process_database.daemon=True
	process_database.start()

	d = database_process_manager(request_database)

	### ppro update SUB PROCESS####

	request_pipe, receive_pipe = multiprocessing.Pipe()
	process_ppro = multiprocessing.Process(target=multi_processing_price, args=(receive_pipe,),daemon=True)
	process_ppro.daemon=True
	process_ppro.start()

	ppro = ppro_process_manager(request_pipe)

	### scanner pannel needs the manager. 


	### algo comms 
	server_side_comm, client_side_comm = multiprocessing.Pipe()
	# algo_comm_link = multiprocessing.Process(target=algo_manager_commlink, args=(client_side_comm,),daemon=True)
	# algo_comm_link.daemon=True
	# algo_comm_link.start()

	authen_comm, authen_clientside_comm = multiprocessing.Pipe()
	auth = multiprocessing.Process(target=authentication, args=(authen_comm,),daemon=True)
	auth.daemon=True
	auth.start()


	
	root = tk.Tk() 
	root.title("GoodTrade") 
	root.geometry("1800x700")
	root.minsize(1500, 600)
	root.maxsize(3000, 1500)

	root.protocol("WM_DELETE_WINDOW", on_closing)

	view = viewer(root,s,d,ppro,server_side_comm,authen_clientside_comm)
	root.mainloop()

	print("Main process terminated")


	request_scanner.send(["terminate"])
	process_database.terminate()
	process_ppro.terminate()

	request_scanner.recv()
	process_scanner.terminate()
	process_scanner.join()
	process_database.join()
	process_ppro.join()

	algo_comm_link.terminate()
	algo_comm_link.join()
	print("All subprocesses terminated")
	
	os._exit(1) 
	print("exit")