import tkinter as tk
from tkinter import ttk

import pip
try:
    import pandas as pd
except ImportError:
    pip.main(['install', 'pandas'])
    import pandas as pd

try:
    import numpy as np
except ImportError:
    pip.main(['install', 'numpy'])
    import numpy as np

# try:
#     pip.main(['install', 'matplotlib'])
#     pip.main(['install', 'requests'])
# except:
# 	pass

import os
import time
import threading
import sys
from tkinter import messagebox

from modules.Util_client import *
from modules.alerts import *
from modules.pannel import *	
from modules.Symbol_data_manager import *

from modules.Symbol_data_manager import *
from modules.spreadtrader import *

from modules.scanner import *

from modules.ppro_process_manager import *

from cores.algo_manager_comms import *
from cores.algo_process_manager_client import *

class viewer:

	def __init__(self,root,util_process,ppro_process,algo_comm,authen_comm,util_request):

		self.data = Symbol_data_manager()

		self.db = util_process
		self.db.set_symbols_manager(self.data)

		self.ppro = ppro_process
		self.ppro.set_symbols_manager(self.data)

		self.data.set_database_manager(self.db)
		self.data.set_ppro_manager(self.ppro)

		# self.algo_manager = algo_manager
		# self.algo_manager.set_symbols_manager(self.data)

		self.listening = ttk.LabelFrame(root,text="Analyzer") 
		self.listening.place(x=640,rely=0.05,relheight=1,width=1100)

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

		self.tab12 = tk.Canvas(self.tabControl)

		self.tabControl.add(self.tab1, text ='Tickers Manager') 

		self.tabControl.add(self.tab11, text ='Alerts map') 
		self.tabControl.add(self.tab10, text ='Prev Close') 
		self.tabControl.add(self.tab5, text ='High-Low')
		self.tabControl.add(self.tab6, text ='Open-High')
		self.tabControl.add(self.tab7, text ='Open-Low')
		self.tabControl.add(self.tab2, text ='Extreme Range') 
		self.tabControl.add(self.tab3, text ='Extreme Volume') 
		self.tabControl.add(self.tab4, text ='First five minutes')
		self.tabControl.add(self.tab9, text ='Premarket Breakout')

		self.tabControl.add(self.tab12,text='Pair Trader')

		self.tabControl.pack(expand = 1, fill ="both") 

		#self.tabControl.add(self.tab8, text ='All alerts') 
		#self.ticker_management_init(self.tab1)
		#self.all_alerts = all_alerts(self.tab8)

		self.open_high_pannel = openhigh(self.tab6,self.data)

		self.high_low_pannel = highlow(self.tab5,self.data)
		self.open_low_pannel = openlow(self.tab7,self.data)

		self.first_5 = firstfive(self.tab4,self.data)
		self.er = extremrange(self.tab2,self.data)
		self.ev = extremevolume(self.tab3,self.data)

		self.pv = prevclose(self.tab10,self.data,)

		self.br = breakout(self.tab9,self.data,algo_comm)#algo_comm #,algo_comm
		self.am = alert_map(self.tab11,self.data)
		#alerts  =[self.open_high_pannel]
		alerts = [self.high_low_pannel,self.open_high_pannel,self.open_low_pannel,self.first_5,self.er,self.ev,self.br,self.pv,self.am]

		self.tm = ticker_manager(self.tab1,self.data,alerts,authen_comm)
		
		self.pair =  spread_trader(self.tab12,self.data)

		self.scanner_pannel = scanner(root,self.tm,util_process,self.data,util_request,algo_comm)

		util_process.set_pannel(self.scanner_pannel)



class ticker_manager(pannel):
	def __init__(self,frame,data,alerts,authen_comm):
		super().__init__(frame)

		self.authen = authen_comm

		self.alerts = alerts
		self.data = data

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

		self.symbol = tk.Button(frame,command=self.data.retech_database) #,command=self.loadsymbol
		self.symbol.place(x=400, y=5, height=30, width=120, bordermode='ignore')
		self.symbol.configure(activebackground="#ececec")
		self.symbol.configure(activeforeground="#000000")
		self.symbol.configure(background="#d9d9d9")
		self.symbol.configure(disabledforeground="#a3a3a3")
		self.symbol.configure(foreground="#000000")
		self.symbol.configure(highlightbackground="#d9d9d9")
		self.symbol.configure(highlightcolor="black")
		self.symbol.configure(pady="0")
		self.symbol.configure(text='''Refresh Database''')

		self.trader_stats = ttk.Label(frame, text="User Authentication:")
		#self.trader_stats.place(x = 400, y =12)

		self.permission_stats = ttk.Label(frame, text="Permission Status:")
		#self.permission_stats.place(x = 600, y =12)

		self.ticker_stats = ttk.Label(frame, text="Current Registered Tickers: "+str(self.ticker_count))
		self.ticker_stats.place(x = 800, y =12)

		#############Registration Window ####################

		


		self.width = [8,10,12,10,15,24,10,10]
		self.labels = ["Ticker","Status","Last update","Price","Status","Last Alert","Last Alert time","Remove"]

		#init the labels. 
		self.labels_creator(self.frame)

		self.init_reg_list()

		#data = threading.Thread(target=self.recv, name="Authen thread",daemon=True)
		#data.start()

		
	def init_reg_list(self):

		ticks = self.data.get_list()

		data = threading.Thread(target=self.adding_one_by_one(ticks), name="init reg list thread", daemon=True)
		data.start()

	def adding_one_by_one(self,ticks):

		try:

			for i in range(len(ticks)):
				self.add_symbol_label(ticks[i])

			self.tickers = self.data.get_list()
			self.rebind(self.canvas,self.frame)

			self.data.start=True

		except:

			print("util activate failed")

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
		#["Ticker","Status","Last update","Price","Status","Last Alert","Last Alert time","Remove"]
		info = [symbol,\
				self.data.symbol_status[symbol],\
				self.data.symbol_update_time[symbol],\
				self.data.symbol_price[symbol],\
				self.data.symbol_position_status[symbol],\
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

		try:
			k=self.authen.recv()
			name=k[0]
			per=k[1]
			sta=k[2]
			self.trader_stats["text"]= "User Authentication: "+name
			self.permission_stats["text"]="Permission Status:"+per
		except:
			print("Authen not good")
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


#Utility 

def utils(algo_manager_receive_comm,util_response):

		# db = threading.Thread(target=multi_processing_database,args=(db_sending_pipe,),daemon=True)
		# db.start()
		time.sleep(5)
		algo_comm = threading.Thread(target=algo_manager_commlink,args=(algo_manager_receive_comm,util_response,),daemon=True)
		algo_comm.start()

		receiver = threading.Thread(target=algo_server,args=(util_response,),daemon=True)
		receiver.start()

		util_comms(util_response)
if __name__ == '__main__':

	#try:

	multiprocessing.freeze_support()




	### scanner pannel needs the manager. 

	
	# auth = multiprocessing.Process(name="Authentica",target=authentication, args=(authen_comm,),daemon=True)
	# auth.daemon=True
	#auth.start()

	### algo comms 
	#algo_manager_comm, algo_manager_thread_comm = multiprocessing.Pipe()
	algo_manager_receive_comm, algo_manager_process_comm = multiprocessing.Pipe()
	
	# algo_comm_link = multiprocessing.Process(target=algo_manager_commlink, args=(algo_manager_receive_comm,),daemon=True)
	# algo_comm_link.daemon=True
	#algo_comm_link.start()


	#UTIL#

	# algo_comm = threading.Thread(target=algo_manager_commlink, args=(algo_manager_receive_comm,),daemon=True)
	# algo_comm.daemon=True

	#algo_manager_commlink(algo_manager_receive_comm)

	#GARBAGE SECTION
	authen_comm, authen_clientside_comm = multiprocessing.Pipe()

	#################


	util_request, util_response = multiprocessing.Pipe()



	# utility = multiprocessing.Process(target=utils, args=(scanner_sending_pipe,db_sending_pipe,algo_manager_receive_comm,util_receive),daemon=True)
	# utility.daemon=True


	root = tk.Tk() 
	root.title("GoodTrade v506") 
	root.geometry("1800x900")
	root.minsize(1500, 600)
	root.maxsize(3000, 1500)


	#algo_manager = algo_process_manager_client(algo_manager_process_comm,root)
	
	utility = multiprocessing.Process(target=utils, args=(algo_manager_receive_comm,util_response),daemon=True)
	utility.daemon=True


	root.protocol("WM_DELETE_WINDOW", on_closing)

	util_process = util_client(util_request)

	request_pipe, receive_pipe = multiprocessing.Pipe()
	process_ppro = multiprocessing.Process(target=multi_processing_price, args=(receive_pipe,util_process,),daemon=True)
	process_ppro.daemon=True
	process_ppro.start()
	ppro = ppro_process_manager(request_pipe)
	
	view = viewer(root,util_process,ppro,algo_manager_process_comm,authen_clientside_comm,util_request)
	
	# PPRO SECTION ##


	

	utility.start()

	root.mainloop()

	print("Main process terminated")

	#scanner_request_scanner.send(["terminate"])
	utility.terminate()
	process_ppro.terminate()
	#scanner_request_scanner.recv()

	utility.join()
	process_ppro.join()

	print("All subprocesses terminated")
	
	os._exit(1) 
	print("exit")