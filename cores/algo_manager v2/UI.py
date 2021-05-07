from pannel import *
from constant import *

class UI(pannel):
	def __init__(self,root,manager=None):

		self.root = root


		self.manager = manager

		self.tk_strings=["algo_status","realized","shares","unrealized","unrealized_pshr","average_price"]
		self.tk_labels=[SYMBOL,STATUS,MIND, 'EntryPlan', 'EntryType', 'ETmr', 'Management','Reload', 'AR', 'Sup', 'Res', 'Act/Est R', 'Position', 'AvgPx', 'SzIn', 'UPshr', 'U', 'R', 'TR', 'flatten', 'log']
		
		self.tklabels = {}
		self.label_count = 1

		self.algo_counts = 0

		self.option_values()

		self.init_pannel()

	def option_values(self):

		self.entry_type_options = {INSTANT,INCREMENTAL}

		self.entry_plan_options = {BREAISH,BULLISH,BREAKUP,BREAKDOWN,BREAKANY}

		self.management_plan_options = {NONE,THREE_TARGETS,TRAILING_FIB}



	def init_HQ_pannel(self):

		self.main_app_status = tk.StringVar()
		self.main_app_status.set("")

		self.ppro_status = tk.StringVar()
		self.ppro_status.set("")


		self.algo_count_number = tk.DoubleVar(value=0)
		self.algo_number = 0

		self.algo_count_string = tk.StringVar(value="0")
		self.algo_timer_string = tk.StringVar(value="0")
		self.algo_count_string.set("Activated Algos:"+str(self.algo_count_number))

		self.main = ttk.Label(self.comms, text="Main:")
		self.main.grid(sticky="w",column=1,row=1,padx=10)
		self.main_status = ttk.Label(self.comms, textvariable=self.main_app_status)
		self.main_status.grid(sticky="w",column=2,row=1)

		self.ppro = ttk.Label(self.comms, text="Ppro:")
		self.ppro.grid(sticky="w",column=1,row=2,padx=10)
		self.ppro_status_ = ttk.Label(self.comms, textvariable=self.ppro_status)
		self.ppro_status_.grid(sticky="w",column=2,row=2)

		self.al = ttk.Label(self.comms, text="Algo count::")
		self.al.grid(sticky="w",column=1,row=3,padx=10)
		self.algo_count_ = ttk.Label(self.comms,  textvariable=self.algo_count_number)
		self.algo_count_.grid(sticky="w",column=2,row=3,padx=10)

		self.timerc = ttk.Label(self.comms, text="Deploy in:")
		self.timerc.grid(sticky="w",column=1,row=4,padx=10)
		self.timersx = ttk.Label(self.comms,  textvariable=self.algo_timer_string)
		self.timersx.grid(sticky="w",column=2,row=4,padx=10)

	def init_config_pannel(self):

		ttk.Label(self.config, text="All timer:").grid(sticky="w",column=1,row=5,padx=10)

		ttk.Label(self.config, text="Aall EnPlan:").grid(sticky="w",column=1,row=6,padx=10)

		ttk.Label(self.config, text="All EnType:").grid(sticky="w",column=1,row=7,padx=10)

		ttk.Label(self.config, text="All Manaplan:",anchor="w").grid(sticky="w",column=1,row=8,padx=10)


		self.all_timer = tk.DoubleVar(value=0)
		tk.Entry(self.config,textvariable=self.all_timer,width=5).grid(sticky="w",column=2,row=5,padx=10)


		self.all_enp = tk.StringVar(value=BREAKANY)
		tk.OptionMenu(self.config, self.all_enp, *sorted(self.entry_plan_options)).grid(sticky="w",column=2,row=6,padx=10)

		self.all_ent = tk.StringVar(value=INSTANT)
		tk.OptionMenu(self.config, self.all_ent, *sorted(self.entry_type_options)).grid(sticky="w",column=2,row=7,padx=10)

		self.all_mana = tk.StringVar(value=NONE)
		tk.OptionMenu(self.config, self.all_mana, *sorted(self.management_plan_options)).grid(sticky="w",column=2,row=8,padx=10)


		self.algo_deploy = ttk.Button(self.config, text="Apply to selected")#,command=self.manager.set_all_tp)
		self.algo_deploy.grid(column=1,row=9)


		self.algo_deploy = ttk.Button(self.config, text="Apply to all",command=self.manager.set_all_tp)#,command=self.deploy_all_stoporders)
		self.algo_deploy.grid(column=2,row=9)

	def init_command(self):

		self.algo_deploy = ttk.Button(self.cmd, text="Deploy all algo",command=self.manager.deploy_all)#,command=self.deploy_all_stoporders)
		self.algo_deploy.grid(sticky="w",column=1,row=10)

		self.algo_pend = ttk.Button(self.cmd, text="Withdraw all algo",command=self.manager.withdraw_all)#,command=self.cancel_all_stoporders)
		self.algo_pend.grid(sticky="w",column=2,row=10)

		self.flatten = ttk.Button(self.cmd, text="Flatten all algo",command=self.manager.flatten_all)
		self.flatten.grid(sticky="w",column=1,row=11)

		self.algo_cancel = ttk.Button(self.cmd, text="Cancel all algo",command=self.manager.cancel_all)
		self.algo_cancel.grid(sticky="w",column=2,row=11)


	def init_pannel(self):
		self.labels = {"Symbol":10,\
						"Status":10,\
						"MIND":20,\
						"EntryPlan":11,\
						"EntryType":12,\
						"Timer":5,\
						"Management":14,\
						"Reload":6,\
						"AR":4,\
						"Sup":6,\
						"Res":6,\
						"Act/Est R":8,\
						"Position":6,\
						"Stop":8,\
						"AvgPx":8,\
						"SzIn":6,\
						"PxT1":5,\
						"PxT2":5,\
						"PxT3":5,\
						"UPshr":8,\
						"U":8,\
						"R":8,\
						"TR":8,\
						"flatten":10,
						"log":5}

		#print(list(self.labels.keys()))
		self.width = list(self.labels.values())

		self.comms = ttk.LabelFrame(self.root,text="HQ") 
		self.comms.place(x=10,y=10,height=150,width=210)

		self.init_HQ_pannel()

		self.config = ttk.LabelFrame(self.root,text="Config") 
		self.config.place(x=10,y=140,height=160,width=210)

		self.cmd = ttk.LabelFrame(self.root,text="Command") 
		self.cmd.place(x=10,y=310,height=160,width=210)


		self.init_config_pannel()
		self.init_command()
		# self.log_panel = ttk.LabelFrame(self.root,text="Events") 
		# self.log_panel.place(x=10,y=300,relheight=0.5,width=210)

		self.deployment_panel = ttk.LabelFrame(self.root,text="Algo deployment") 
		self.deployment_panel.place(x=210,y=10,relheight=0.85,width=1700)

		self.total_u = tk.StringVar()
		self.total_r = tk.StringVar()



		self.dev_canvas = tk.Canvas(self.deployment_panel)
		self.dev_canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)

		self.scroll = tk.Scrollbar(self.deployment_panel)
		self.scroll.config(orient=tk.VERTICAL, command=self.dev_canvas.yview)
		self.scroll.pack(side=tk.RIGHT,fill="y")
		self.dev_canvas.configure(yscrollcommand=self.scroll.set)

		self.deployment_frame = tk.Frame(self.dev_canvas)
		self.deployment_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)
		self.dev_canvas.create_window(0, 0, window=self.deployment_frame, anchor=tk.NW)

		#self.create_example_trade()

		self.rebind(self.dev_canvas,self.deployment_frame)
		self.recreate_labels()


	def create_new_entry(self,tradingplan):


		infos = {
		'Symbol':tradingplan.symbol_name, \
		STATUS:tradingplan.tkvars[STATUS],\
		MIND: tradingplan.tkvars[MIND],\
		ENTRYPLAN:tradingplan.tkvars[ENTRYPLAN], \
		ENTYPE:tradingplan.tkvars[ENTYPE], \
		TIMER:tradingplan.tkvars[TIMER], \
		MANAGEMENTPLAN:tradingplan.tkvars[MANAGEMENTPLAN], \
		"Reload":tradingplan.tkvars[RELOAD], \
		'AR':tradingplan.tkvars[AUTORANGE], \
		SUPPORT:tradingplan.tkvars[SUPPORT], \
		RESISTENCE:tradingplan.tkvars[RESISTENCE], \
		RISK_RATIO:tradingplan.tkvars[RISK_RATIO], \
		'Position':tradingplan.tkvars[POSITION], \
		'Stop':tradingplan.tkvars[STOP_LEVEL],\
		'AvgPx':tradingplan.tkvars[AVERAGE_PRICE], \
		'SzIn':tradingplan.tkvars[SIZE_IN], \
		PXT1: tradingplan.tkvars[PXT1], \
		PXT2:tradingplan.tkvars[PXT2], \
		PXT3:tradingplan.tkvars[PXT3], \
		UNREAL_PSHR:tradingplan.tkvars[UNREAL_PSHR], \
		UNREAL:tradingplan.tkvars[UNREAL], \
		REALIZED:tradingplan.tkvars[REALIZED], \
		TOTAL_REALIZED:tradingplan.tkvars[TOTAL_REALIZED], \
		'flatten':"", \
		'log':""}

		l = self.label_count

		info = list(infos.values())
		labels = list(infos.keys())
		symbol = info[0]
		self.tklabels[symbol] = {}
		for j in range(len(info)):
			#"symbol","algo_status","description","break_at","position","act_r/est_r","stoplevel","average_price","shares","pxtgt1","pxtgt1","pxtgt1","unrealized_pshr","unrealized","realized"
			label_name = labels[j]

			if label_name == "Symbol":
				self.tklabels[symbol][label_name] = tk.Button(self.deployment_frame ,text=info[j],width=self.width[j],command=tradingplan.deploy)
			elif label_name == STATUS:
				self.tklabels[symbol][label_name] = tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command=tradingplan.cancle_deployment)

			elif label_name ==TIMER:
				self.tklabels[symbol][label_name] = tk.Entry(self.deployment_frame,textvariable=info[j],width=self.width[j])

			elif label_name ==ENTRYPLAN:
				self.tklabels[symbol][label_name] = tk.OptionMenu(self.deployment_frame, info[j], *sorted(self.entry_plan_options))

			elif label_name ==ENTYPE:
				self.tklabels[symbol][label_name] = tk.OptionMenu(self.deployment_frame, info[j], *sorted(self.entry_type_options))

			elif label_name ==MANAGEMENTPLAN:
				self.tklabels[symbol][label_name] =tk.OptionMenu(self.deployment_frame, info[j], *sorted(self.management_plan_options))

			elif label_name =="AR" :
				self.tklabels[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j],width=2,command=tradingplan.AR_toggle)
			elif label_name =="Reload":
				self.tklabels[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j],width=2)

			elif label_name =="MIND":
				self.tklabels[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])

			elif label_name =="flatten":
				self.tklabels[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command=tradingplan.flatten_cmd)

			elif label_name == SUPPORT or label_name == RESISTENCE or label_name == "pxtgt1" or label_name == "pxtgt2" or label_name == "pxtgt3":
				self.tklabels[symbol][label_name] =tk.Entry(self.deployment_frame ,textvariable=info[j],width=self.width[j],state="disabled")	
			else:
				if str(type(info[j]))=="<class 'tkinter.StringVar'>" or str(type(info[j]))=="<class 'tkinter.DoubleVar'>":
					self.tklabels[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
				else:
					#print(self.tklabels[symbol])
					self.tklabels[symbol][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])
			try:
				self.label_default_configure(self.tklabels[symbol][label_name])
			except:
				pass

			tradingplan.tklabels[label_name] = self.tklabels[symbol][label_name]

			self.tklabels[symbol][label_name].grid(row= l+2, column=j,padx=0)

		self.label_count +=1

		self.algo_count_number.set(self.label_count-1)
		self.rebind(self.dev_canvas,self.deployment_frame)
		self.recreate_labels()
		tradingplan.update_displays()

	def create_example_trade(self):

		info=['AAPL','STATUS', 'MIND', 'Bullish', 'EntryStrat', 'Timer', 'ManaStart', 'AR', 'Sup', 'Res', 'Act/Est R', 'Long', 'AvgPx', 'SzIn', 'UPshr', 'U', 'R', 'TR', 'flatten', 'log']
		symbol = 'AAPL'
		self.tklabels[symbol]={}
		self.tklabels[symbol][1]=1
		l = self.label_count
		for j in range(len(info)):
			#"symbol","algo_status","description","break_at","position","act_r/est_r","stoplevel","average_price","shares","pxtgt1","pxtgt1","pxtgt1","unrealized_pshr","unrealized","realized"
			label_name = self.tk_labels[j]

			if label_name == "Symbol":
				self.tklabels[symbol][label_name] = tk.Button(self.deployment_frame ,text=info[j],width=self.width[j],command = lambda s=symbol: self.deploy_stop_order(symbol))

			elif label_name =="Timer":
				self.tklabels[symbol][label_name] = tk.Entry(self.deployment_frame,textvariable=info[j],width=self.width[j])

			# elif label_name =="EntryStrat":
			# 	self.tklabels[symbol][label_name] = tk.OptionMenu(self.deployment_frame, textvariable="",set())

			# elif label_name =="ManaStart":
			# 	self.tklabels[symbol][label_name] = tk.OptionMenu(self.deployment_frame, textvariable="",set())

			elif label_name =="AR" or  label_name =="AM":
				self.tklabels[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j])
			elif label_name =="MIND":
				self.tklabels[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command = lambda s=symbol: self.cancel_deployed(symbol))
			elif label_name == "Sup" or label_name == "Res" or label_name == "pxtgt1" or label_name == "pxtgt2" or label_name == "pxtgt3":
				self.tklabels[symbol][label_name] =tk.Entry(self.deployment_frame ,textvariable=info[j],width=self.width[j])	
			else:
				if str(type(info[j]))=="<class 'tkinter.StringVar'>":
					self.tklabels[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
				else:
					#print(self.tklabels[symbol])
					self.tklabels[symbol][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

			try:
				self.label_default_configure(self.tklabels[symbol][label_name])
			except:
				pass
			self.tklabels[symbol][label_name].grid(row= l+2, column=j,padx=0)


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
		symbol = info[0][1]
		status = info[1]
		l = self.label_count

		#self.tickers_labels[i]=[]
		self.tickers_tracers[i] = []
		self.tklabels[symbol] = {}

		#add in tickers.
		#print("LENGTH",len(info))
		for j in range(len(info)):
			#"symbol","algo_status","description","break_at","position","act_r/est_r","stoplevel","average_price","shares","pxtgt1","pxtgt1","pxtgt1","unrealized_pshr","unrealized","realized"
			label_name = self.tk_labels[j]

			if label_name == "symbol":
				self.tklabels[symbol][label_name] =tk.Button(self.deployment_frame ,text=info[j][0],width=self.width[j],command = lambda s=symbol: self.deploy_stop_order(symbol))	
			elif label_name =="AR" or  label_name =="AM":
				self.tklabels[symbol][label_name] =tk.Checkbutton(self.deployment_frame,variable=info[j])
			elif label_name =="algo_status":
				self.tklabels[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command = lambda s=symbol: self.cancel_deployed(symbol))
			elif label_name == "break_at" or label_name == "stoplevel" or label_name == "pxtgt1" or label_name == "pxtgt2" or label_name == "pxtgt3":
				self.tklabels[symbol][label_name] =tk.Entry(self.deployment_frame ,textvariable=info[j],width=self.width[j])	
			else:
				if str(type(info[j]))=="<class 'tkinter.StringVar'>":
					self.tklabels[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
				else:
					self.tklabels[symbol][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

			try:
				self.label_default_configure(self.tklabels[symbol][label_name])
			except:
				pass
			self.tklabels[symbol][label_name].grid(row= l+2, column=j,padx=0)

			#else: #command = lambda s=symbol: self.delete_symbol_reg_list(s))

		j+=1
		flatten=tk.Button(self.deployment_frame ,text="flatten",width=self.width[j],command= lambda k=i:self.flatten_symbol(k,symbol,status))
		self.label_default_configure(flatten)
		flatten.grid(row= l+2, column=j,padx=0)

		self.label_count +=1

		self.rebind(self.dev_canvas,self.deployment_frame)
	

if __name__ == '__main__':

	root = tk.Tk() 
	root.title("GoodTrade Algo Manager v2") 
	root.geometry("1920x1000")

	UI(root)
	# root.minsize(1600, 1000)
	# root.maxsize(1800, 1200)
	root.mainloop()