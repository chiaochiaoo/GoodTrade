from pannel import *
from constant import *
from Util_functions import *

class UI(pannel):
	def __init__(self,root,manager=None,receiving_signals=None,cmd_text=None):

		self.root = root


		self.manager = manager


		self.receiving_signals = receiving_signals
		self.command_text = cmd_text

		self.tk_strings=["algo_status","realized","shares","unrealized","unrealized_pshr","average_price"]
		self.tk_labels=[SYMBOL,STATUS,MIND, 'EntryPlan', 'EntryType', 'ETmr', 'Management','Reload', 'AR', 'Sup', 'Res', 'Act/Est R', 'Position', 'AvgPx', 'SzIn', 'UPshr', 'U', 'R', 'TR', 'flatten', 'log']

		self.tk_labels_single = {}

		self.tk_labels_pair = {}


		self.single_label_count = 1

		self.pair_label_count = 1

		self.tklabels_list = []

		self.algo_counts = 0

		self.risk_timer = tk.DoubleVar(value=300)

		self.option_values()

		self.init_pannel()

		self.init_entry_pannel()

	def option_values(self):

		self.entry_type_options = {INSTANT,INCREMENTAL,INCREMENTAL2}

		self.entry_plan_options = {BREAKUP,BREAKDOWN,BREAKFIRST,FREECONTROL,INSTANTLONG,INSTANTSHORT,TARGETLONG,TARGETSHORT}

		self.management_plan_options = {TRENDRIDER,FIBO,EM_STRATEGY,EMASTRAT,ONETOTWORISKREWARD,FULLMANUAL,SEMIMANUAL}#SCALPATRON #THREE_TARGETS,SMARTTRAIL,ANCARTMETHOD,ONETOTWORISKREWARD,ONETOTWORISKREWARDOLD,

	def init_pannel(self):

		"""
						"EntryPlan":11,\
						"EntryType":12,\
						"Timer":5,\
						"Management":14,\
						"Reload":6,\
						"AR":4,\
						"Sup":6,\
						"Res":6,\
		"""
		self.labels = {"":4,\
						"Symbol":8,\
						"Status":10,\
						"MIND":20,\


						"Act/Est R":8,\
						"SzIn":6,\
						"Position":6,\
						"Stop":6,\
						"AvgPx":10,\
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

		self.stats = ttk.LabelFrame(self.root,text="Statistics") 
		self.stats.place(x=10,y=160,height=260,width=210)

		self.active_trade = tk.IntVar()
		self.active_trade_max = tk.IntVar()

		self.total_u = tk.DoubleVar()
		self.total_u_max = tk.DoubleVar()
		self.total_u_min = tk.DoubleVar()
		self.total_r = tk.DoubleVar()
		self.total_r_max = tk.DoubleVar()
		self.total_r_min = tk.DoubleVar()

		self.max_risk = tk.DoubleVar()

		self.passive_aggregation = tk.BooleanVar()
		self.current_total_risk = tk.DoubleVar()
		self.current_downside = tk.DoubleVar()

		self.net = tk.DoubleVar()
		self.net_max = tk.DoubleVar()
		self.net_min = tk.DoubleVar()

		self.current_upside = tk.DoubleVar()

		self.deltaspx = tk.DoubleVar()
		self.longexp = tk.DoubleVar()
		self.shortexp = tk.DoubleVar()
		self.overallexp = tk.DoubleVar()


		self.current_downside_max = tk.DoubleVar()
		self.u_winning = tk.DoubleVar()
		self.u_winning_min = tk.DoubleVar()
		self.u_winning_max = tk.DoubleVar()

		self.u_losing = tk.DoubleVar()
		self.u_losing_min = tk.DoubleVar()
		self.u_losing_max = tk.DoubleVar()

		self.x1 = ttk.Label(self.stats, text="Cur:")
		self.x1.grid(sticky="w",column=2,row=1,padx=3)
		self.x2 = ttk.Label(self.stats, text="Min:")
		self.x2.grid(sticky="w",column=3,row=1,padx=3)
		self.x3 = ttk.Label(self.stats, text="Max:")
		self.x3.grid(sticky="w",column=4,row=1,padx=3)

		row = 2 
		self.t1 = ttk.Label(self.stats, text="Activated:")
		self.t1.grid(sticky="w",column=1,row=row,padx=10)
		self.t1_ = ttk.Label(self.stats, textvariable=self.active_trade)
		self.t1_.grid(sticky="w",column=2,row=row)

		ttk.Label(self.stats, textvariable=self.active_trade_max).grid(sticky="w",column=4,row=row)

		row +=1 
		self.t2 = ttk.Label(self.stats, text="Total Net:")
		self.t2.grid(sticky="w",column=1,row=row,padx=10)
		self.t2_ = ttk.Label(self.stats, textvariable=self.net)
		self.t2_.grid(sticky="w",column=2,row=row)

		ttk.Label(self.stats, textvariable=self.net_min).grid(sticky="w",column=3,row=row)
		ttk.Label(self.stats, textvariable=self.net_max).grid(sticky="w",column=4,row=row)


		row +=1 
		self.t2 = ttk.Label(self.stats, text="Total U:")
		self.t2.grid(sticky="w",column=1,row=row,padx=10)
		self.t2_ = ttk.Label(self.stats, textvariable=self.total_u)
		self.t2_.grid(sticky="w",column=2,row=row)

		self.t2_ = ttk.Label(self.stats, textvariable=self.total_u_min)
		self.t2_.grid(sticky="w",column=3,row=row)

		self.t2_ = ttk.Label(self.stats, textvariable=self.total_u_max)
		self.t2_.grid(sticky="w",column=4,row=row)


		# row +=1 
		# self.t2 = ttk.Label(self.stats, text="Winnig:")
		# self.t2.grid(sticky="w",column=1,row=row,padx=10)
		# self.t2_ = ttk.Label(self.stats, textvariable=self.u_winning)
		# self.t2_.grid(sticky="w",column=2,row=row)



		# self.t2_ = ttk.Label(self.stats, textvariable=self.u_winning_max)
		# self.t2_.grid(sticky="w",column=4,row=row)


		# row +=1 
		# self.t2 = ttk.Label(self.stats, text="Losing:")
		# self.t2.grid(sticky="w",column=1,row=row,padx=10)
		# self.t2_ = ttk.Label(self.stats, textvariable=self.u_losing)
		# self.t2_.grid(sticky="w",column=2,row=row)


		# self.t2_ = ttk.Label(self.stats, textvariable=self.u_losing_max)
		# self.t2_.grid(sticky="w",column=4,row=row)



		row +=1 
		self.t6 = ttk.Label(self.stats, text="Total Risk:")
		self.t6.grid(sticky="w",column=1,row=row,padx=10)
		self.t6_ = ttk.Label(self.stats, textvariable=self.current_total_risk)
		self.t6_.grid(sticky="w",column=2,row=row)
		self.t6_ = ttk.Label(self.stats, textvariable=self.max_risk)
		self.t6_.grid(sticky="w",column=4,row=row)

		row +=1 
		self.t6 = ttk.Label(self.stats, text="Delta SPX:")
		self.t6.grid(sticky="w",column=1,row=row,padx=10)
		self.t6_ = ttk.Label(self.stats, textvariable=self.deltaspx)
		self.t6_.grid(sticky="w",column=2,row=row)
		# self.t6_ = ttk.Label(self.stats, textvariable=self.max_risk)
		# self.t6_.grid(sticky="w",column=4,row=row)
		row +=1 
		self.t6 = ttk.Label(self.stats, text="LONG EXP:")
		self.t6.grid(sticky="w",column=1,row=row,padx=10)
		self.t6_ = ttk.Label(self.stats, textvariable=self.longexp)
		self.t6_.grid(sticky="w",column=2,row=row)

		row +=1 
		self.t6 = ttk.Label(self.stats, text="SHORT EXP:")
		self.t6.grid(sticky="w",column=1,row=row,padx=10)
		self.t6_ = ttk.Label(self.stats, textvariable=self.shortexp)
		self.t6_.grid(sticky="w",column=2,row=row)

		row +=1 
		self.t6 = ttk.Label(self.stats, text="OVERALL.EXP:")
		self.t6.grid(sticky="w",column=1,row=row,padx=10)
		self.t6_ = ttk.Label(self.stats, textvariable=self.overallexp)
		self.t6_.grid(sticky="w",column=2,row=row)

		# row +=1 
		# self.t6 = ttk.Label(self.stats, text="Locked in:")
		# self.t6.grid(sticky="w",column=1,row=row,padx=10)
		# self.t6_ = ttk.Label(self.stats, textvariable=self.current_upside)
		# self.t6_.grid(sticky="w",column=2,row=row)




		# self.config = ttk.LabelFrame(self.root,text="Config") 
		# self.config.place(x=10,y=360,height=260,width=210)

		self.cmd = ttk.LabelFrame(self.root,text="Command") 
		self.cmd.place(x=10,y=360,height=500,width=210)


		#self.init_config_pannel()
		self.init_command()
		# self.log_panel = ttk.LabelFrame(self.root,text="Events") 
		# self.log_panel.place(x=10,y=300,relheight=0.5,width=210)

		# self.stats_panel = ttk.LabelFrame(self.root,text="Algo Stats") 
		# self.stats_panel.place(x=210,y=10,height=50,width=1650)

		self.deployment_panel = ttk.LabelFrame(self.root,text="Single Algo") 
		self.deployment_panel.place(x=210,rely=0.01,relheight=0.65,width=1200)


		self.pair_panel = ttk.LabelFrame(self.root,text="Pairs Algo") 
		self.pair_panel.place(x=210,rely=0.66,relheight=0.30,width=1200)
		###########################################################################################################

		self.dev_canvas = tk.Canvas(self.deployment_panel)
		self.dev_canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)

		self.scroll = tk.Scrollbar(self.deployment_panel)
		self.scroll.config(orient=tk.VERTICAL, command=self.dev_canvas.yview)
		self.scroll.pack(side=tk.RIGHT,fill="y")
		self.dev_canvas.configure(yscrollcommand=self.scroll.set)

		self.deployment_frame = tk.Frame(self.dev_canvas)
		self.deployment_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)
		self.dev_canvas.create_window(0, 0, window=self.deployment_frame, anchor=tk.NW)

		##########################################################################################################
		self.pair_canvas = tk.Canvas(self.pair_panel)
		self.pair_canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)

		self.scroll = tk.Scrollbar(self.pair_panel)
		self.scroll.config(orient=tk.VERTICAL, command=self.pair_canvas.yview)
		self.scroll.pack(side=tk.RIGHT,fill="y")
		self.pair_canvas.configure(yscrollcommand=self.scroll.set)

		self.pair_frame = tk.Frame(self.pair_canvas)
		self.pair_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)
		self.pair_canvas.create_window(0, 0, window=self.pair_frame, anchor=tk.NW)

		#self.create_example_trade()

		self.rebind(self.dev_canvas,self.deployment_frame)

		self.rebind(self.pair_canvas,self.pair_frame)

		self.recreate_labels()

	def init_HQ_pannel(self):


		self.main_app_status = tk.StringVar()
		self.main_app_status.set("")

		self.ppro_status = tk.StringVar()
		self.ppro_status.set("")

		self.ppro_out_status = tk.StringVar()
		self.ppro_out_status.set("")

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

		self.ppro = ttk.Label(self.comms, text="Ppro in:")
		self.ppro.grid(sticky="w",column=1,row=2,padx=10)
		self.ppro_status_ = ttk.Label(self.comms, textvariable=self.ppro_status)
		self.ppro_status_.grid(sticky="w",column=2,row=2)

		self.ppro = ttk.Label(self.comms, text="Ppro out:")
		self.ppro.grid(sticky="w",column=1,row=3,padx=10)
		self.ppro_status_out = ttk.Label(self.comms, textvariable=self.ppro_out_status)
		self.ppro_status_out.grid(sticky="w",column=2,row=3)


		self.al = ttk.Label(self.comms, text="Algo count::")
		self.al.grid(sticky="w",column=1,row=4,padx=10)
		self.algo_count_ = ttk.Label(self.comms,  textvariable=self.algo_count_number)
		self.algo_count_.grid(sticky="w",column=2,row=4,padx=10)

		self.timerc = ttk.Label(self.comms, text="Deploy in:")
		self.timerc.grid(sticky="w",column=1,row=5,padx=10)
		self.timersx = ttk.Label(self.comms,  textvariable=self.algo_timer_string)
		self.timersx.grid(sticky="w",column=2,row=5,padx=10)

		self.timerc = ttk.Label(self.comms, text="Close in:")
		self.timerc.grid(sticky="w",column=1,row=6,padx=10)
		self.timersx = ttk.Label(self.comms,  textvariable=self.algo_timer_close_string)
		self.timersx.grid(sticky="w",column=2,row=6,padx=10)

		ttk.Label(self.comms, text="Risk timer:").grid(sticky="w",column=1,row=7,padx=10)
		tk.Entry(self.comms,textvariable=self.risk_timer,width=7).grid(sticky="w",column=2,row=7,padx=10)
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

		


		ttk.Label(self.cmd, text="Receiving Algo:").grid(sticky="w",column=1,row=1)
		ttk.Checkbutton(self.cmd, variable=self.receiving_signals).grid(sticky="w",column=2,row=1)

		#self.receiving_signals


		row = 2

		self.algo_deploy = ttk.Button(self.cmd, text="Deploy all algo",command=self.manager.deploy_all)#,command=self.deploy_all_stoporders)
		self.algo_deploy.grid(sticky="w",column=1,row=row)

		self.algo_pend = ttk.Button(self.cmd, text="Withdraw all algo",command=self.manager.withdraw_all)#,command=self.cancel_all_stoporders)
		self.algo_pend.grid(sticky="w",column=2,row=row)

		row +=1 

		self.flatten = ttk.Button(self.cmd, text="Flatten all algo",command=self.manager.flatten_all)
		self.flatten.grid(sticky="w",column=1,row=row)

		# self.algo_cancel = ttk.Button(self.cmd, text="Cancel all algo",command=self.manager.cancel_all)
		# self.algo_cancel.grid(sticky="w",column=2,row=row)

		row +=1 

		self.flatten = ttk.Button(self.cmd, text="Weekly Report",command=graphweekly)
		self.flatten.grid(sticky="w",column=1,row=row)

		self.algo_cancel = ttk.Button(self.cmd, text="Daily Report" ) #command=self.manager.import_algos
		self.algo_cancel.grid(sticky="w",column=2,row=row)

		row=6

		ttk.Label(self.cmd, text=" ").grid(sticky="w",column=1,row=row)
		row+=2



		row+=1
		#self.command_text = tk.StringVar(value="Status:")
		ttk.Label(self.cmd, textvariable=self.command_text).grid(sticky="w",column=1,row=row,columnspan =2)


		row+=1

		ttk.Label(self.cmd, text="Passive Fills:").grid(sticky="w",column=1,row=row)
		ttk.Checkbutton(self.cmd, variable=self.passive_aggregation).grid(sticky="w",column=2,row=row)


		row+=1
		ttk.Button(self.cmd, text="Flatten LONGS",command= lambda action=MINUS,percent=1:self.manager.trades_aggregation(LONG,action,percent,True,self.passive_aggregation)).grid(sticky="w",column=1,row=row)
		ttk.Button(self.cmd, text="Flatten SHORTS",command= lambda action=MINUS,percent=1:self.manager.trades_aggregation(SHORT,action,percent,False,self.passive_aggregation)).grid(sticky="w",column=2,row=row)

		row+=1
		ttk.Label(self.cmd, text="All Active Winnings:").grid(sticky="w",column=1,row=row)

		row+=1
		ttk.Button(self.cmd, text="Add 10%",command= lambda action=ADD,percent=0.1:self.manager.trades_aggregation(None,action,percent,True,self.passive_aggregation)).grid(sticky="w",column=1,row=row)
		ttk.Button(self.cmd, text="Add 25%",command= lambda action=ADD,percent=0.25:self.manager.trades_aggregation(None,action,percent,True,self.passive_aggregation)).grid(sticky="w",column=2,row=row)

		row+=1
		ttk.Button(self.cmd, text="Minus 10%",command= lambda action=MINUS,percent=0.1:self.manager.trades_aggregation(None,action,percent,True,self.passive_aggregation)).grid(sticky="w",column=1,row=row)
		ttk.Button(self.cmd, text="Minus 25%",command= lambda action=MINUS,percent=0.25:self.manager.trades_aggregation(None,action,percent,True,self.passive_aggregation)).grid(sticky="w",column=2,row=row)


		ttk.Label(self.cmd, text=" ").grid(sticky="w",column=1,row=row)
		row+=1
		ttk.Label(self.cmd, text="All Active Longs:").grid(sticky="w",column=1,row=row)

		row+=1
		ttk.Button(self.cmd, text="Add 10%",command= lambda side=LONG,action=ADD,percent=0.1:self.manager.trades_aggregation(side,action,percent,False,self.passive_aggregation)).grid(sticky="w",column=1,row=row)
		ttk.Button(self.cmd, text="Add 25%",command= lambda side=LONG,action=ADD,percent=0.25:self.manager.trades_aggregation(side,action,percent,False,self.passive_aggregation)).grid(sticky="w",column=2,row=row)

		row+=1
		ttk.Button(self.cmd, text="Minus 10%",command= lambda side=LONG,action=MINUS,percent=0.1:self.manager.trades_aggregation(side,action,percent,False,self.passive_aggregation)).grid(sticky="w",column=1,row=row)
		ttk.Button(self.cmd, text="Minus 25%",command= lambda side=LONG,action=MINUS,percent=0.25:self.manager.trades_aggregation(side,action,percent,False,self.passive_aggregation)).grid(sticky="w",column=2,row=row)

		row+=1
		ttk.Label(self.cmd, text=" ").grid(sticky="w",column=1,row=row)
		row+=1
		ttk.Label(self.cmd, text="All Active Shorts:").grid(sticky="w",column=1,row=row)

		row+=1
		ttk.Button(self.cmd, text="Add 10%",command= lambda side=SHORT,action=ADD,percent=0.1:self.manager.trades_aggregation(side,action,percent,False,self.passive_aggregation)).grid(sticky="w",column=1,row=row)
		ttk.Button(self.cmd, text="Add 25%",command= lambda side=SHORT,action=ADD,percent=0.25:self.manager.trades_aggregation(side,action,percent,False,self.passive_aggregation)).grid(sticky="w",column=2,row=row)

		row+=1
		ttk.Button(self.cmd, text="Minus 10%",command= lambda side=SHORT,action=MINUS,percent=0.1:self.manager.trades_aggregation(side,action,percent,False,self.passive_aggregation)).grid(sticky="w",column=1,row=row)
		ttk.Button(self.cmd, text="Minus 25%",command= lambda side=SHORT,action=MINUS,percent=0.25:self.manager.trades_aggregation(side,action,percent,False,self.passive_aggregation)).grid(sticky="w",column=2,row=row)


		#iterate all the trading plans.
		#if position ="LONG"
		#if shares>= 25.
		#calculate the shares to be taken off. 

	def init_entry_pannel(self):


		"""
				ENTRYPLAN:"", \
		ENTYPE:"", \
		TIMER:"", \
		MANAGEMENTPLAN:"", \


		"Reload":"", \
		'AR':"", \
		SUPPORT:"", \
		RESISTENCE:"", \
		"""
		infos = {
		SELECTED:"",\
		'Symbol':"", \
		STATUS:"",\
		MIND:"",\


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

		for l in range(51):
			self.tk_labels_single[l]={}
			for j in range(len(info)):
				#"symbol","algo_status","description","break_at","position","act_r/est_r","stoplevel","average_price","shares","pxtgt1","pxtgt1","pxtgt1","unrealized_pshr","unrealized","realized"
				label_name = labels[j]

				if label_name == "Symbol":
					self.tk_labels_single[l][label_name] = tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])
				elif label_name == STATUS:
					self.tk_labels_single[l][label_name] = tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

				elif label_name ==TIMER:
					self.tk_labels_single[l][label_name] = tk.Entry(self.deployment_frame,text=info[j],width=self.width[j])

				elif label_name =="AR" :
					self.tk_labels_single[l][label_name] = tk.Checkbutton(self.deployment_frame,width=2,)
				elif label_name =="Reload" or label_name==SELECTED:
					self.tk_labels_single[l][label_name] = tk.Checkbutton(self.deployment_frame,width=2)

				elif label_name =="MIND":
					self.tk_labels_single[l][label_name] =tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])
				elif label_name =="Stop":
					self.tk_labels_single[l][label_name] =tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

				elif label_name ==RISK_RATIO:
					self.tk_labels_single[l][RISK_PER_SHARE]=tk.Entry(self.deployment_frame ,text=info[j],width=self.width[j])

					self.tk_labels_single[l][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

				elif label_name =='SzIn':
					self.tk_labels_single[l][TARGET_SHARE]=tk.Entry(self.deployment_frame ,text=info[j],width=self.width[j])
	

					self.tk_labels_single[l][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

				elif label_name =="flatten":
					self.tk_labels_single[l][label_name] =tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

				elif label_name == SUPPORT or label_name == RESISTENCE or label_name == "pxtgt1" or label_name == "pxtgt2" or label_name == "pxtgt3":
					self.tk_labels_single[l][label_name] =tk.Entry(self.deployment_frame ,text=info[j],width=self.width[j],state="disabled")	
				else:
					if str(type(info[j]))=="<class 'tkinter.StringVar'>" or str(type(info[j]))=="<class 'tkinter.DoubleVar'>":
						self.tk_labels_single[l][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])
					else:
						#print(self.tk_labels_single[symbol])
						self.tk_labels_single[l][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])
				try:
					self.label_default_configure(self.tk_labels_single[l][label_name])
				except:
					pass

				self.tk_labels_single[l][label_name].grid(row= l+2, column=j,padx=0)

		for l in range(25):

			self.tk_labels_pair[l] = {}

				
			for j in range(len(info)):
				#"symbol","algo_status","description","break_at","position","act_r/est_r","stoplevel","average_price","shares","pxtgt1","pxtgt1","pxtgt1","unrealized_pshr","unrealized","realized"
				label_name = labels[j]

				if label_name == "Symbol":
					self.tk_labels_pair[l][label_name] = tk.Button(self.pair_frame ,text=info[j],width=self.width[j])
				elif label_name == STATUS:
					self.tk_labels_pair[l][label_name] = tk.Button(self.pair_frame ,text=info[j],width=self.width[j])

				elif label_name ==TIMER:
					self.tk_labels_pair[l][label_name] = tk.Entry(self.pair_frame,text=info[j],width=self.width[j])

				elif label_name =="AR" :
					self.tk_labels_pair[l][label_name] = tk.Checkbutton(self.pair_frame,width=2,)
				elif label_name =="Reload" or label_name==SELECTED:
					self.tk_labels_pair[l][label_name] = tk.Checkbutton(self.pair_frame,width=2)

				elif label_name =="MIND":
					self.tk_labels_pair[l][label_name] =tk.Button(self.pair_frame ,text=info[j],width=self.width[j])
				elif label_name =="Stop":
					self.tk_labels_pair[l][label_name] =tk.Button(self.pair_frame ,text=info[j],width=self.width[j])

				elif label_name ==RISK_RATIO:
					self.tk_labels_pair[l][RISK_PER_SHARE]=tk.Entry(self.pair_frame ,text=info[j],width=self.width[j])

					self.tk_labels_pair[l][label_name]=tk.Button(self.pair_frame ,text=info[j],width=self.width[j])

				elif label_name =='SzIn':
					self.tk_labels_pair[l][TARGET_SHARE]=tk.Entry(self.pair_frame ,text=info[j],width=self.width[j])
	

					self.tk_labels_pair[l][label_name]=tk.Button(self.pair_frame ,text=info[j],width=self.width[j])

				elif label_name =="flatten":
					self.tk_labels_pair[l][label_name] =tk.Button(self.pair_frame ,text=info[j],width=self.width[j])

				elif label_name == SUPPORT or label_name == RESISTENCE or label_name == "pxtgt1" or label_name == "pxtgt2" or label_name == "pxtgt3":
					self.tk_labels_pair[l][label_name] =tk.Entry(self.pair_frame ,text=info[j],width=self.width[j],state="disabled")	
				else:
					if str(type(info[j]))=="<class 'tkinter.StringVar'>" or str(type(info[j]))=="<class 'tkinter.DoubleVar'>":
						self.tk_labels_pair[l][label_name]=tk.Button(self.pair_frame ,text=info[j],width=self.width[j])
					else:
						#print(self.tk_labels_single[symbol])
						self.tk_labels_pair[l][label_name]=tk.Button(self.pair_frame ,text=info[j],width=self.width[j])
				try:
					self.label_default_configure(self.tk_labels_pair[l][label_name])
				except:
					pass

				self.tk_labels_pair[l][label_name].grid(row= l+2, column=j,padx=0)

		self.rebind(self.dev_canvas,self.deployment_frame)
		self.rebind(self.pair_canvas,self.pair_frame)



	def create_new_single_entry(self,tradingplan,single,row_number):

		if single=="Single":

			if row_number==None:
				l = self.single_label_count
				row_number = l-1 #info[1]
			#self.tk_labels_single[symbol] = {}

			self.create_single_entry(tradingplan, row_number)

			self.single_label_count +=1

			self.rebind(self.dev_canvas,self.deployment_frame)
			#self.recreate_labels()
			tradingplan.update_displays()
		else:

			#print("XXXXXXXXXXXXXXX using row number",row_number,self.pair_label_count)

			if row_number==None:
				# l = self.single_label_count
				# row_number = l-1 #info[1]
				l = self.pair_label_count
				row_number = l-1 #info[1]
			

			#print("XXXXXXXXXXXXXXX using row number",row_number,self.pair_label_count)
			#self.tk_labels_single[symbol] = {}

			self.create_pair_entry(tradingplan, row_number)

			self.pair_label_count +=1

			self.rebind(self.dev_canvas,self.deployment_frame)
			#self.recreate_labels()
			tradingplan.update_displays()

	def create_single_entry(self,tradingplan,symbol):

		"""
		ENTRYPLAN:tradingplan.tkvars[ENTRYPLAN], \
		ENTYPE:tradingplan.tkvars[ENTYPE], \
		TIMER:tradingplan.tkvars[TIMER], \
		MANAGEMENTPLAN:tradingplan.tkvars[MANAGEMENTPLAN], \
		"Reload":tradingplan.tkvars[RELOAD], \
		'AR':tradingplan.tkvars[AUTORANGE], \
		SUPPORT:tradingplan.tkvars[SUPPORT], \
		RESISTENCE:tradingplan.tkvars[RESISTENCE], \
		"""

		self.algo_count_number.set(self.algo_count_number.get()+1)

		infos = {
		SELECTED:tradingplan.tkvars[SELECTED],\
		'Symbol':tradingplan.symbol_name, \
		STATUS:tradingplan.tkvars[STATUS],\
		MIND: tradingplan.tkvars[MIND],\


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


		info = list(infos.values())
		labels = list(infos.keys())	

		for j in range(len(info)):
			#"symbol","algo_status","description","break_at","position","act_r/est_r","stoplevel","average_price","shares","pxtgt1","pxtgt1","pxtgt1","unrealized_pshr","unrealized","realized"
			label_name = labels[j]
			#print(self.tk_labels_single[symbol])
			if label_name == "Symbol":
				self.tk_labels_single[symbol][label_name]["text"] = info[j] #tk.Button(self.deployment_frame ,text=info[j],width=self.width[j],command=tradingplan.deploy)
				self.tk_labels_single[symbol][label_name]["command"] = tradingplan.deploy
			elif label_name == STATUS:
				self.tk_labels_single[symbol][label_name]["textvariable"] = info[j] 
				self.tk_labels_single[symbol][label_name]["command"] = tradingplan.cancle_deployment
				#= tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command=tradingplan.cancle_deployment)

			elif label_name ==TIMER:
				self.tk_labels_single[symbol][label_name]["textvariable"] = info[j] 
				#self.tk_labels_single[symbol][label_name] = tk.Entry(self.deployment_frame,textvariable=info[j],width=self.width[j])

			elif label_name =="AR" :
				self.tk_labels_single[symbol][label_name]["variable"] = info[j] 
				self.tk_labels_single[symbol][label_name]["command"] = tradingplan.AR_toggle
				#self.tk_labels_single[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j],width=2,command=tradingplan.AR_toggle)
			elif label_name =="Reload" or label_name==SELECTED:
				self.tk_labels_single[symbol][label_name]["variable"] = info[j]
				#self.tk_labels_single[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j],width=2)
				 
			elif label_name =="MIND":
				self.tk_labels_single[symbol][label_name]["textvariable"] = info[j]
				#self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
			elif label_name =="Stop":
				self.tk_labels_single[symbol][label_name]["textvariable"] = info[j]
				self.tk_labels_single[symbol][label_name]["command"] = lambda tp=tradingplan:adjust_stop(tp)

				#self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command= lambda tp=tradingplan:adjust_stop(tp))


			elif label_name ==RISK_RATIO:
				self.tk_labels_single[symbol][label_name]["textvariable"] = info[j]

				tradingplan.tklabels[RISK_PER_SHARE] = self.tk_labels_single[symbol][RISK_PER_SHARE]

				#self.tk_labels_single[symbol][RISK_PER_SHARE]=tk.Entry(self.deployment_frame ,textvariable=tradingplan.tkvars[RISK_PER_SHARE],width=self.width[j])
				#tradingplan.tklabels[RISK_PER_SHARE].grid(row= l+2, column=j,padx=0)

				#self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])

			elif label_name =='SzIn':
				# self.tk_labels_single[symbol][TARGET_SHARE]=tk.Entry(self.deployment_frame ,textvariable=tradingplan.tkvars[INPUT_TARGET_SHARE],width=self.width[j])
				# tradingplan.tklabels[TARGET_SHARE] = self.tk_labels_single[symbol][TARGET_SHARE]
				# tradingplan.tklabels[TARGET_SHARE].grid(row= l+2, column=j,padx=0)
				self.tk_labels_single[symbol][label_name]["textvariable"] = info[j]
				#self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])

			elif label_name =="flatten":
				self.tk_labels_single[symbol][label_name]["command"] = tradingplan.flatten_cmd
				#self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command=tradingplan.flatten_cmd)

			elif label_name == SUPPORT or label_name == RESISTENCE or label_name == "pxtgt1" or label_name == "pxtgt2" or label_name == "pxtgt3":
				self.tk_labels_single[symbol][label_name]["textvariable"] = info[j]
				self.tk_labels_single[symbol][label_name]["state"] = "disabled"

				#self.tk_labels_single[symbol][label_name] =tk.Entry(self.deployment_frame ,textvariable=info[j],width=self.width[j],state="disabled")	
			else:
				if str(type(info[j]))=="<class 'tkinter.StringVar'>" or str(type(info[j]))=="<class 'tkinter.DoubleVar'>":
					self.tk_labels_single[symbol][label_name]["textvariable"] = info[j]
					#self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
				else:
					#print(self.tk_labels_single[symbol])
					self.tk_labels_single[symbol][label_name]["text"] = info[j]
					#self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])
			# try:
			# 	self.label_default_configure(self.tk_labels_single[symbol][label_name])
			# except Exception as e:
			# 	print(e)

			tradingplan.tklabels[label_name] = self.tk_labels_single[symbol][label_name]


		tradingplan.algo_ui_id = symbol


	def create_pair_entry(self,tradingplan,symbol):

		self.algo_count_number.set(self.algo_count_number.get()+1)

		infos = {
		SELECTED:tradingplan.tkvars[SELECTED],\
		'Symbol':tradingplan.symbol_name, \
		STATUS:tradingplan.tkvars[STATUS],\
		MIND: tradingplan.tkvars[MIND],\

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


		info = list(infos.values())
		labels = list(infos.keys())	

		for j in range(len(info)):
			#"symbol","algo_status","description","break_at","position","act_r/est_r","stoplevel","average_price","shares","pxtgt1","pxtgt1","pxtgt1","unrealized_pshr","unrealized","realized"
			label_name = labels[j]
			#print(self.tk_labels_single[symbol])
			if label_name == "Symbol":
				self.tk_labels_pair[symbol][label_name]["text"] = info[j] #tk.Button(self.deployment_frame ,text=info[j],width=self.width[j],command=tradingplan.deploy)
				self.tk_labels_pair[symbol][label_name]["command"] = tradingplan.deploy
			elif label_name == STATUS:
				self.tk_labels_pair[symbol][label_name]["textvariable"] = info[j] 
				self.tk_labels_pair[symbol][label_name]["command"] = tradingplan.cancle_deployment
				#= tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command=tradingplan.cancle_deployment)

			elif label_name ==TIMER:
				self.tk_labels_pair[symbol][label_name]["textvariable"] = info[j] 
				#self.tk_labels_single[symbol][label_name] = tk.Entry(self.deployment_frame,textvariable=info[j],width=self.width[j])

			elif label_name =="AR" :
				self.tk_labels_pair[symbol][label_name]["variable"] = info[j] 
				self.tk_labels_pair[symbol][label_name]["command"] = tradingplan.AR_toggle
				#self.tk_labels_single[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j],width=2,command=tradingplan.AR_toggle)
			elif label_name =="Reload" or label_name==SELECTED:
				self.tk_labels_pair[symbol][label_name]["variable"] = info[j]
				#self.tk_labels_single[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j],width=2)
				 
			elif label_name =="MIND":
				self.tk_labels_pair[symbol][label_name]["textvariable"] = info[j]
				#self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
			elif label_name =="Stop":
				self.tk_labels_pair[symbol][label_name]["textvariable"] = info[j]
				self.tk_labels_pair[symbol][label_name]["command"] = lambda tp=tradingplan:adjust_stop(tp)

				#self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command= lambda tp=tradingplan:adjust_stop(tp))


			elif label_name ==RISK_RATIO:
				self.tk_labels_pair[symbol][label_name]["textvariable"] = info[j]

				tradingplan.tklabels[RISK_PER_SHARE] = self.tk_labels_pair[symbol][RISK_PER_SHARE]

				#self.tk_labels_single[symbol][RISK_PER_SHARE]=tk.Entry(self.deployment_frame ,textvariable=tradingplan.tkvars[RISK_PER_SHARE],width=self.width[j])
				#tradingplan.tklabels[RISK_PER_SHARE].grid(row= l+2, column=j,padx=0)

				#self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])

			elif label_name =='SzIn':
				# self.tk_labels_single[symbol][TARGET_SHARE]=tk.Entry(self.deployment_frame ,textvariable=tradingplan.tkvars[INPUT_TARGET_SHARE],width=self.width[j])
				# tradingplan.tklabels[TARGET_SHARE] = self.tk_labels_single[symbol][TARGET_SHARE]
				# tradingplan.tklabels[TARGET_SHARE].grid(row= l+2, column=j,padx=0)
				self.tk_labels_pair[symbol][label_name]["textvariable"] = info[j]
				#self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])

			elif label_name =="flatten":
				self.tk_labels_pair[symbol][label_name]["command"] = tradingplan.flatten_cmd
				#self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command=tradingplan.flatten_cmd)

			elif label_name == SUPPORT or label_name == RESISTENCE or label_name == "pxtgt1" or label_name == "pxtgt2" or label_name == "pxtgt3":
				self.tk_labels_pair[symbol][label_name]["textvariable"] = info[j]
				self.tk_labels_pair[symbol][label_name]["state"] = "disabled"

				#self.tk_labels_single[symbol][label_name] =tk.Entry(self.deployment_frame ,textvariable=info[j],width=self.width[j],state="disabled")	
			else:
				if str(type(info[j]))=="<class 'tkinter.StringVar'>" or str(type(info[j]))=="<class 'tkinter.DoubleVar'>":
					self.tk_labels_pair[symbol][label_name]["textvariable"] = info[j]
					#self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
				else:
					#print(self.tk_labels_single[symbol])
					self.tk_labels_pair[symbol][label_name]["text"] = info[j]
					#self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])
			# try:
			# 	self.label_default_configure(self.tk_labels_single[symbol][label_name])
			# except Exception as e:
			# 	print(e)

			tradingplan.tklabels[label_name] = self.tk_labels_pair[symbol][label_name]


		tradingplan.algo_ui_id = symbol



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


		l = self.single_label_count

		info = list(infos.values())
		labels = list(infos.keys())
		symbol = info[1]
		self.tk_labels_single[symbol] = {}
		for j in range(len(info)):
			#"symbol","algo_status","description","break_at","position","act_r/est_r","stoplevel","average_price","shares","pxtgt1","pxtgt1","pxtgt1","unrealized_pshr","unrealized","realized"
			label_name = labels[j]

			if label_name == "Symbol":
				self.tk_labels_single[symbol][label_name] = tk.Button(self.deployment_frame ,text=info[j],width=self.width[j],command=tradingplan.deploy)
			elif label_name == STATUS:
				self.tk_labels_single[symbol][label_name] = tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command=tradingplan.cancle_deployment)

			elif label_name ==TIMER:
				self.tk_labels_single[symbol][label_name] = tk.Entry(self.deployment_frame,textvariable=info[j],width=self.width[j])

			elif label_name ==ENTRYPLAN:
				self.tk_labels_single[symbol][label_name] = tk.OptionMenu(self.deployment_frame, info[j], *sorted(self.entry_plan_options))

			elif label_name ==ENTYPE:
				self.tk_labels_single[symbol][label_name] = tk.OptionMenu(self.deployment_frame, info[j], *sorted(self.entry_type_options))

			elif label_name ==MANAGEMENTPLAN:

				info[j].trace('w',  lambda *_, symbol=symbol,plan=info[j],tgt_share=tradingplan.tkvars[INPUT_TARGET_SHARE],rsk_share=tradingplan.tkvars[RISK_PER_SHARE]: self.management_plan_checking(symbol,plan,tgt_share,rsk_share))
		
				self.tk_labels_single[symbol][label_name] =tk.OptionMenu(self.deployment_frame, info[j], *sorted(self.management_plan_options))

			elif label_name =="AR" :
				self.tk_labels_single[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j],width=2,command=tradingplan.AR_toggle)
			elif label_name =="Reload" or label_name==SELECTED:
				self.tk_labels_single[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j],width=2)

			elif label_name =="MIND":
				self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
			elif label_name =="Stop":
				self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command= lambda tp=tradingplan:adjust_stop(tp))


			elif label_name ==RISK_RATIO:
				self.tk_labels_single[symbol][RISK_PER_SHARE]=tk.Entry(self.deployment_frame ,textvariable=tradingplan.tkvars[RISK_PER_SHARE],width=self.width[j])
				tradingplan.tklabels[RISK_PER_SHARE] = self.tk_labels_single[symbol][RISK_PER_SHARE]
				tradingplan.tklabels[RISK_PER_SHARE].grid(row= l+2, column=j,padx=0)

				self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])

			elif label_name =='SzIn':
				self.tk_labels_single[symbol][TARGET_SHARE]=tk.Entry(self.deployment_frame ,textvariable=tradingplan.tkvars[INPUT_TARGET_SHARE],width=self.width[j])
				tradingplan.tklabels[TARGET_SHARE] = self.tk_labels_single[symbol][TARGET_SHARE]
				tradingplan.tklabels[TARGET_SHARE].grid(row= l+2, column=j,padx=0)

				self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])

			elif label_name =="flatten":
				self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command=tradingplan.flatten_cmd)

			elif label_name == SUPPORT or label_name == RESISTENCE or label_name == "pxtgt1" or label_name == "pxtgt2" or label_name == "pxtgt3":
				self.tk_labels_single[symbol][label_name] =tk.Entry(self.deployment_frame ,textvariable=info[j],width=self.width[j],state="disabled")	
			else:
				if str(type(info[j]))=="<class 'tkinter.StringVar'>" or str(type(info[j]))=="<class 'tkinter.DoubleVar'>":
					self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
				else:
					#print(self.tk_labels_single[symbol])
					self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])
			try:
				self.label_default_configure(self.tk_labels_single[symbol][label_name])
			except:
				pass

			tradingplan.tklabels[label_name] = self.tk_labels_single[symbol][label_name]

			self.tk_labels_single[symbol][label_name].grid(row= l+2, column=j,padx=0)

		self.single_label_count +=1



		self.algo_count_number.set(self.single_label_count-1)
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


		l = self.single_label_count

		info = list(infos.values())
		labels = list(infos.keys())
		symbol = info[1]
		self.tk_labels_single[symbol] = {}
		for j in range(len(info)):
			#"symbol","algo_status","description","break_at","position","act_r/est_r","stoplevel","average_price","shares","pxtgt1","pxtgt1","pxtgt1","unrealized_pshr","unrealized","realized"
			label_name = labels[j]

			if label_name == "Symbol":
				self.tk_labels_single[symbol][label_name] = tk.Button(self.deployment_frame ,text=info[j],width=self.width[j],command=tradingplan.deploy)
			elif label_name == STATUS:
				self.tk_labels_single[symbol][label_name] = tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command=tradingplan.cancle_deployment)

			elif label_name ==TIMER:
				self.tk_labels_single[symbol][label_name] = tk.Entry(self.deployment_frame,textvariable=info[j],width=self.width[j])

			elif label_name =="AR" :
				self.tk_labels_single[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j],width=2,command=tradingplan.AR_toggle)
			elif label_name =="Reload" or label_name==SELECTED:
				self.tk_labels_single[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j],width=2)

			elif label_name =="MIND":
				self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
			elif label_name =="Stop":
				self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command= lambda tp=tradingplan:adjust_stop(tp))


			elif label_name ==RISK_RATIO:
				self.tk_labels_single[symbol][RISK_PER_SHARE]=tk.Entry(self.deployment_frame ,textvariable=tradingplan.tkvars[RISK_PER_SHARE],width=self.width[j])
				tradingplan.tklabels[RISK_PER_SHARE] = self.tk_labels_single[symbol][RISK_PER_SHARE]
				tradingplan.tklabels[RISK_PER_SHARE].grid(row= l+2, column=j,padx=0)

				self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])

			elif label_name =='SzIn':
				self.tk_labels_single[symbol][TARGET_SHARE]=tk.Entry(self.deployment_frame ,textvariable=tradingplan.tkvars[INPUT_TARGET_SHARE],width=self.width[j])
				tradingplan.tklabels[TARGET_SHARE] = self.tk_labels_single[symbol][TARGET_SHARE]
				tradingplan.tklabels[TARGET_SHARE].grid(row= l+2, column=j,padx=0)

				self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])

			elif label_name =="flatten":
				self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command=tradingplan.flatten_cmd)

			elif label_name == SUPPORT or label_name == RESISTENCE or label_name == "pxtgt1" or label_name == "pxtgt2" or label_name == "pxtgt3":
				self.tk_labels_single[symbol][label_name] =tk.Entry(self.deployment_frame ,textvariable=info[j],width=self.width[j],state="disabled")	
			else:
				if str(type(info[j]))=="<class 'tkinter.StringVar'>" or str(type(info[j]))=="<class 'tkinter.DoubleVar'>":
					self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
				else:
					#print(self.tk_labels_single[symbol])
					self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])
			try:
				self.label_default_configure(self.tk_labels_single[symbol][label_name])
			except:
				pass

			tradingplan.tklabels[label_name] = self.tk_labels_single[symbol][label_name]

			self.tk_labels_single[symbol][label_name].grid(row= l+2, column=j,padx=0)

		self.single_label_count +=1

		self.algo_count_number.set(self.single_label_count-1)
		self.rebind(self.dev_canvas,self.deployment_frame)
		#self.recreate_labels()
		tradingplan.update_displays()

	def management_plan_checking(self,symbol,plan,target_share,risk_per_share):

		if plan.get()==ANCARTMETHOD:
			self.tk_labels_single[symbol][RISK_RATIO].grid_remove()
			self.tk_labels_single[symbol]['SzIn'].grid_remove()
			target_share.set(100)
			risk_per_share.set(0.5)
		else:
			self.tk_labels_single[symbol][RISK_RATIO].grid()
			self.tk_labels_single[symbol]['SzIn'].grid()
			target_share.set(0)


	def create_example_trade(self):

		info=['AAPL','STATUS', 'MIND', 'Bullish', 'EntryStrat', 'Timer', 'ManaStart', 'AR', 'Sup', 'Res', 'Act/Est R', 'Long', 'AvgPx', 'SzIn', 'UPshr', 'U', 'R', 'TR', 'flatten', 'log']
		symbol = 'AAPL'
		self.tk_labels_single[symbol]={}
		self.tk_labels_single[symbol][1]=1
		l = self.single_label_count
		for j in range(len(info)):
			#"symbol","algo_status","description","break_at","position","act_r/est_r","stoplevel","average_price","shares","pxtgt1","pxtgt1","pxtgt1","unrealized_pshr","unrealized","realized"
			label_name = self.tk_labels[j]

			if label_name == "Symbol":
				self.tk_labels_single[symbol][label_name] = tk.Button(self.deployment_frame ,text=info[j],width=self.width[j],command = lambda s=symbol: self.deploy_stop_order(symbol))

			elif label_name =="Timer":
				self.tk_labels_single[symbol][label_name] = tk.Entry(self.deployment_frame,textvariable=info[j],width=self.width[j])

			# elif label_name =="EntryStrat":
			# 	self.tk_labels_single[symbol][label_name] = tk.OptionMenu(self.deployment_frame, textvariable="",set())

			# elif label_name =="ManaStart":
			# 	self.tk_labels_single[symbol][label_name] = tk.OptionMenu(self.deployment_frame, textvariable="",set())

			elif label_name =="AR" or  label_name =="AM":
				self.tk_labels_single[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j])
			elif label_name =="MIND":
				self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command = lambda s=symbol: self.cancel_deployed(symbol))
			elif label_name == "Sup" or label_name == "Res" or label_name == "pxtgt1" or label_name == "pxtgt2" or label_name == "pxtgt3":
				self.tk_labels_single[symbol][label_name] =tk.Entry(self.deployment_frame ,textvariable=info[j],width=self.width[j])	
			else:
				if str(type(info[j]))=="<class 'tkinter.StringVar'>":
					self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
				else:
					#print(self.tk_labels_single[symbol])
					self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

			try:
				self.label_default_configure(self.tk_labels_single[symbol][label_name])
			except:
				pass
			self.tk_labels_single[symbol][label_name].grid(row= l+2, column=j,padx=0)


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
		l = self.single_label_count

		#self.tickers_labels[i]=[]
		self.tickers_tracers[i] = []
		self.tk_labels_single[symbol] = {}

		#add in tickers.
		#print("LENGTH",len(info))
		for j in range(len(info)):
			#"symbol","algo_status","description","break_at","position","act_r/est_r","stoplevel","average_price","shares","pxtgt1","pxtgt1","pxtgt1","unrealized_pshr","unrealized","realized"
			label_name = self.tk_labels[j]

			if label_name == "symbol":
				self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,text=info[j][0],width=self.width[j],command = lambda s=symbol: self.deploy_stop_order(symbol))	
			elif label_name =="AR" or  label_name =="AM":
				self.tk_labels_single[symbol][label_name] =tk.Checkbutton(self.deployment_frame,variable=info[j])
			elif label_name =="algo_status":
				self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command = lambda s=symbol: self.cancel_deployed(symbol))
			elif label_name == "break_at" or label_name == "stoplevel" or label_name == "pxtgt1" or label_name == "pxtgt2" or label_name == "pxtgt3":
				self.tk_labels_single[symbol][label_name] =tk.Entry(self.deployment_frame ,textvariable=info[j],width=self.width[j])	
			else:
				if str(type(info[j]))=="<class 'tkinter.StringVar'>":
					self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
				else:
					self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])


			self.label_default_configure(self.tk_labels_single[symbol][label_name])

			self.tk_labels_single[symbol][label_name].grid(row= l+2, column=j,padx=0)

			#else: #command = lambda s=symbol: self.delete_symbol_reg_list(s))

		j+=1
		flatten=tk.Button(self.deployment_frame ,text="flatten",width=self.width[j],command= lambda k=i:self.flatten_symbol(k,symbol,status))
		self.label_default_configure(flatten)
		flatten.grid(row= l+2, column=j,padx=0)

		self.single_label_count +=1

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