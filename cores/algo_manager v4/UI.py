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

		self.tk_labels_basket = {}

		self.single_label_count = 1

		self.pair_label_count = 1

		self.basket_label_count = 1

		self.tklabels_list = []

		self.algo_counts = 0

		self.risk_timer = tk.DoubleVar(value=300)

		self.init_pannel()

		self.init_entry_pannel()



	def init_system_pannel(self):



	
		self.main_app_status = tk.StringVar()
		self.main_app_status.set("")

	
		self.user = tk.StringVar()
		self.user.set("")


		self.ppro_status = tk.StringVar()
		self.ppro_status.set("")

		self.ppro_out_status = tk.StringVar()
		self.ppro_out_status.set("")

		self.algo_count_number = tk.DoubleVar(value=0)
		self.algo_number = 0

		self.position_count = tk.IntVar(value=0)
		self.position_number = 0

		self.user_email = tk.StringVar()
		self.user_email.set("")

		self.user_phone = tk.StringVar()
		self.user_phone.set("")


		self.ppro_last_update = tk.StringVar()

		self.algo_count_string = tk.StringVar(value="0")
		self.algo_timer_string = tk.StringVar(value="0")
		self.algo_timer_close_string = tk.StringVar(value="0")

		self.algo_count_string.set("Activated Algos:"+str(self.algo_count_number))

		row = 1
		self.main = ttk.Label(self.system_pannel, text="Main:")
		self.main.grid(sticky="w",column=1,row=row,padx=10)
		
		self.main_status = ttk.Label(self.system_pannel, textvariable=self.main_app_status)
		self.main_status.grid(sticky="w",column=2,row=row)

		row += 1
		self.main = ttk.Label(self.system_pannel, text="Account ID:")
		self.main.grid(sticky="w",column=1,row=row,padx=10)
		
		self.account_status = ttk.Label(self.system_pannel, textvariable=self.user)
		self.account_status.grid(sticky="w",column=2,row=row)


		row +=1
		self.ppro = ttk.Label(self.system_pannel, text="Ppro In:")
		self.ppro.grid(sticky="w",column=1,row=row,padx=10)
		self.ppro_status_ = ttk.Label(self.system_pannel, textvariable=self.ppro_status)
		self.ppro_status_.grid(sticky="w",column=2,row=row)

		row +=1
		self.ppro = ttk.Label(self.system_pannel, text="Ppro Out:")
		self.ppro.grid(sticky="w",column=1,row=row,padx=10)
		self.ppro_status_out = ttk.Label(self.system_pannel, textvariable=self.ppro_out_status)
		self.ppro_status_out.grid(sticky="w",column=2,row=row)

		row +=1
		self.timerc = ttk.Label(self.system_pannel, text="Ppro Update:")
		self.timerc.grid(sticky="w",column=1,row=row,padx=10)
		self.timersx = ttk.Label(self.system_pannel,  textvariable=self.ppro_last_update)
		self.timersx.grid(sticky="w",column=2,row=row,padx=10)

		row +=1
		self.al = ttk.Label(self.system_pannel, text="Algo Count::")
		self.al.grid(sticky="w",column=1,row=row,padx=10)
		self.algo_count_ = ttk.Label(self.system_pannel,  textvariable=self.algo_count_number)
		self.algo_count_.grid(sticky="w",column=2,row=row,padx=10)

		row +=1
		self.al = ttk.Label(self.system_pannel, text="Position Count::")
		self.al.grid(sticky="w",column=1,row=row,padx=10)
		self.algo_count_ = ttk.Label(self.system_pannel,  textvariable=self.position_count)
		self.algo_count_.grid(sticky="w",column=2,row=row,padx=10)




		row +=1
		ttk.Label(self.system_pannel, text="Maximum Risk:").grid(sticky="w",column=1,row=row,padx=10)
		tk.Entry(self.system_pannel,textvariable=self.risk_timer,width=7).grid(sticky="w",column=2,row=row,padx=10)


		row +=1
		self.timerc = ttk.Label(self.system_pannel, text="User Email:")
		self.timerc.grid(sticky="w",column=1,row=row,padx=10)


		ttk.Label(self.system_pannel, text="User Email:").grid(sticky="w",column=1,row=row,padx=10)
		tk.Entry(self.system_pannel,textvariable=self.user_email,width=7).grid(sticky="w",column=2,row=row,padx=10)


		row +=1
		self.timerc = ttk.Label(self.system_pannel, text="User Phone:")
		self.timerc.grid(sticky="w",column=1,row=row,padx=10)

		ttk.Label(self.system_pannel, text="User Phone:").grid(sticky="w",column=1,row=row,padx=10)
		tk.Entry(self.system_pannel,textvariable=self.user_phone,width=7).grid(sticky="w",column=2,row=row,padx=10)

		# self.deconstruct = ttk.Button(self.system_pannel, text="Terminate GT",command=self.manager.terminateGT)#,command=self.deploy_all_stoporders)
		# self.deconstruct.grid(sticky="w",column=1,row=5)


	def update_performance(self,d):

		self.net.set(d['unrealizedPlusNet'])

		if d['net']>self.net_max.get():
			self.net_max.set(d['net'])

		if d['net']<self.net_min.get():
			self.net_min.set(d['net'])


		self.total_u.set(d['unrealized'] )

		if d['unrealized']>self.total_u_max.get():
			self.total_u_max.set(d['unrealized'])

		if d['unrealized']<self.total_u_min.get():
			self.total_u_min.set(d['unrealized'])

		self.trade_count.set(d['trades'])
		self.fees.set(d['fees'])
		self.sizeTraded.set(d['sizeTraded'])

		self.exposure.set(d['cur_exp'])
		self.exposure_max.set(d['max_exp'])

				# d['fees'] = fees
				# d['trades'] = trades
				# d['sizeTraded'] = sizeTraded
				# d['unrealizedPlusNet'] = unrealizedPlusNet
				# d['timestamp'] = ts
				# d['unrealized'] = unrealized	

	def init_performance_pannel(self):

		self.net = tk.DoubleVar()
		self.net_max = tk.DoubleVar()
		self.net_min = tk.DoubleVar()

		self.exposure = tk.StringVar()
		self.exposure_max = tk.StringVar()

		self.total_u = tk.DoubleVar()
		self.total_u_max = tk.DoubleVar()
		self.total_u_min = tk.DoubleVar()

		self.current_total_risk = tk.DoubleVar()
		self.max_risk = tk.DoubleVar()

		#self.position_count = tk.IntVar()
		self.position_count_max = tk.IntVar()

		self.trade_count = tk.IntVar()

		self.fees = tk.DoubleVar()
		self.sizeTraded = tk.IntVar()







		self.u_winning = tk.DoubleVar()
		self.u_winning_min = tk.DoubleVar()
		self.u_winning_max = tk.DoubleVar()

		self.u_losing = tk.DoubleVar()
		self.u_losing_min = tk.DoubleVar()
		self.u_losing_max = tk.DoubleVar()

		self.x1 = ttk.Button(self.performance_pannel, text="")
		self.x1.grid(sticky="w",column=1,row=1,padx=3)
		self.x1 = ttk.Button(self.performance_pannel, text="Cur:")
		self.x1.grid(sticky="w",column=1,row=2,padx=3)
		self.x2 = ttk.Button(self.performance_pannel, text="Min:")
		self.x2.grid(sticky="w",column=1,row=3,padx=3)
		self.x3 = ttk.Button(self.performance_pannel, text="Max:")
		self.x3.grid(sticky="w",column=1,row=4,padx=3)



		col = 1
		col +=1 
		self.t2 = ttk.Button(self.performance_pannel, text="Net:")
		self.t2.grid(sticky="w",column=col,row=1)
		self.t2_ = ttk.Button(self.performance_pannel, textvariable=self.net)
		self.t2_.grid(sticky="w",column=col,row=2)

		ttk.Button(self.performance_pannel, textvariable=self.net_min).grid(sticky="w",column=col,row=3)
		ttk.Button(self.performance_pannel, textvariable=self.net_max).grid(sticky="w",column=col,row=4)



		col +=1 
		self.t2 = ttk.Button(self.performance_pannel, text="Unreal:")
		self.t2.grid(sticky="w",column=col,row=1)
		self.t2_ = ttk.Button(self.performance_pannel, textvariable=self.total_u)
		self.t2_.grid(sticky="w",column=col,row=2)

		ttk.Button(self.performance_pannel, textvariable=self.total_u_min).grid(sticky="w",column=col,row=3)
		ttk.Button(self.performance_pannel, textvariable=self.total_u_max).grid(sticky="w",column=col,row=4)




		col +=1 
		self.t2 = ttk.Button(self.performance_pannel, text="Risk:")
		self.t2.grid(sticky="w",column=col,row=1)
		self.t2_ = ttk.Button(self.performance_pannel, textvariable=self.current_total_risk)
		self.t2_.grid(sticky="w",column=col,row=2)

		ttk.Button(self.performance_pannel, text="").grid(sticky="w",column=col,row=3)
		ttk.Button(self.performance_pannel, textvariable=self.max_risk).grid(sticky="w",column=col,row=4)


		col +=1 
		self.t2 = ttk.Button(self.performance_pannel, text="Position:")
		self.t2.grid(sticky="w",column=col,row=1)
		self.t2_ = ttk.Button(self.performance_pannel, textvariable=self.position_count)
		self.t2_.grid(sticky="w",column=col,row=2)




		ttk.Button(self.performance_pannel, text="").grid(sticky="w",column=col,row=3)
		ttk.Button(self.performance_pannel, textvariable=self.position_count_max).grid(sticky="w",column=col,row=4)

		col +=1 
		self.t2 = ttk.Button(self.performance_pannel, text="Exposure:")
		self.t2.grid(sticky="w",column=col,row=1)
		self.t2_ = ttk.Button(self.performance_pannel, textvariable=self.exposure)
		self.t2_.grid(sticky="w",column=col,row=2)

		ttk.Button(self.performance_pannel, text="").grid(sticky="w",column=col,row=3)
		ttk.Button(self.performance_pannel, textvariable=self.exposure_max).grid(sticky="w",column=col,row=4)



		col +=1 
		self.t2 = ttk.Button(self.performance_pannel, text="Trades:")
		self.t2.grid(sticky="w",column=col,row=1)
		self.t2_ = ttk.Button(self.performance_pannel, textvariable=self.trade_count)
		self.t2_.grid(sticky="w",column=col,row=2)

		ttk.Button(self.performance_pannel, text="").grid(sticky="w",column=col,row=3)
		ttk.Button(self.performance_pannel, text="").grid(sticky="w",column=col,row=4)

		col +=1 
		self.t2 = ttk.Button(self.performance_pannel, text="fees:")
		self.t2.grid(sticky="w",column=col,row=1)
		self.t2_ = ttk.Button(self.performance_pannel, textvariable=self.fees)
		self.t2_.grid(sticky="w",column=col,row=2)

		ttk.Button(self.performance_pannel, text="").grid(sticky="w",column=col,row=3)
		ttk.Button(self.performance_pannel, text="").grid(sticky="w",column=col,row=4)

		col +=1 
		self.t2 = ttk.Button(self.performance_pannel, text="SizeTraded:")
		self.t2.grid(sticky="w",column=col,row=1)
		self.t2_ = ttk.Button(self.performance_pannel, textvariable=self.sizeTraded)
		self.t2_.grid(sticky="w",column=col,row=2)

		ttk.Button(self.performance_pannel, text="").grid(sticky="w",column=col,row=3)
		ttk.Button(self.performance_pannel, text="").grid(sticky="w",column=col,row=4)


		# row +=1 
	def init_deployment_pannel(self):

		self.labels = {"":4,\
						"Strategy":8,\
						"Status":10,\
						"Updates":26,\
						"Est R":8,\
						"MaxU":8,\
						"MinU":8,\
						"U":8,\
						"R":8,\
						"flatten":8,\
						"log":8}
		self.width = list(self.labels.values())


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

	def init_pannel(self):

		self.system_pannel = ttk.LabelFrame(self.root,text="System") 
		self.system_pannel.place(x=10,y=10,height=260,width=210)

		self.control_pannel = ttk.LabelFrame(self.root,text="Control") 
		self.control_pannel.place(x=230,y=10,height=50,width=700)

		self.performance_pannel = ttk.LabelFrame(self.root,text="Performance") 
		self.performance_pannel.place(x=230,y=70,height=260,width=700)

		self.deployment_panel = ttk.LabelFrame(self.root,text="Strategy Deployment") 
		self.deployment_panel.place(x=10,y=260,height=500,width=920)

		self.init_system_pannel()
		self.init_performance_pannel()
		self.init_deployment_pannel()
		self.init_control_pannel()

	def init_control_pannel(self):

		col = 1
		try:
			ttk.Button(self.control_pannel, text="Flatten All (P)",command=self.manager.flatten_all).grid(sticky="w",column=col,row=1)
		except:
			pass
		# col +=1
		# ttk.Button(self.control_pannel, text="Flatten All (A)",command=self.manager.flatten_all).grid(sticky="w",column=col,row=1)

		col +=1
		ttk.Button(self.control_pannel, text="Weekly Report").grid(sticky="w",column=col,row=1)

		col +=1
		ttk.Button(self.control_pannel, text="Monthly Report").grid(sticky="w",column=col,row=1)





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



		# self.config2 = ttk.LabelFrame(self.config) 
		# self.config2.place(x=0,y=160,height=100,width=210)
		# self.algo_deploy = ttk.Button(self.config2, text="Apply Slctd",command=self.manager.set_selected_tp)#,command=self.manager.set_all_tp)
		# self.algo_deploy.grid(sticky="w",column=1,row=1,padx=10)
		# #self.algo_deploy.place(x=5,y=5)

		# self.algo_deploy = ttk.Button(self.config2, text="Deslect All",command=self.manager.deselect_all)#,command=self.deploy_all_stoporders)
		# self.algo_deploy.grid(sticky="w",column=1,row=2,padx=10)

		# self.algo_deploy = ttk.Button(self.config2, text="Apply All",command=self.manager.set_all_tp)#,command=self.deploy_all_stoporders)
		# self.algo_deploy.grid(sticky="w",column=2,row=1,padx=10)
		# #self.algo_deploy.place(x=5,y=25)



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

		# self.labels = {"":4,\
		# 		"Strategy":8,\
		# 		"Status":10,\
		# 		"INFO":20,\
		# 		"Est R":8,\
		# 		"U":8,\
		# 		"R":8,\
		# 		"TR":8,\
		# 		"flatten":8,}



		infos = {
		SELECTED:"",\
		'Symbol':"", \
		STATUS:"",\
		MIND: "",\

		ESTRISK:"", \
		UNREAL_MAX:"",\
		UNREAL_MIN:"",\
		UNREAL:"", \
		REALIZED:"", \
		TOTAL_REALIZED:"", \
		"flatten":"",\
		"log":""}

		info = list(infos.values())
		labels = list(infos.keys())

		for l in range(30):
			self.tk_labels_basket[l]={}
			for j in range(len(self.labels)):
				#"symbol","algo_status","description","break_at","position","act_r/est_r","stoplevel","average_price","shares","pxtgt1","pxtgt1","pxtgt1","unrealized_pshr","unrealized","realized"
				label_name = labels[j]

				if label_name == "Symbol":
					self.tk_labels_basket[l][label_name] = tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])
				elif label_name == STATUS:
					self.tk_labels_basket[l][label_name] = tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

				elif label_name ==TIMER:
					self.tk_labels_basket[l][label_name] = tk.Entry(self.deployment_frame,text=info[j],width=self.width[j])

				elif label_name =="AR" :
					self.tk_labels_basket[l][label_name] = tk.Checkbutton(self.deployment_frame,width=2,)
				elif label_name =="Reload" or label_name==SELECTED:
					self.tk_labels_basket[l][label_name] = tk.Checkbutton(self.deployment_frame,width=2)

				elif label_name =="MIND":
					self.tk_labels_basket[l][label_name] =tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

				elif label_name =="flatten":
					self.tk_labels_basket[l][label_name] =tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])

				elif label_name == SUPPORT or label_name == RESISTENCE or label_name == "pxtgt1" or label_name == "pxtgt2" or label_name == "pxtgt3":
					self.tk_labels_basket[l][label_name] =tk.Entry(self.deployment_frame ,text=info[j],width=self.width[j],state="disabled")	
				else:
					if str(type(info[j]))=="<class 'tkinter.StringVar'>" or str(type(info[j]))=="<class 'tkinter.DoubleVar'>":
						self.tk_labels_basket[l][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])
					else:
						#print(self.tk_labels_single[symbol])
						self.tk_labels_basket[l][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])
				try:
					self.label_default_configure(self.tk_labels_basket[l][label_name])
				except:
					pass

				self.tk_labels_basket[l][label_name].grid(row= l+2, column=j,padx=0)

		self.rebind(self.dev_canvas,self.deployment_frame)

	def create_new_single_entry(self,tradingplan,single,row_number):

		if single=="Single":

			if row_number==None:
				l = self.single_label_count
				row_number = l-1 


			self.create_single_entry(tradingplan, row_number)

			self.single_label_count +=1
			self.rebind(self.dev_canvas,self.deployment_frame)

			tradingplan.update_displays()

		elif single=="Pair":

			#print("XXXXXXXXXXXXXXX using row number",row_number,self.pair_label_count)
			if row_number==None:
				l = self.pair_label_count
				row_number = l-1 

			self.create_pair_entry(tradingplan, row_number)

			self.pair_label_count +=1

			self.rebind(self.dev_canvas,self.deployment_frame)
			tradingplan.update_displays()

		elif single=="Basket":

			if row_number==None:

				l = self.basket_label_count
				row_number = l-1 #info[1]
			
			self.create_basket_entry(tradingplan, row_number)

			self.basket_label_count +=1

			self.rebind(self.dev_canvas,self.deployment_frame)
			tradingplan.update_displays()


	def create_basket_entry(self,tradingplan,symbol):

		self.algo_count_number.set(self.algo_count_number.get()+1)


		self.labels = {"":4,\
						"Strategy":8,\
						"Status":10,\
						"Updates":26,\
						"Est R":8,\
						"Max_U":8,\
						"Min_U":8,\
						"U":8,\
						"R":8,\
						"TR":8,\
						"flatten":8,
						"log":4}

		self.algo_count_number.set(self.algo_count_number.get()+1)

		infos = {
		SELECTED:tradingplan.tkvars[SELECTED],\
		'Symbol':tradingplan.algo_name, \
		STATUS:tradingplan.tkvars[STATUS],\
		MIND: tradingplan.tkvars[MIND],\

		ESTRISK:tradingplan.tkvars[ESTRISK], \

		UNREAL_MAX: tradingplan.tkvars[UNREAL_MAX],\
		UNREAL_MIN: tradingplan.tkvars[UNREAL_MIN],\
		UNREAL:tradingplan.tkvars[UNREAL], \
		REALIZED:tradingplan.tkvars[REALIZED], \
		TOTAL_REALIZED:"", \
		'flatten':""}

		#link the global variable 
		tradingplan.tkvars[RISKTIMER] = self.risk_timer 

		info = list(infos.values())
		labels = list(infos.keys())	

		for j in range(len(info)):
			#"symbol","algo_status","description","break_at","position","act_r/est_r","stoplevel","average_price","shares","pxtgt1","pxtgt1","pxtgt1","unrealized_pshr","unrealized","realized"
			
			label_name = labels[j]
			#print(symbol,label_name,j,info,self.tk_labels_basket[symbol].keys())
			#print(self.tk_labels_single[symbol])
			if label_name == "Symbol":
				self.tk_labels_basket[symbol][label_name]["text"] = info[j] 
			elif label_name == STATUS:
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j] 
				#self.tk_labels_basket[symbol][label_name]["command"] = tradingplan.cancle_deployment
				#= tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command=tradingplan.cancle_deployment)

			elif label_name==SELECTED:
				self.tk_labels_basket[symbol][label_name]["variable"] = info[j]
				#self.tk_labels_single[symbol][label_name] = tk.Checkbutton(self.deployment_frame,variable=info[j],width=2)
				 
			elif label_name =="MIND":
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]
				#self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
			elif label_name =="Stop":
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]
				self.tk_labels_basket[symbol][label_name]["command"] = lambda tp=tradingplan:adjust_stop(tp)

				#self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command= lambda tp=tradingplan:adjust_stop(tp))


			elif label_name =="flatten":

				self.tk_labels_basket[symbol][label_name]["command"] = tradingplan.flatten_cmd

				#self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command=tradingplan.flatten_cmd)
			else:
				if str(type(info[j]))=="<class 'tkinter.StringVar'>" or str(type(info[j]))=="<class 'tkinter.DoubleVar'>":
					self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]
					#self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
				else:
					#print(self.tk_labels_single[symbol])
					self.tk_labels_basket[symbol][label_name]["text"] = info[j]
					#self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,text=info[j],width=self.width[j])
			# try:
			# 	self.label_default_configure(self.tk_labels_single[symbol][label_name])
			# except Exception as e:
			# 	print(e)

			tradingplan.tklabels[label_name] = self.tk_labels_basket[symbol][label_name]


		tradingplan.algo_ui_id = symbol




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
	root.title("GoodTrade Algo Manager v4") 
	root.geometry("950x780")
	UI(root)
	# root.minsize(1600, 1000)
	# root.maxsize(1800, 1200)
	root.mainloop()