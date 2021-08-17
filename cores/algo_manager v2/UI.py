from pannel import *
from constant import *
from Util_functions import *

class UI(pannel):
	def __init__(self,root,manager=None):

		self.root = root


		self.manager = manager

		self.tk_strings=["algo_status","realized","shares","unrealized","unrealized_pshr","average_price"]
		self.tk_labels=[SYMBOL,STATUS,MIND, 'EntryPlan', 'EntryType', 'ETmr', 'Management','Reload', 'AR', 'Sup', 'Res', 'Act/Est R', 'Position', 'AvgPx', 'SzIn', 'UPshr', 'U', 'R', 'TR', 'flatten', 'log']

		self.tklabels = {}
		self.label_count = 1

		self.tklabels_list = []

		self.algo_counts = 0

		self.risk_timer = tk.DoubleVar(value=300)

		self.option_values()

		self.init_pannel()

		self.init_entry_pannel()

	def option_values(self):

		self.entry_type_options = {INSTANT,INCREMENTAL,INCREMENTAL2}

		self.entry_plan_options = {BREAISH,BULLISH,BREAKUP,BREAKDOWN,BREAKFIRST,BREAKANY,RIPSELL,DIPBUY,FADEANY}

		self.management_plan_options = {FIBO,EM_STRATEGY,EMASTRAT,ONETOTWORISKREWARD}#THREE_TARGETS,SMARTTRAIL,ANCARTMETHOD,ONETOTWORISKREWARD,ONETOTWORISKREWARDOLD,

	def init_pannel(self):
		self.labels = {"":4,\
						"Symbol":8,\
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
						"SzIn":6,\
						"Position":6,\
						"Stop":8,\
						"AvgPx":8,\
						"PxT1":5,\
						"PxT2":5,\
						"PxT3":5,\
						"UPshr":8,\
						"U":8,\
						"R":8,\
						"TR":8,\
						"flatten":8,
						"log":5}

		#print(list(self.labels.keys()))
		self.width = list(self.labels.values())

		self.comms = ttk.LabelFrame(self.root,text="HQ") 
		self.comms.place(x=10,y=10,height=150,width=210)

		self.init_HQ_pannel()

		self.config = ttk.LabelFrame(self.root,text="Config") 
		self.config.place(x=10,y=140,height=300,width=210)

		self.cmd = ttk.LabelFrame(self.root,text="Command") 
		self.cmd.place(x=10,y=380,height=500,width=210)


		self.init_config_pannel()
		self.init_command()
		# self.log_panel = ttk.LabelFrame(self.root,text="Events") 
		# self.log_panel.place(x=10,y=300,relheight=0.5,width=210)

		self.deployment_panel = ttk.LabelFrame(self.root,text="Algo deployment") 
		self.deployment_panel.place(x=210,y=10,relheight=0.85,width=1650)

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

	def init_HQ_pannel(self):

		self.main_app_status = tk.StringVar()
		self.main_app_status.set("")

		self.ppro_status = tk.StringVar()
		self.ppro_status.set("")

		self.algo_count_number = tk.DoubleVar(value=0)
		self.algo_number = 0

		self.algo_count_string = tk.StringVar(value="0")
		self.algo_timer_string = tk.StringVar(value="0")
		self.algo_timer_close_string = tk.StringVar(value="0")
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

		self.timerc = ttk.Label(self.comms, text="Close in:")
		self.timerc.grid(sticky="w",column=1,row=5,padx=10)
		self.timersx = ttk.Label(self.comms,  textvariable=self.algo_timer_close_string)
		self.timersx.grid(sticky="w",column=2,row=5,padx=10)

		ttk.Label(self.comms, text="Risk timer:").grid(sticky="w",column=1,row=6,padx=10)
		tk.Entry(self.comms,textvariable=self.risk_timer,width=5).grid(sticky="w",column=2,row=6,padx=10)
		# self.deconstruct = ttk.Button(self.comms, text="Terminate GT",command=self.manager.terminateGT)#,command=self.deploy_all_stoporders)
		# self.deconstruct.grid(sticky="w",column=1,row=5)


	def init_config_pannel(self):

		self.all_timer_b = tk.IntVar(value=1)
		self.all_risk_b = tk.IntVar(value=1)
		self.all_enplan_b = tk.IntVar(value=1)
		self.all_entype_b = tk.IntVar(value=1)
		self.all_manaplan_b = tk.IntVar(value=1)
		self.all_reload_b = tk.IntVar(value=1)


		row = 5

		ttk.Checkbutton(self.config, variable=self.all_reload_b).grid(sticky="w",column=1,row=row)
		ttk.Checkbutton(self.config, variable=self.all_timer_b).grid(sticky="w",column=1,row=row+1)
		ttk.Checkbutton(self.config, variable=self.all_risk_b).grid(sticky="w",column=1,row=row+2)
		ttk.Checkbutton(self.config, variable=self.all_enplan_b).grid(sticky="w",column=1,row=row+3,padx=0)
		ttk.Checkbutton(self.config, variable=self.all_entype_b).grid(sticky="w",column=1,row=row+4)
		ttk.Checkbutton(self.config, variable=self.all_manaplan_b).grid(sticky="w",column=1,row=row+5)


		ttk.Label(self.config, text="reload:").grid(sticky="w",column=2,row=row,padx=10)
		ttk.Label(self.config, text="timer:").grid(sticky="w",column=2,row=row+1,padx=10)
		ttk.Label(self.config, text="Rsk:").grid(sticky="w",column=2,row=row+2,padx=10)
		ttk.Label(self.config, text="Entry:").grid(sticky="w",column=2,row=row+3,padx=10)
		ttk.Label(self.config, text="EnType:").grid(sticky="w",column=2,row=row+4,padx=10)
		ttk.Label(self.config, text="Manage:").grid(sticky="w",column=2,row=row+5,padx=10)


		self.all_reload = tk.DoubleVar(value=1)
		tk.Entry(self.config,textvariable=self.all_reload,width=5).grid(sticky="w",column=3,row=row,padx=10)

		self.all_timer = tk.DoubleVar(value=0)
		tk.Entry(self.config,textvariable=self.all_timer,width=5).grid(sticky="w",column=3,row=row+1,padx=10)

		self.all_risk = tk.DoubleVar(value=50)
		tk.Entry(self.config,textvariable=self.all_risk,width=5).grid(sticky="w",column=3,row=row+2,padx=10)


		self.all_enp = tk.StringVar(value=BREAKFIRST)
		tk.OptionMenu(self.config, self.all_enp, *sorted(self.entry_plan_options)).grid(sticky="w",column=3,row=row+3,padx=10)

		self.all_ent = tk.StringVar(value=INCREMENTAL2)
		tk.OptionMenu(self.config, self.all_ent, *sorted(self.entry_type_options)).grid(sticky="w",column=3,row=row+4,padx=10)

		self.all_mana = tk.StringVar(value=FIBO)
		tk.OptionMenu(self.config, self.all_mana, *sorted(self.management_plan_options)).grid(sticky="w",column=3,row=row+5,padx=10)



		self.config2 = ttk.LabelFrame(self.config) 
		self.config2.place(x=0,y=160,height=100,width=210)
		self.algo_deploy = ttk.Button(self.config2, text="Apply Slctd",command=self.manager.set_selected_tp)#,command=self.manager.set_all_tp)
		self.algo_deploy.grid(sticky="w",column=1,row=1,padx=10)
		#self.algo_deploy.place(x=5,y=5)

		self.algo_deploy = ttk.Button(self.config2, text="Deslect All",command=self.manager.deselect_all)#,command=self.deploy_all_stoporders)
		self.algo_deploy.grid(sticky="w",column=1,row=2,padx=10)

		self.algo_deploy = ttk.Button(self.config2, text="Apply All",command=self.manager.set_all_tp)#,command=self.deploy_all_stoporders)
		self.algo_deploy.grid(sticky="w",column=2,row=1,padx=10)
		#self.algo_deploy.place(x=5,y=25)


	def set_command_text(self,string):
		self.command_text.set(string)

	def init_command(self):

		self.command_text = tk.StringVar(value="Ready:")

		ttk.Label(self.cmd, text="").grid(sticky="w",column=1,row=1)

		ttk.Label(self.cmd, textvariable=self.command_text).place(x=0,y=0)


		self.algo_deploy = ttk.Button(self.cmd, text="Deploy all algo",command=self.manager.deploy_all)#,command=self.deploy_all_stoporders)
		self.algo_deploy.grid(sticky="w",column=1,row=2)

		self.algo_pend = ttk.Button(self.cmd, text="Withdraw all algo",command=self.manager.withdraw_all)#,command=self.cancel_all_stoporders)
		self.algo_pend.grid(sticky="w",column=2,row=2)

		self.flatten = ttk.Button(self.cmd, text="Flatten all algo",command=self.manager.flatten_all)
		self.flatten.grid(sticky="w",column=1,row=3)

		self.algo_cancel = ttk.Button(self.cmd, text="Cancel all algo",command=self.manager.cancel_all)
		self.algo_cancel.grid(sticky="w",column=2,row=3)

		self.flatten = ttk.Button(self.cmd, text="Export Algos",command=self.manager.export_algos)
		self.flatten.grid(sticky="w",column=1,row=4)

		self.algo_cancel = ttk.Button(self.cmd, text="Import Algos",command=self.manager.import_algos)
		self.algo_cancel.grid(sticky="w",column=2,row=4)

		row=5
		ttk.Label(self.cmd, text=" ").grid(sticky="w",column=1,row=row)
		row+=1
		ttk.Label(self.cmd, text="All Active Winnings:").grid(sticky="w",column=1,row=row)

		row+=1
		ttk.Button(self.cmd, text="Add 10%",command= lambda action=ADD,percent=0.1:self.manager.trades_aggregation(None,action,percent,True)).grid(sticky="w",column=1,row=row)
		ttk.Button(self.cmd, text="Add 25%",command= lambda action=ADD,percent=0.25:self.manager.trades_aggregation(None,action,percent,True)).grid(sticky="w",column=2,row=row)

		row+=1
		ttk.Button(self.cmd, text="Minus 10%",command= lambda action=MINUS,percent=0.1:self.manager.trades_aggregation(None,action,percent,True)).grid(sticky="w",column=1,row=row)
		ttk.Button(self.cmd, text="Minus 25%",command= lambda action=MINUS,percent=0.25:self.manager.trades_aggregation(None,action,percent,True)).grid(sticky="w",column=2,row=row)


		ttk.Label(self.cmd, text=" ").grid(sticky="w",column=1,row=row)
		row+=1
		ttk.Label(self.cmd, text="All Active Longs:").grid(sticky="w",column=1,row=row)

		row+=1
		ttk.Button(self.cmd, text="Add 10%",command= lambda side=LONG,action=ADD,percent=0.1:self.manager.trades_aggregation(side,action,percent,False)).grid(sticky="w",column=1,row=row)
		ttk.Button(self.cmd, text="Add 25%",command= lambda side=LONG,action=ADD,percent=0.25:self.manager.trades_aggregation(side,action,percent,False)).grid(sticky="w",column=2,row=row)

		row+=1
		ttk.Button(self.cmd, text="Minus 10%",command= lambda side=LONG,action=MINUS,percent=0.1:self.manager.trades_aggregation(side,action,percent,False)).grid(sticky="w",column=1,row=row)
		ttk.Button(self.cmd, text="Minus 25%",command= lambda side=LONG,action=MINUS,percent=0.25:self.manager.trades_aggregation(side,action,percent,False)).grid(sticky="w",column=2,row=row)

		row+=1
		ttk.Label(self.cmd, text=" ").grid(sticky="w",column=1,row=row)
		row+=1
		ttk.Label(self.cmd, text="All Active Shorts:").grid(sticky="w",column=1,row=row)

		row+=1
		ttk.Button(self.cmd, text="Add 10%",command= lambda side=SHORT,action=ADD,percent=0.1:self.manager.trades_aggregation(side,action,percent,False)).grid(sticky="w",column=1,row=row)
		ttk.Button(self.cmd, text="Add 25%",command= lambda side=SHORT,action=ADD,percent=0.25:self.manager.trades_aggregation(side,action,percent,False)).grid(sticky="w",column=2,row=row)

		row+=1
		ttk.Button(self.cmd, text="Minus 10%",command= lambda side=SHORT,action=MINUS,percent=0.1:self.manager.trades_aggregation(side,action,percent,False)).grid(sticky="w",column=1,row=row)
		ttk.Button(self.cmd, text="Minus 25%",command= lambda side=SHORT,action=MINUS,percent=0.25:self.manager.trades_aggregation(side,action,percent,False)).grid(sticky="w",column=2,row=row)


		#iterate all the trading plans.
		#if position ="LONG"
		#if shares>= 25.
		#calculate the shares to be taken off. 

	def init_entry_pannel(self):

		infos = {
		SELECTED:"",\
		'Symbol':"", \
		STATUS:"",\
		MIND:"",\
		ENTRYPLAN:"", \
		ENTYPE:"", \
		TIMER:"", \
		MANAGEMENTPLAN:"", \
		"Reload":"", \
		'AR':"", \
		SUPPORT:"", \
		RESISTENCE:"", \
		RISK_RATIO:"", \
		'SzIn':"", \
		'Position':"", \
		'Stop':"",\
		'AvgPx':"", \
		PXT1:"", \
		PXT2:"", \
		PXT3:"", \
		UNREAL_PSHR:"", \
		UNREAL:"", \
		REALIZED:"", \
		TOTAL_REALIZED:"", \
		'flatten':"", \
		'log':""}

		info = list(infos.values())
		labels = list(infos.keys())

		for l in range(50):
			self.tklabels[l]={}
			for j in range(len(info)):
				#"symbol","algo_status","description","break_at","position","act_r/est_r","stoplevel","average_price","shares","pxtgt1","pxtgt1","pxtgt1","unrealized_pshr","unrealized","realized"
				label_name = labels[j]

				if label_name == "Symbol":
					self.tklabels[l][label_name] = tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])
				elif label_name == STATUS:
					self.tklabels[l][label_name] = tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

				elif label_name ==TIMER:
					self.tklabels[l][label_name] = tk.Entry(self.deployment_frame,text=info[j],width=self.width[j])

				elif label_name =="AR" :
					self.tklabels[l][label_name] = tk.Checkbutton(self.deployment_frame,width=2,)
				elif label_name =="Reload" or label_name==SELECTED:
					self.tklabels[l][label_name] = tk.Checkbutton(self.deployment_frame,width=2)

				elif label_name =="MIND":
					self.tklabels[l][label_name] =tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])
				elif label_name =="Stop":
					self.tklabels[l][label_name] =tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

				elif label_name ==RISK_RATIO:
					self.tklabels[l][RISK_PER_SHARE]=tk.Entry(self.deployment_frame ,text=info[j],width=self.width[j])

					self.tklabels[l][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

				elif label_name =='SzIn':
					self.tklabels[l][TARGET_SHARE]=tk.Entry(self.deployment_frame ,text=info[j],width=self.width[j])
	

					self.tklabels[l][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

				elif label_name =="flatten":
					self.tklabels[l][label_name] =tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

				elif label_name == SUPPORT or label_name == RESISTENCE or label_name == "pxtgt1" or label_name == "pxtgt2" or label_name == "pxtgt3":
					self.tklabels[l][label_name] =tk.Entry(self.deployment_frame ,text=info[j],width=self.width[j],state="disabled")	
				else:
					if str(type(info[j]))=="<class 'tkinter.StringVar'>" or str(type(info[j]))=="<class 'tkinter.DoubleVar'>":
						self.tklabels[l][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])
					else:
						#print(self.tklabels[symbol])
						self.tklabels[l][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])
				try:
					self.label_default_configure(self.tklabels[l][label_name])
				except:
					pass

				self.tklabels[l][label_name].grid(row= l+2, column=j,padx=0)

		self.rebind(self.dev_canvas,self.deployment_frame)


	def create_new_entry(self,tradingplan):


		infos = {
		SELECTED:tradingplan.tkvars[SELECTED],\
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
		'SzIn':tradingplan.tkvars[SIZE_IN], \
		'Position':tradingplan.tkvars[POSITION], \
		'Stop':tradingplan.tkvars[STOP_LEVEL],\
		'AvgPx':tradingplan.tkvars[AVERAGE_PRICE], \
		PXT1: tradingplan.tkvars[PXT1], \
		PXT2:tradingplan.tkvars[PXT2], \
		PXT3:tradingplan.tkvars[PXT3], \
		UNREAL_PSHR:tradingplan.tkvars[UNREAL_PSHR], \
		UNREAL:tradingplan.tkvars[UNREAL], \
		REALIZED:tradingplan.tkvars[REALIZED], \
		TOTAL_REALIZED:tradingplan.tkvars[TOTAL_REALIZED], \
		'flatten':"", \
		'log':""}


		#link the global variable 
		tradingplan.tkvars[RISKTIMER] = self.risk_timer 


		l = self.label_count

		info = list(infos.values())
		labels = list(infos.keys())
		symbol = l-1 #info[1]
		#self.tklabels[symbol] = {}

		for j in range(len(info)):
			#"symbol","algo_status","description","break_at","position","act_r/est_r","stoplevel","average_price","shares","pxtgt1","pxtgt1","pxtgt1","unrealized_pshr","unrealized","realized"
			label_name = labels[j]
			#print(self.tklabels[symbol])
			if label_name == "Symbol":
				self.tklabels[symbol][label_name]["text"] = info[j] #tk.Button(self.deployment_frame ,text=info[j],width=self.width[j],command=tradingplan.deploy)
				self.tklabels[symbol][label_name]["command"] = tradingplan.deploy
			elif label_name == STATUS:
				self.tklabels[symbol][label_name]["textvariable"] = info[j] 
				self.tklabels[symbol][label_name]["command"] = tradingplan.cancle_deployment
				#= tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command=tradingplan.cancle_deployment)

			elif label_name ==TIMER:
				self.tklabels[symbol][label_name]["textvariable"] = info[j] 
				#self.tklabels[symbol][label_name] = tk.Entry(self.deployment_frame,textvariable=info[j],width=self.width[j])

			elif label_name =="AR" :
				self.tklabels[symbol][label_name]["variable"] = info[j] 
				self.tklabels[symbol][label_name]["command"] = tradingplan.AR_toggle
				#self.tklabels[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j],width=2,command=tradingplan.AR_toggle)
			elif label_name =="Reload" or label_name==SELECTED:
				self.tklabels[symbol][label_name]["variable"] = info[j]
				#self.tklabels[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j],width=2)
				 
			elif label_name =="MIND":
				self.tklabels[symbol][label_name]["textvariable"] = info[j]
				#self.tklabels[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
			elif label_name =="Stop":
				self.tklabels[symbol][label_name]["textvariable"] = info[j]
				self.tklabels[symbol][label_name]["command"] = lambda tp=tradingplan:adjust_stop(tp)

				#self.tklabels[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command= lambda tp=tradingplan:adjust_stop(tp))


			elif label_name ==RISK_RATIO:
				self.tklabels[symbol][label_name]["textvariable"] = info[j]

				tradingplan.tklabels[RISK_PER_SHARE] = self.tklabels[symbol][RISK_PER_SHARE]

				#self.tklabels[symbol][RISK_PER_SHARE]=tk.Entry(self.deployment_frame ,textvariable=tradingplan.tkvars[RISK_PER_SHARE],width=self.width[j])
				#tradingplan.tklabels[RISK_PER_SHARE].grid(row= l+2, column=j,padx=0)

				#self.tklabels[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])

			elif label_name =='SzIn':
				# self.tklabels[symbol][TARGET_SHARE]=tk.Entry(self.deployment_frame ,textvariable=tradingplan.tkvars[INPUT_TARGET_SHARE],width=self.width[j])
				# tradingplan.tklabels[TARGET_SHARE] = self.tklabels[symbol][TARGET_SHARE]
				# tradingplan.tklabels[TARGET_SHARE].grid(row= l+2, column=j,padx=0)
				self.tklabels[symbol][label_name]["textvariable"] = info[j]
				#self.tklabels[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])

			elif label_name =="flatten":
				self.tklabels[symbol][label_name]["command"] = tradingplan.flatten_cmd
				#self.tklabels[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command=tradingplan.flatten_cmd)

			elif label_name == SUPPORT or label_name == RESISTENCE or label_name == "pxtgt1" or label_name == "pxtgt2" or label_name == "pxtgt3":
				self.tklabels[symbol][label_name]["textvariable"] = info[j]
				self.tklabels[symbol][label_name]["state"] = "disabled"

				#self.tklabels[symbol][label_name] =tk.Entry(self.deployment_frame ,textvariable=info[j],width=self.width[j],state="disabled")	
			else:
				if str(type(info[j]))=="<class 'tkinter.StringVar'>" or str(type(info[j]))=="<class 'tkinter.DoubleVar'>":
					self.tklabels[symbol][label_name]["textvariable"] = info[j]
					#self.tklabels[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
				else:
					#print(self.tklabels[symbol])
					self.tklabels[symbol][label_name]["text"] = info[j]
					#self.tklabels[symbol][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])
			# try:
			# 	self.label_default_configure(self.tklabels[symbol][label_name])
			# except Exception as e:
			# 	print(e)

			tradingplan.tklabels[label_name] = self.tklabels[symbol][label_name]


		self.label_count +=1

		self.algo_count_number.set(self.label_count-1)
		self.rebind(self.dev_canvas,self.deployment_frame)
		#self.recreate_labels()
		tradingplan.update_displays()

	def create_new_entryB(self,tradingplan):


		infos = {
		SELECTED:tradingplan.tkvars[SELECTED],\
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
		'SzIn':tradingplan.tkvars[SIZE_IN], \
		'Position':tradingplan.tkvars[POSITION], \
		'Stop':tradingplan.tkvars[STOP_LEVEL],\
		'AvgPx':tradingplan.tkvars[AVERAGE_PRICE], \
		PXT1: tradingplan.tkvars[PXT1], \
		PXT2:tradingplan.tkvars[PXT2], \
		PXT3:tradingplan.tkvars[PXT3], \
		UNREAL_PSHR:tradingplan.tkvars[UNREAL_PSHR], \
		UNREAL:tradingplan.tkvars[UNREAL], \
		REALIZED:tradingplan.tkvars[REALIZED], \
		TOTAL_REALIZED:tradingplan.tkvars[TOTAL_REALIZED], \
		'flatten':"", \
		'log':""}


		#link the global variable 
		tradingplan.tkvars[RISKTIMER] = self.risk_timer 


		l = self.label_count

		info = list(infos.values())
		labels = list(infos.keys())
		symbol = info[1]
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

				info[j].trace('w',  lambda *_, symbol=symbol,plan=info[j],tgt_share=tradingplan.tkvars[INPUT_TARGET_SHARE],rsk_share=tradingplan.tkvars[RISK_PER_SHARE]: self.management_plan_checking(symbol,plan,tgt_share,rsk_share))
		
				self.tklabels[symbol][label_name] =tk.OptionMenu(self.deployment_frame, info[j], *sorted(self.management_plan_options))

			elif label_name =="AR" :
				self.tklabels[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j],width=2,command=tradingplan.AR_toggle)
			elif label_name =="Reload" or label_name==SELECTED:
				self.tklabels[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j],width=2)

			elif label_name =="MIND":
				self.tklabels[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
			elif label_name =="Stop":
				self.tklabels[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command= lambda tp=tradingplan:adjust_stop(tp))


			elif label_name ==RISK_RATIO:
				self.tklabels[symbol][RISK_PER_SHARE]=tk.Entry(self.deployment_frame ,textvariable=tradingplan.tkvars[RISK_PER_SHARE],width=self.width[j])
				tradingplan.tklabels[RISK_PER_SHARE] = self.tklabels[symbol][RISK_PER_SHARE]
				tradingplan.tklabels[RISK_PER_SHARE].grid(row= l+2, column=j,padx=0)

				self.tklabels[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])

			elif label_name =='SzIn':
				self.tklabels[symbol][TARGET_SHARE]=tk.Entry(self.deployment_frame ,textvariable=tradingplan.tkvars[INPUT_TARGET_SHARE],width=self.width[j])
				tradingplan.tklabels[TARGET_SHARE] = self.tklabels[symbol][TARGET_SHARE]
				tradingplan.tklabels[TARGET_SHARE].grid(row= l+2, column=j,padx=0)

				self.tklabels[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])

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
		#self.recreate_labels()
		tradingplan.update_displays()

	def create_new_entry_systemB(self,tradingplan):


		infos = {
		SELECTED:tradingplan.tkvars[SELECTED],\
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
		'SzIn':tradingplan.tkvars[SIZE_IN], \
		'Position':tradingplan.tkvars[POSITION], \
		'Stop':tradingplan.tkvars[STOP_LEVEL],\
		'AvgPx':tradingplan.tkvars[AVERAGE_PRICE], \
		PXT1: tradingplan.tkvars[PXT1], \
		PXT2:tradingplan.tkvars[PXT2], \
		PXT3:tradingplan.tkvars[PXT3], \
		UNREAL_PSHR:tradingplan.tkvars[UNREAL_PSHR], \
		UNREAL:tradingplan.tkvars[UNREAL], \
		REALIZED:tradingplan.tkvars[REALIZED], \
		TOTAL_REALIZED:tradingplan.tkvars[TOTAL_REALIZED], \
		'flatten':"", \
		'log':""}


		#link the global variable 
		tradingplan.tkvars[RISKTIMER] = self.risk_timer 


		l = self.label_count

		info = list(infos.values())
		labels = list(infos.keys())
		symbol = info[1]
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

			elif label_name =="AR" :
				self.tklabels[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j],width=2,command=tradingplan.AR_toggle)
			elif label_name =="Reload" or label_name==SELECTED:
				self.tklabels[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j],width=2)

			elif label_name =="MIND":
				self.tklabels[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
			elif label_name =="Stop":
				self.tklabels[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command= lambda tp=tradingplan:adjust_stop(tp))


			elif label_name ==RISK_RATIO:
				self.tklabels[symbol][RISK_PER_SHARE]=tk.Entry(self.deployment_frame ,textvariable=tradingplan.tkvars[RISK_PER_SHARE],width=self.width[j])
				tradingplan.tklabels[RISK_PER_SHARE] = self.tklabels[symbol][RISK_PER_SHARE]
				tradingplan.tklabels[RISK_PER_SHARE].grid(row= l+2, column=j,padx=0)

				self.tklabels[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])

			elif label_name =='SzIn':
				self.tklabels[symbol][TARGET_SHARE]=tk.Entry(self.deployment_frame ,textvariable=tradingplan.tkvars[INPUT_TARGET_SHARE],width=self.width[j])
				tradingplan.tklabels[TARGET_SHARE] = self.tklabels[symbol][TARGET_SHARE]
				tradingplan.tklabels[TARGET_SHARE].grid(row= l+2, column=j,padx=0)

				self.tklabels[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])

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
		#self.recreate_labels()
		tradingplan.update_displays()

	def management_plan_checking(self,symbol,plan,target_share,risk_per_share):

		if plan.get()==ANCARTMETHOD:
			self.tklabels[symbol][RISK_RATIO].grid_remove()
			self.tklabels[symbol]['SzIn'].grid_remove()
			target_share.set(100)
			risk_per_share.set(0.5)
		else:
			self.tklabels[symbol][RISK_RATIO].grid()
			self.tklabels[symbol]['SzIn'].grid()
			target_share.set(0)


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


			self.label_default_configure(self.tklabels[symbol][label_name])

			self.tklabels[symbol][label_name].grid(row= l+2, column=j,padx=0)

			#else: #command = lambda s=symbol: self.delete_symbol_reg_list(s))

		j+=1
		flatten=tk.Button(self.deployment_frame ,text="flatten",width=self.width[j],command= lambda k=i:self.flatten_symbol(k,symbol,status))
		self.label_default_configure(flatten)
		flatten.grid(row= l+2, column=j,padx=0)

		self.label_count +=1

		self.rebind(self.dev_canvas,self.deployment_frame)
	

class adjust_stop:
	def __init__(self,tp):

		
		pos=tp.tkvars[POSITION]
		if pos.get()!="":
			self.symbol = tp.symbol_name
			self.tp = tp
			self.stopvalue = self.tp.data[STOP_LEVEL]
			self.stopvaluetk = self.tp.tkvars[STOP_LEVEL]
			self.root = tk.Toplevel(width=300,height=200)
			self.root.title(self.symbol+" Stop Adjustment")
			#self.label=ttk.LabelFrame(self.root).place(x=0,y=0,relheight=1,relwidth=1)
			#		self.deployment_panel = ttk.LabelFrame(self.root,text="Algo deployment") 
			ttk.Label(self.root, text="Current Stop: "+str(self.stopvalue),font=("Arial", 14)).place(x=40,y=15,height=35,width=200)#.grid(sticky="w",column=1,row=1,padx=10)
			ttk.Label(self.root, text="New Stop:",font=("Arial", 14)).place(x=40,y=45,height=35,width=100)#.grid(sticky="w",column=1,row=2,padx=10)

			self.new_stop = tk.DoubleVar(value=self.stopvalue)
			self.input=tk.Entry(self.root,textvariable=self.new_stop,width=15,font=("Arial", 14))

			self.input.place(x=150,y=45,height=35,width=80)
			tk.Button(self.root ,text="Confirm",width=65,command=self.confirm,font=("Arial", 14)).place(x=40,y=120,height=35,width=100)
			
			tk.Button(self.root ,text="Cancel",width=65,command=self.cancel,font=("Arial", 14)).place(x=150,y=120,height=35,width=100)


	def confirm(self):

		try:
			old = self.stopvalue
			val = float(self.new_stop.get())


			self.tp.data[STOP_LEVEL] = val
			self.stopvaluetk.set(val) 
			self.tp.adjusting_risk()
			self.tp.update_displays()
			log_print(self.symbol,"stop adjusted from",old,"to",val)
			self.root.destroy()
			# if abs(val-self.stopvalue)/val <0.02:

			# else:
			# 	self.input["background"] = "red"
		except Exception as e:
			print(e)
			self.input["background"] = "red"
			return False
		

	def cancel(self):
		self.root.destroy()

if __name__ == '__main__':

	root = tk.Tk() 
	root.title("GoodTrade Algo Manager v2") 
	#root.geometry("1920x1000")
	#UI(root)
	# root.minsize(1600, 1000)
	# root.maxsize(1800, 1200)
	root.mainloop()