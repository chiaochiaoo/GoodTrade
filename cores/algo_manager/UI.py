from pannel import *

class UI(pannel):
	def __init__(self,root):

		self.root = root

		self.tk_strings=["algo_status","realized","shares","unrealized","unrealized_pshr","average_price"]
		self.tk_labels=['Symbol', 'MIND', 'TradingPlan', 'EntryStrat', 'Timer', 'ManaStart', 'AR', 'Sup', 'Res', 'Act/Est R', 'Position', 'AvgPx', 'SzIn', 'UPshr', 'U', 'R', 'TR', 'flatten', 'log']
		
		self.order_tklabels = {}
		self.label_count = 1
		self.init_pannel()
	def init_pannel(self):
		self.labels = {"Symbol":10,\
						"MIND":20,\
						"TradingPlan":12,\
						"EntryStrat":12,\
						"Timer":5,\
						"ManaStart":8,\
						"AR":4,\
						"Sup":6,\
						"Res":6,\
						"Act/Est R":8,\
						"Position":6,\
						"AvgPx":8,\
						"SzIn":6,\
						"UPshr":8,\
						"U":8,\
						"R":8,\
						"TR":8,\
						"flatten":10,
						"log":5}

		print(list(self.labels.keys()))
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
		self.log_panel.place(x=10,y=250,relheight=0.5,width=180)

		self.deployment_panel = ttk.LabelFrame(root,text="Algo deployment") 
		self.deployment_panel.place(x=200,y=10,relheight=0.85,width=1400)

		self.dev_canvas = tk.Canvas(self.deployment_panel)
		self.dev_canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)

		self.scroll = tk.Scrollbar(self.deployment_panel)
		self.scroll.config(orient=tk.VERTICAL, command=self.dev_canvas.yview)
		self.scroll.pack(side=tk.RIGHT,fill="y")
		self.dev_canvas.configure(yscrollcommand=self.scroll.set)

		self.deployment_frame = tk.Frame(self.dev_canvas)
		self.deployment_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)
		self.dev_canvas.create_window(0, 0, window=self.deployment_frame, anchor=tk.NW)


		self.create_example_trade()

		self.rebind(self.dev_canvas,self.deployment_frame)
		self.recreate_labels()

	def create_example_trade(self):

		
		info=['AAPL', 'MIND', 'Bullish', 'EntryStrat', 'Timer', 'ManaStart', 'AR', 'Sup', 'Res', 'Act/Est R', 'Long', 'AvgPx', 'SzIn', 'UPshr', 'U', 'R', 'TR', 'flatten', 'log']
		id_ = 'AAPL'
		self.order_tklabels[id_]={}
		self.order_tklabels[id_][1]=1
		l = self.label_count
		for j in range(len(info)):
			#"symbol","algo_status","description","break_at","position","act_r/est_r","stoplevel","average_price","shares","pxtgt1","pxtgt1","pxtgt1","unrealized_pshr","unrealized","realized"
			label_name = self.tk_labels[j]

			if label_name == "Symbol":
				self.order_tklabels[id_][label_name] =tk.Button(self.deployment_frame ,text=info[j],width=self.width[j],command = lambda s=id_: self.deploy_stop_order(id_))	
			#elif label_name =="TradingPlan":
				#self.order_tklabels[id_][label_name] =tk.Option(self.deployment_frame,variable=info[j])

			elif label_name =="AR" or  label_name =="AM":
				self.order_tklabels[id_][label_name] =tk.Checkbutton(self.deployment_frame,variable=info[j])
			elif label_name =="MIND":
				self.order_tklabels[id_][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command = lambda s=id_: self.cancel_deployed(id_))
			elif label_name == "Sup" or label_name == "Res" or label_name == "pxtgt1" or label_name == "pxtgt2" or label_name == "pxtgt3":
				self.order_tklabels[id_][label_name] =tk.Entry(self.deployment_frame ,textvariable=info[j],width=self.width[j])	
			else:
				if str(type(info[j]))=="<class 'tkinter.StringVar'>":
					self.order_tklabels[id_][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
				else:
					print(self.order_tklabels[id_])
					self.order_tklabels[id_][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

			try:
				self.label_default_configure(self.order_tklabels[id_][label_name])
			except:
				pass
			self.order_tklabels[id_][label_name].grid(row= l+2, column=j,padx=0)


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


	def add_symbol(self):
		pass
	def order_ui_creation(self,info):

		#if they already exisit, just repace the old ones.
		i = info[0][0]
		id_ = info[0][1]
		status = info[1]
		l = self.label_count

		#self.tickers_labels[i]=[]
		self.tickers_tracers[i] = []
		self.order_tklabels[id_] = {}

		#add in tickers.
		#print("LENGTH",len(info))
		for j in range(len(info)):
			#"symbol","algo_status","description","break_at","position","act_r/est_r","stoplevel","average_price","shares","pxtgt1","pxtgt1","pxtgt1","unrealized_pshr","unrealized","realized"
			label_name = self.tk_labels[j]

			if label_name == "symbol":
				self.order_tklabels[id_][label_name] =tk.Button(self.deployment_frame ,text=info[j][0],width=self.width[j],command = lambda s=id_: self.deploy_stop_order(id_))	
			elif label_name =="AR" or  label_name =="AM":
				self.order_tklabels[id_][label_name] =tk.Checkbutton(self.deployment_frame,variable=info[j])
			elif label_name =="algo_status":
				self.order_tklabels[id_][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command = lambda s=id_: self.cancel_deployed(id_))
			elif label_name == "break_at" or label_name == "stoplevel" or label_name == "pxtgt1" or label_name == "pxtgt2" or label_name == "pxtgt3":
				self.order_tklabels[id_][label_name] =tk.Entry(self.deployment_frame ,textvariable=info[j],width=self.width[j])	
			else:
				if str(type(info[j]))=="<class 'tkinter.StringVar'>":
					self.order_tklabels[id_][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
				else:
					self.order_tklabels[id_][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

			try:
				self.label_default_configure(self.order_tklabels[id_][label_name])
			except:
				pass
			self.order_tklabels[id_][label_name].grid(row= l+2, column=j,padx=0)

			#else: #command = lambda s=symbol: self.delete_symbol_reg_list(s))

		j+=1
		flatten=tk.Button(self.deployment_frame ,text="flatten",width=self.width[j],command= lambda k=i:self.flatten_symbol(k,id_,status))
		self.label_default_configure(flatten)
		flatten.grid(row= l+2, column=j,padx=0)

		self.label_count +=1

		self.rebind(self.dev_canvas,self.deployment_frame)
	


root = tk.Tk() 
root.title("GoodTrade Algo Manager") 
root.geometry("1500x500")

UI(root)
# root.minsize(1600, 1000)
# root.maxsize(1800, 1200)
root.mainloop()