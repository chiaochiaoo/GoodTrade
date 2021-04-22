from pannel import *
from tkinter import ttk

#Thoughts:
#Combine PPRO sutff with VOXCOM into one process.

#Create subclass for the algo manager.

#Entry strategy 

#Manage strategy

#How to get the machine to read chart?


#DATA CLASS. SUPPORT/RESISTENCE. 
class symbol:

	def __init__(self,symbol):

		self.symbol = symbol

		self.bid = 0
		self.ask = 0

		self.support = 0
		self.resistence = 0

		self.open = 0
		self.high = 0
		self.low = 0

		self.total_realized = 0
		self.number_trades = 0

		self.triggers=[]

	def update_price(self,bid,ask,ts):

		self.bid = bid
		self.ask = ask
		self.timestamp = ts

		remove = []
		for i in self.triggers:
			if i.check():
				#print(1)
				remove.append(i)

		#execute the actions on remove.
		#remove it from triggers.
		for i in remove:
			i.trigger_event()
			self.triggers.remove(i)

	def get_bid(self):
		return self.bid

	def get_ask(self):
		return self.ask

	def get_time(self):
		return self.timestamp

	def add_trigger(self,info,type_,trigger_price,timer):
		self.triggers.append(trigger(self,info,type_,trigger_price,timer))

class trigger:

	def __init__(self,sym:symbol,info,type_,trigger_price,timer):

		self.symbol = sym
		#bigger, or less than. 

		self.info = info

		self.type = type_

		self.trigger_price = trigger_price

		#stay above this time. 
		self.trigger_timer = timer

		self.triggered = False
		self.trigger_time = 0
		self.trigger_duration = 0


	def check(self):

		#if it is above the price, update the time. put into is trigger 
		if self.type ==">":

			if self.symbol.get_bid()>=self.trigger_price:
				return self.check_trigger()
			else:
				self.reset()

		elif self.type =="<":

			if self.symbol.get_bid()<=self.trigger_price:
				self.check_trigger()
			else:
				return self.reset()

		return False
	def check_trigger(self):

		if self.triggered == False: #first time trigger

			self.triggered = True
			self.trigger_time = self.symbol.get_time() 
		
		else: #second tie trigger. update trigger duation
			self.trigger_duration = self.symbol.get_time() - self.trigger_time

		#check the trigger thingy. 
		return self.is_trigger()

	def is_trigger(self):
		
		if self.triggered==True and self.trigger_duration >= self.trigger_timer:
			return True
		else:
			return False 


	def trigger_event(self):  #once it's fired, it is gone.
		print(self.info,"at time",self.symbol.get_time())

	def reset(self):
		self.triggered = False
		self.trigger_time = 0
		self.trigger_duration = 0

class trade:
	def __init__(self,symbol,position,shares,price=None,rationale=None):

		self.activation = False
		self.symbol = symbol
		self.position = position
		self.shares = shares
		self.price = None

		self.stop_order = False
		self.stop_order_id = None

	def place_trade(self): #ask ppro to place orders.
		pass


class ui(pannel):
	def __init__(self,root):

		self.root = root

		self.tk_strings=["algo_status","realized","shares","unrealized","unrealized_pshr","average_price"]
		self.tk_labels=["symbol","algo_status","description","AR","break_at","stoplevel","position","act_r/est_r","average_price","shares","AM","pxtgt1","pxtgt2","pxtgt3","unrealized_pshr","unrealized","realized"]

		self.init_pannel()
	def init_pannel(self):

		# self.width = [10,10,30,8,8,8,8,8,8,8,6]
		# self.labels = []

		#"AM":4,\
		#				"PxTgt 1":8,\
		#				"PxTgt 2":8,\
		#				"PxTgt 3":8,\
		self.labels = {"Symbol":10,\
						"Algo status":10,\
						"Algo rationale":12,\
						"Strategy":10,\
						"Config":12,\
						"AR":4,\
						"Sup":6,\
						"Res":6,\
						"Act/Est R":8,\
						"AvgPx":8,\
						"SzIn":6,\
						"Position":6,\
						"PosMan":8,\
						"Configm":8,\
						"UPshr":8,\
						"U":8,\
						"R":8,\
						"flatten":10,
						"log":5}

		self.width = list(self.labels.values())

		self.setting = ttk.LabelFrame(self.root,text="Algo Manager") 
		self.setting.place(x=10,y=10,height=250,width=180)


		self.main_app_status = tk.StringVar()
		self.main_app_status.set("Main :")

		self.ppro_status = tk.StringVar()
		self.ppro_status.set("Ppro :")



		self.algo_count_number = 0
		# self.algo_count_string.set("Activated Algos:"+str(self.algo_count_number))

		# self.algo_count_ = ttk.Label(self.setting, textvariable=self.algo_count_string)
		# self.algo_count_.grid(column=1,row=5,padx=10)

		self.main_status = ttk.Label(self.setting, textvariable=self.main_app_status)
		self.main_status.grid(column=1,row=1,padx=10)
		#self.main_status.place(x = 20, y =12)

		self.ppro_status_ = ttk.Label(self.setting, textvariable=self.ppro_status)
		self.ppro_status_.grid(column=1,row=2,padx=10)
		#self.ppro_status_.place(x = 20, y =32)

		self.algo_count_string = tk.StringVar()

		self.algo_timer_string = tk.StringVar()

		self.timerc = ttk.Label(self.setting, text="Opening Algos deploy in:")
		self.timerc.grid(column=1,row=3,padx=10)
		self.timersx = ttk.Label(self.setting,  textvariable=self.algo_timer_string)
		self.timersx.grid(column=1,row=4,padx=10)



		# self.algo_deploy = ttk.Button(self.setting, text="Deploy all algo")#,command=self.deploy_all_stoporders)
		# self.algo_deploy.grid(column=1,row=6)

		# self.algo_cancel = ttk.Button(self.setting, text="Unmount all algo")#,command=self.cancel_all_stoporders)
		# self.algo_cancel.grid(column=1,row=7)

		# self.algo_cancel = ttk.Button(self.setting, text="Flatten all algo",command=self.cancel_all_stoporders)
		# self.algo_cancel.grid(column=1,row=6)

		# self.algo_cancel = ttk.Button(self.setting, text="Cancel all algo",command=self.cancel_all_stoporders)
		# self.algo_cancel.grid(column=1,row=7)

		self.total_u = tk.StringVar()
		self.total_r = tk.StringVar()

		self.log_panel = ttk.LabelFrame(root,text="Logs") 
		self.log_panel.place(x=10,y=250,relheight=0.8,width=180)

		self.deployment_panel = ttk.LabelFrame(root,text="Algo deployment") 
		self.deployment_panel.place(x=200,y=10,relheight=1,width=1400)

		self.dev_canvas = tk.Canvas(self.deployment_panel)
		self.dev_canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)

		self.scroll = tk.Scrollbar(self.deployment_panel)
		self.scroll.config(orient=tk.VERTICAL, command=self.dev_canvas.yview)
		self.scroll.pack(side=tk.RIGHT,fill="y")
		self.dev_canvas.configure(yscrollcommand=self.scroll.set)

		self.deployment_frame = tk.Frame(self.dev_canvas)
		self.deployment_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)
		self.dev_canvas.create_window(0, 0, window=self.deployment_frame, anchor=tk.NW)


		self.rebind(self.dev_canvas,self.deployment_frame)
		self.recreate_labels()

	def recreate_labels(self):

		l = list(self.labels.keys())
		w = list(self.labels.values())

		for i in range(len(l)): #Rows
			self.b = tk.Button(self.deployment_frame, text=l[i],width=w[i],height=2)#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=1, column=i)
# class manager:
# 	def __init__(self):



if __name__ == '__main__':

	#TEST CASES for trigger.
	# aapl = symbol("aapl")
	# aapl.add_trigger("breakup",">",11,3)
	# aapl.update_price(10,11,0)
	# aapl.update_price(10,11,1)
	# aapl.update_price(11,13,2)
	# aapl.update_price(11,11,3)
	# aapl.update_price(12,13,4)
	# aapl.update_price(11,11,5)

	root = tk.Tk() 

	# s=ttk.Style()
	# print(s.theme_names())
	# s.theme_use('winnative')
	root.title("GoodTrade Algo Manager v2") 
	root.geometry("1600x1000")
	root.minsize(1600, 1000)
	root.maxsize(1800, 1200)

	a=ui(root)

	root.mainloop()