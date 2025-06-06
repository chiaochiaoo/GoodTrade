from pannel import *
from constant import *
from Util_functions import *
from UI_custom_algo import * 
import time


try:
	from ttkwidgets.frames import Tooltip
except ImportError:
	import pip
	pip.main(['install', 'ttkwidgets'])
	from ttkwidgets.frames import Tooltip



def trace_func(d):

	if d['lock'].get()==0:
		d['set_entry']["state"] = DISABLED
		d['set_button']["state"] = DISABLED
		#d['flat_button']["state"] = DISABLED
		
		d['set_current']["state"] = DISABLED
		d['set_max']["state"] = DISABLED
		d['passive_button']["state"] = DISABLED


	else:
		d['set_entry']["state"] = "normal"
		d['set_button']["state"] = "normal"
		#d['flat_button']["state"] = "normal"
		d['set_current']["state"] = "normal"
		d['set_max']["state"] = "normal"
		d['passive_button']["state"] = "normal"



def show_tooltip(event, widget,root,label,text):
    x, y, _, _ = widget.bbox("insert")
    x += widget.winfo_rootx() + 25
    y += widget.winfo_rooty() - 25
    
    root.geometry("+{}+{}".format(x, y))
    label.config(text=text)
    root.deiconify()

def hide_tooltip(event,root):
    root.withdraw()


class UI(pannel):
	def __init__(self,root,manager=None,receiving_signals=None,cmd_text=None):

		self.root = root

		self.manager = manager

		self.receiving_signals = receiving_signals
		
		self.command_text = cmd_text

		self.tk_strings=["algo_status","realized","shares","unrealized","unrealized_pshr","average_price"]
		
		self.tk_labels=['Strategy',"Status","Updates" , "MaxU", "MinU", "U", "R", "WR", "MR", "TR", 'flatten', 'log']

		self.algo_limit = 220 #102 #200 -3

		self.algo_counts = 0


		self.sort_timer = 0
		self.sort_reverse_real = True 
		self.sort_reverse_unreal = True 
		
		# infos = {
		# 'Strategy':tradingplan.algo_name, \
		# STATUS:tradingplan.tkvars[STATUS],\
		# MIND: tradingplan.tkvars[MIND],\

		# ESTRISK:tradingplan.tkvars[ESTRISK], \

		# UNREAL_MAX: tradingplan.tkvars[UNREAL_MAX],\
		# UNREAL_MIN: tradingplan.tkvars[UNREAL_MIN],\
		# UNREAL:tradingplan.tkvars[UNREAL], \
		# REALIZED:tradingplan.tkvars[REALIZED], \
		# WR:tradingplan.tkvars[WR], \
		# MR:tradingplan.tkvars[MR], \
		# TR:tradingplan.tkvars[TR], \
		# 'flatten':"",\
		# 'log':""}

		self.tk_labels_single = {}

		self.tk_labels_pair = {}

		self.tk_labels_basket = {}

		self.single_label_count = 1

		self.pair_label_count = 1

		self.basket_label_count = 1

		self.tklabels_list = []

		self.deploy_list = []

		self.risk_timer = tk.DoubleVar(value=300)

		self.empty = tk.StringVar(value="")
		self.custom_algo = None 

		self.init_pannel()

		self.init_entry_pannel()

		self.custom_algo_init()


	def init_system_pannel(self):

		self.main_app_status = tk.StringVar()
		self.main_app_status.set("")

		self.user = tk.StringVar()
		self.user.set("DISCONNECTED")

		self.ppro_api_status = tk.StringVar()
		self.ppro_api_status.set("Disconnected")

		self.algo_count_number = tk.IntVar(value=0)
		self.active_algo_count_number = tk.IntVar(value=0)
		self.current_display_count = 0
		self.algo_number = 0

		self.position_count = tk.IntVar(value=0)
		self.position_number = 0

		self.user_email = tk.StringVar()
		self.user_email.set("")

		self.user_phone = tk.StringVar()
		self.user_phone.set("")

		self.system_status_text = tk.StringVar()
		self.system_status_text.set("ERROR")

		self.file_last_update = tk.StringVar(value="Disconnected")

		self.algo_count_string = tk.StringVar(value="0")
		self.algo_timer_string = tk.StringVar(value="0")
		self.algo_timer_close_string = tk.StringVar(value="0")

		self.algo_count_string.set("Activated Algos:"+str(self.algo_count_number))


		row = 1
		self.system = ttk.Label(self.system_pannel, text="SYSTEM:")
		self.system.grid(sticky="w",column=1,row=row,padx=10)

		self.system_status = tk.Button(self.system_pannel, textvariable=self.system_status_text,activebackground='red',activeforeground='yellow')
		self.system_status.grid(sticky="w",column=2,row=row)
		self.system_status["background"] = "red"
		row +=1
		self.account = ttk.Label(self.system_pannel, text="Account ID:")
		self.account.grid(sticky="w",column=1,row=row,padx=10)
		
		self.account_status = ttk.Label(self.system_pannel, textvariable=self.user)
		self.account_status.grid(sticky="w",column=2,row=row)
		self.account_status["background"] = "red"

		row +=1
		self.file_link_label = ttk.Label(self.system_pannel, text="File Linked:")
		self.file_link_label.grid(sticky="w",column=1,row=row,padx=10)
		self.file_link_status = ttk.Label(self.system_pannel,  textvariable=self.file_last_update)
		self.file_link_status["background"] = "red"
		self.file_link_status.grid(sticky="w",column=2,row=row,padx=10)

		row +=1
		self.ppro = ttk.Label(self.system_pannel, text="Ppro API:")
		self.ppro.grid(sticky="w",column=1,row=row,padx=10)
		self.ppro_api_status_label = ttk.Label(self.system_pannel, textvariable=self.ppro_api_status)
		self.ppro_api_status_label.grid(sticky="w",column=2,row=row)
		self.ppro_api_status_label["background"] = "red"


		row +=1
		self.al = ttk.Label(self.system_pannel, text="Total Algo Count::")
		self.al.grid(sticky="w",column=1,row=row,padx=10)
		self.algo_count_ = ttk.Label(self.system_pannel,  textvariable=self.algo_count_number)
		self.algo_count_.grid(sticky="w",column=2,row=row,padx=10)


		row +=1
		self.al = ttk.Label(self.system_pannel, text="Active Algo Count::")
		self.al.grid(sticky="w",column=1,row=row,padx=10)
		self.algo_count_ = ttk.Label(self.system_pannel,  textvariable=self.active_algo_count_number)
		self.algo_count_.grid(sticky="w",column=2,row=row,padx=10)

		row +=1
		self.al = ttk.Label(self.system_pannel, text="Position Count::")
		self.al.grid(sticky="w",column=1,row=row,padx=10)
		self.algo_count_ = ttk.Label(self.system_pannel,  textvariable=self.position_count)
		self.algo_count_.grid(sticky="w",column=2,row=row,padx=10)



		row +=1
		self.ol = ttk.Label(self.system_pannel, text="Orders Count::")
		self.ol.grid(sticky="w",column=1,row=row,padx=10)
		# self.algo_count_ = ttk.Label(self.system_pannel,  textvariable=self.position_count)
		# self.algo_count_.grid(sticky="w",column=2,row=row,padx=10)

		row +=1

		ttk.Label(self.system_pannel, text="Subdollar 500MIN:").grid(sticky="w",column=1,row=row,padx=10)

		try:
			ttk.Checkbutton(self.system_pannel, variable=self.manager.subdollar_check).grid(sticky="w",column=2,row=row)
		except:
			pass 

		row +=1

		ttk.Label(self.system_pannel, text="NQ Trader Only:").grid(sticky="w",column=1,row=row,padx=10)

		try:
			ttk.Checkbutton(self.system_pannel, variable=self.manager.nq_only).grid(sticky="w",column=2,row=row)
		except:
			pass 


		row +=1

		ttk.Label(self.system_pannel, text="Disaster mode:").grid(sticky="w",column=1,row=row,padx=10)

		try:
			ttk.Checkbutton(self.system_pannel, variable=self.manager.disaster_mode).grid(sticky="w",column=2,row=row)
		except:
			pass 

		row +=1

		ttk.Label(self.system_pannel, text="Stop Taking More Algos:").grid(sticky="w",column=1,row=row,padx=10)

		try:
			ttk.Checkbutton(self.system_pannel, variable=self.manager.stop_more_algos).grid(sticky="w",column=2,row=row)
		except:
			pass 

		row +=1
		ttk.Label(self.system_pannel, text="Maximum Risk:").grid(sticky="w",column=1,row=row,padx=10)
		self.risk_amount = tk.Entry(self.system_pannel,textvariable=self.risk_timer,width=7)
		self.risk_amount.grid(sticky="w",column=2,row=row,padx=10)

		self.risk_set = ttk.Button(self.system_pannel, text="Set Risk",command=self.set_risk)
		self.risk_set.grid(sticky="w",column=3,row=row)


	def set_risk(self):

		try:

			risk_ = int(self.risk_amount.get())
			self.risk_set["text"] = "Risk Set: "+str(risk_)
			self.manager.set_risk(risk_)
		except Exception as e:

			print(e)


	def update_performance(self,d):

		self.net.set(d['unrealizedPlusNet'])

		d['net'] = d['unrealizedPlusNet']
		
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

		self.position_count_max = tk.IntVar()

		self.trade_count = tk.IntVar()

		self.fees = tk.DoubleVar()
		self.sizeTraded = tk.IntVar()

		self.weeklyTotal = tk.IntVar(value=1)
		self.monthlyTotal = tk.IntVar(value=1)
		self.quarterlyTotal = tk.IntVar(value=1)

		self.weekly_algo = tk.StringVar()
		self.monthly_manual = tk.StringVar()
		self.quarterly_manual = tk.StringVar()


		self.weekly_commision = tk.StringVar()
		self.monthly_commision = tk.StringVar()
		self.quarterly_commision = tk.StringVar()

		self.weeklySR = tk.DoubleVar(value=1)
		self.monthlySR = tk.DoubleVar(value=1)

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
		self.t2 = ttk.Button(self.performance_pannel, text="WeeklyTotal:")
		self.t2.grid(sticky="w",column=col,row=1)
		self.t2_ = ttk.Button(self.performance_pannel, textvariable=self.weeklyTotal)
		self.t2_.grid(sticky="w",column=col,row=2)

		ttk.Button(self.performance_pannel, text="").grid(sticky="w",column=col,row=3)
		ttk.Button(self.performance_pannel, text="").grid(sticky="w",column=col,row=4)



		col +=1 
		self.t2 = ttk.Button(self.performance_pannel, text="MonthlyTotal:")
		self.t2.grid(sticky="w",column=col,row=1)
		self.t2_ = ttk.Button(self.performance_pannel, textvariable=self.monthlyTotal)
		self.t2_.grid(sticky="w",column=col,row=2)

		ttk.Button(self.performance_pannel, textvariable=self.monthly_commision).grid(sticky="w",column=col,row=3)
		ttk.Button(self.performance_pannel, textvariable=self.monthly_manual).grid(sticky="w",column=col,row=4)


		col +=1 
		self.t2 = ttk.Button(self.performance_pannel, text="QuarterTotal:")
		self.t2.grid(sticky="w",column=col,row=1)
		self.t2_ = ttk.Button(self.performance_pannel, textvariable=self.quarterlyTotal)
		self.t2_.grid(sticky="w",column=col,row=2)

		ttk.Button(self.performance_pannel, textvariable=self.quarterly_commision).grid(sticky="w",column=col,row=3)
		ttk.Button(self.performance_pannel, textvariable=self.quarterly_manual).grid(sticky="w",column=col,row=4)



	def init_deployment_pannel(self):

		self.labels = {"CANCEL":6,\
						"Strategy":40,\
						"Status":8,\
						#"Updates":5,\
						"MaxU":8,\
						"MinU":8,\
						UNREAL:8,\
						REALIZED:8,\
						"WR":7,\
						"MR":7,\
						"TR":7,\
						"BR":6,\
						"-90%":6,\
						"-50%":6,\
						"+25%":6,\
						"R100":6,\
						"flatten":8,\
						"a-flatten":8,\
						}
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

		self.sub_pannel = ttk.LabelFrame(self.root,text="") 
		self.sub_pannel.place(x=0,y=300,height=950,width=350)

		self.SUB_TAB = ttk.Notebook(self.sub_pannel)
		self.SUB_TAB.place(x=0,rely=0.00,relheight=1,width=640)

		self.quick_spread_pannel = ttk.LabelFrame(self.SUB_TAB,text="") 

		self.custom_algo_pannel = ttk.LabelFrame(self.SUB_TAB,text="") 

		self.tms_pannel = ttk.LabelFrame(self.SUB_TAB,text="") 

		self.SUB_TAB.add(self.custom_algo_pannel,text="AlgoAuthorization")
		self.SUB_TAB.add(self.quick_spread_pannel,text="QuickSpread")

		self.SUB_TAB.add(self.tms_pannel,text="TMS Simulation")

		# self.TNV_TAB = ttk.Notebook(self.custom_algo_pannel)
		# self.TNV_TAB.place(x=0,rely=0.01,relheight=1,width=640)

		self.system_pannel = ttk.LabelFrame(self.root,text="System")
		self.system_pannel.place(x=10,y=10,height=300,width=350)

		self.control_pannel = ttk.LabelFrame(self.root,text="Control") 
		self.control_pannel.place(x=360,y=10,height=50,width=300)

		self.gateway_pannel = ttk.LabelFrame(self.root,text="Default Gateway") 
		self.gateway_pannel.place(x=560,y=10,height=50,width=300)

		self.badsymbol_pannel = ttk.LabelFrame(self.root,text="Bad Symbols") 
		self.badsymbol_pannel.place(x=860,y=10,height=50,width=300)

		self.performance_pannel = ttk.LabelFrame(self.root,text="Performance") 
		self.performance_pannel.place(x=360,y=70,height=200,width=1300)

		self.filter_pannel = ttk.LabelFrame(self.root,text="Algorithms Management") 
		self.filter_pannel.place(x=360,y=200,height=60,width=1300)

		self.deployment_panel = ttk.LabelFrame(self.root,text="Algorithms Deployment") 
		self.deployment_panel.place(x=360,y=260,height=950,width=1300)

		self.init_system_pannel()
		self.init_performance_pannel()

		self.init_strategy_filter()
		self.init_deployment_pannel()
		self.init_control_pannel()

		self.init_gateway()
		self.init_bad_symbol_pannel()
		self.init_quick_spread()

		self.init_tms_simulation()

	def init_strategy_filter(self):

		self.strategy_filter = tk.StringVar()

		# reset button
		c=1
		ttk.Button(self.filter_pannel, text="Only Running",command=self.show_running_only).grid(sticky="w",column=c,row=1)
		# filter button 

		c+=1
		ttk.Button(self.filter_pannel, text="Only Done",command=self.show_done_only).grid(sticky="w",column=c,row=1)


		# c+=1
		# ttk.Button(self.filter_pannel, text="+ 25% to L",command=self.add_to_winners).grid(sticky="w",column=c,row=1)


		# c+=1
		# ttk.Button(self.filter_pannel, text="- 25% to L",command=self.add_to_winners).grid(sticky="w",column=c,row=1)


		# c+=1
		# ttk.Button(self.filter_pannel, text="Only Done",command=self.show_done_only).grid(sticky="w",column=c,row=1)


		# c+=1
		# ttk.Button(self.filter_pannel, text="Clone Winning",command=self.show_done_only,state= "disabled").grid(sticky="w",column=c,row=1)

		# c+=1
		# ttk.Button(self.filter_pannel, text="Clone Losing",command=self.show_done_only,state= "disabled").grid(sticky="w",column=c,row=1)

		# c+=1
		# ttk.Button(self.filter_pannel, text="Only QS",command=self.save_quick_spread).grid(sticky="w",column=c,row=1)

		# current filter. 
		c+=1
		tk.Label(self.filter_pannel, text="Symbol Filter:").grid(sticky="w",column=c,row=1)




		# row 1 entry
		c+=1
		tk.Entry(self.filter_pannel,textvariable=self.strategy_filter,width=20).grid(sticky="w",column=c,row=1)	

		c+=1
		ttk.Button(self.filter_pannel, text="Filter",command=self.show_selected_only).grid(sticky="w",column=c,row=1)
		c+=1
		ttk.Button(self.filter_pannel, text="+ 25% to W",command=self.add_to_winners).grid(sticky="w",column=c,row=1)


		c+=1
		ttk.Button(self.filter_pannel, text="- 25% to W",command=self.sub_to_winners).grid(sticky="w",column=c,row=1)



	def show_selected_only(self):

		# l = self.manager.return_selected_algo(self.strategy_filter.get())

		# # reset the numbers. 

		# self.init_entry_pannel()
		# self.basket_label_count = 1

		# # REFRESH?
		# for i in l:
		# 	self.create_new_single_entry(i,"Basket",None)
			
		try:

			now = datetime.now()
			ts = now.hour*3600 + now.minute*60 + now.second

			if ts>self.sort_timer+2:
				self.sort_timer = ts 

				l = self.manager.return_selected_algo(self.strategy_filter.get())

				self.count_current()
				for i in range(0,self.current_display_count):

					#print("evicting,",i)
					self.evict_entry(i)

				self.basket_label_count = 1
				for i in l:
					self.create_new_single_entry(self.manager.baskets[i],"Basket",None)

			# for basket in self.manager.baskets.keys():
			# 	print(basket,self.manager.baskets[basket].display)
		except Exception as e:
			PrintException(e,"show_running_only error")


	def count_current(self):

		c = 0 

		for symbol in self.tk_labels_basket.keys():
			if self.tk_labels_basket[symbol]['Strategy']["text"]!="":
				c+=1

		self.current_display_count = c 
		log_print("current count:",self.current_display_count)

	def add_to_winners(self):

		now = datetime.now()
		ts = now.hour*3600 + now.minute*60 + now.second

		if ts>self.sort_timer+1:
			self.sort_timer = ts 

			l = self.manager.return_running_algo()[:self.algo_limit]
			for i in l:
				self.manager.baskets[i].add_to_winners()

	def sub_to_winners(self):

		now = datetime.now()
		ts = now.hour*3600 + now.minute*60 + now.second

		if ts>self.sort_timer+1:
			self.sort_timer = ts 

			l = self.manager.return_running_algo()[:self.algo_limit]

			for i in l:
				self.manager.baskets[i].sub_to_winners()
	def show_running_only(self):

		try:

			now = datetime.now()
			ts = now.hour*3600 + now.minute*60 + now.second

			if ts>self.sort_timer+2:
				self.sort_timer = ts 

				l = self.manager.return_running_algo()[:self.algo_limit]

				self.count_current()
				for i in range(0,self.current_display_count):

					#print("evicting,",i)
					self.evict_entry(i)

				self.basket_label_count = 1
				for i in l:
					self.create_new_single_entry(self.manager.baskets[i],"Basket",None)

			# for basket in self.manager.baskets.keys():
			# 	print(basket,self.manager.baskets[basket].display)
		except Exception as e:
			PrintException(e,"show_running_only error")
			

	def show_done_only(self):

		try:

			now = datetime.now()
			ts = now.hour*3600 + now.minute*60 + now.second

			if ts>self.sort_timer+2:
				self.sort_timer = ts 

				l = self.manager.return_done_algo()[:self.algo_limit]

				self.count_current()
				for i in range(0,self.current_display_count):
					self.evict_entry(i)


				self.basket_label_count = 1
				for i in l:
					#print(i,self.basket_label_count)
					self.create_new_single_entry(self.manager.baskets[i],"Basket",None)

		except Exception as e:
			PrintException(e,"Show done only error")

	def save_quick_spread(self):

		d = {}

		tab =self.TNV_TAB.tab(self.TNV_TAB.select(),"text")

		for algo,item in self.qs.items():
			d[algo]=[item['increment'].get(),item['max'].get()]

		with open('quickspread_setting.json', 'w') as fp:
			json.dump(d, fp)


	def load_quick_spread(self):

		try:
			with open('quickspread_setting.json', 'r') as myfile:
				data=myfile.read()

			# parse file
			d = json.loads(data)
			#print("loading",tab)

			for key,item in d.items():
				#print(self.algos[tab][key])
				try:
					increment,max_ = item[0],item[1]
					self.qs[key]['increment'].set(increment)
					self.qs[key]['max'].set(max_)
				except Exception as e:
					print(e)
		except Exception as e:
			print(e)


	def as_is(self,dic):

		self.manager.algo_as_is(dic['name'])


	def submit_spread(self,dic,type_):
	

		now = datetime.now()
		ts = now.hour*3600 + now.minute*60 + now.second

		if ts-self.spread_timer>=5:

			if type_ =="flat":
				dic["current"].set(0)

			elif type_ =="long": #add 

				dic["current"].set(dic["current"].get()+dic['increment'].get())


			elif type_ =="short": #minus
	
				dic["current"].set(dic["current"].get()-dic['increment'].get())

			elif type_ =="direct":

				dic["current"].set(dic["current"].get())
				#dic['lock'].set(0)


			if abs(dic["current"].get())>dic["max"].get():

				if dic["current"].get()>0:
					coe = 1 
				else:
					coe = -1 

				dic["current"].set(dic['max'].get()*coe)

			share1 = dic["current"].get()*dic["ratio"][0]
			share2 = dic["current"].get()*dic["ratio"][1]

			timer = int(dic['TA'].get())
			self.spread_timer = ts

			log_print("Quick Spread:",dic['symbol'],share1,share2,'time:',timer)

			d={}
			d['pair'] = dic['name']
			d['symbol1'] = dic['symbol'][0]
			d['symbol2'] = dic['symbol'][1]
			d['amount'] = dic["current"].get()
			d['ratio'] = dic["ratio"]
			d['passive'] = dic['passive'].get()
			d['timer'] = timer


			try:
				print(d)
				self.manager.apply_pair_cmd(d)
				#self.manager.apply_basket_cmd(dic['name'],{dic['symbol'][0]:share1,dic['symbol'][1]:share2},0,1)
			except Exception as e:
				PrintException("QS error:",e)

			dic["status"].set("Confirmed")
			dic['status_bar']['bg'] = 'lightgreen'
		else:
			dic["status"].set("WAIT: "+str(5-(ts-self.spread_timer))+"s")
			dic['status_bar']['bg'] = 'red'


	def init_bad_symbol_pannel(self):

		self.bad_symbol = tk.StringVar()
		ttk.Entry(self.badsymbol_pannel,textvariable=self.bad_symbol,width=15).grid(sticky="w",column=1,row=1)

		try:
			self.submit_bad_symbol = ttk.Button(self.badsymbol_pannel, text="Submit",command=self.manager.submit_badsymbol)
			self.submit_bad_symbol.grid(sticky="w",column=2,row=1)
		except Exception as e:
			pass


	def init_gateway(self):

		self.gateway = tk.StringVar()
		self.gateway.set("MEMX")

		options = [
			"MEMX",
			"ARCA",
			"BATS",
			"EDGA",
			"MEMX-P",
			"ARCA-P",
		]


		drop = tk.OptionMenu(self.gateway_pannel , self.gateway , *options )
		drop.grid(row=1, column=1)

		try:
			self.set_gateway = ttk.Button(self.gateway_pannel, text="Set Change:MEMX",command=self.manager.set_gateway)
			self.set_gateway.grid(sticky="w",column=2,row=1)
		except:
			pass



	def init_control_pannel(self):

		col = 1

		style = ttk.Style()
		style.configure('K.TButton', background = 'red')

		
		ttk.Button(self.control_pannel,text="STOP ALL",style='K.TButton').grid(sticky="w",column=col,row=1)


		col +=1
		try:
			ttk.Button(self.control_pannel, text="Flatten All (P)",command=self.manager.flatten_all).grid(sticky="w",column=col,row=1)
		except:
			pass
		# col +=1
		# ttk.Button(self.control_pannel, text="Flatten All (A)",command=self.manager.flatten_all).grid(sticky="w",column=col,row=1)

		# col +=1
		# ttk.Button(self.control_pannel, text="Weekly Report").grid(sticky="w",column=col,row=1)

		# col +=1
		# ttk.Button(self.control_pannel, text="Monthly Report").grid(sticky="w",column=col,row=1)

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

	def refresh_entry_pannel(self):
		pass 

	def init_entry_pannel(self):

		infos = {}
		for key in self.labels.keys():
			infos[key] = ""

		info = list(infos.values())
		labels = list(infos.keys())

		for l in range(self.algo_limit):
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

		try:
			if single=="Single":

				if row_number==None:
					l = self.single_label_count
					row_number = l-1 


				self.create_single_entry(tradingplan, row_number)

				self.single_label_count +=1
				self.rebind(self.dev_canvas,self.deployment_frame)

				tradingplan.turn_on_display()
				tradingplan.update_displays()

			elif single=="Pair":

				#print("XXXXXXXXXXXXXXX using row number",row_number,self.pair_label_count)
				if row_number==None:
					l = self.pair_label_count
					row_number = l-1 

				self.create_pair_entry(tradingplan, row_number)

				self.pair_label_count +=1

				self.rebind(self.dev_canvas,self.deployment_frame)
				tradingplan.turn_on_display()
				tradingplan.update_displays()

			elif single=="Basket":

				if row_number==None:

					l = self.basket_label_count
					row_number = l-1 #info[1]


					### here, insert the top of the list, do a search program.

					#
					# if row_number>(self.algo_limit//2):
					# 	row_number = self.find_empty_spot()
				
				self.create_basket_entry(tradingplan, row_number)

				self.basket_label_count +=1


				self.rebind(self.dev_canvas,self.deployment_frame)
				tradingplan.turn_on_display()
				tradingplan.update_displays()

			return True 
		except Exception as e:
			PrintException("UI ERROR:,",e)
			return False 

	def find_empty_spot(self):

		for i in range(0,self.algo_limit):
			status = self.tk_labels_basket[i][STATUS]['text']
			if status=="" or status==DONE:
				print(i,"is free")

				return i 


	def evict_entry(self,symbol):
		infos = {
		'Strategy':"", \
		"Status":self.empty,\
		"MaxU": self.empty,\
		"MinU": self.empty,\
		UNREAL:self.empty, \
		REALIZED:self.empty, \
		"WR":self.empty, \
		"MR":self.empty, \
		"TR":self.empty, \
		"BR":self.empty,\
		"-90%":self.empty,\
		"-50%":self.empty,\
		"+25%":self.empty,\
		'flatten':"",\
		"a-flatten":"",
		}

		info = list(infos.values())
		labels = list(infos.keys())	

		for j in range(len(info)):
			label_name = labels[j]
			if label_name == "Strategy":
				self.tk_labels_basket[symbol][label_name]["text"] = info[j] 
			elif label_name == STATUS:
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j] 
				self.tk_labels_basket[symbol][label_name]["background"] = DEFAULT
			elif label_name==SELECTED:
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]
			elif label_name =="MIND":
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]
			elif label_name =="Stop":
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]

			elif label_name =="-90%":
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]

			elif label_name =="-50%":
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]
			elif label_name =="+25%":
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]

			else:
				if str(type(info[j]))=="<class 'tkinter.StringVar'>" or str(type(info[j]))=="<class 'tkinter.DoubleVar'>":
					self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]
					self.tk_labels_basket[symbol][label_name]["background"] = DEFAULT
					#self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
				else:
					#print(self.tk_labels_single[symbol])
					self.tk_labels_basket[symbol][label_name]["text"] = info[j]
					self.tk_labels_basket[symbol][label_name]["background"] = DEFAULT


	def create_basket_entry(self,tradingplan,symbol):


		if tradingplan.algo_name not in self.deploy_list:
			self.algo_count_number.set(self.algo_count_number.get()+1)
			self.deploy_list.append(tradingplan.algo_name)


		#self.algo_count_number.set(self.algo_count_number.get()+1)

		infos = {
		'CANCEL':"",\
		'Strategy':tradingplan.algo_name, \
		"Status":tradingplan.tkvars[STATUS],\
		"MaxU": tradingplan.tkvars[UNREAL_MAX],\
		"MinU": tradingplan.tkvars[UNREAL_MIN],\
		UNREAL:tradingplan.tkvars[UNREAL], \
		REALIZED:tradingplan.tkvars[REALIZED], \
		"WR":tradingplan.tkvars[WR], \
		"MR":tradingplan.tkvars[MR], \
		"TR":tradingplan.tkvars[TR], \
		"BR":tradingplan.tkvars['break_even'],\
		"-90%":tradingplan.tkvars[ALGO_MULTIPLIER],\
		"-50%":tradingplan.tkvars[ALGO_MULTIPLIER],\
		"+25%":tradingplan.tkvars[ALGO_MULTIPLIER],\
		"R100":"",\
		'flatten':"",\
		"a-flatten":"",
		}

		#link the global variable 
		tradingplan.tkvars[RISKTIMER] = self.risk_timer 

		info = list(infos.values())
		labels = list(infos.keys())	

		for j in range(len(info)):

			label_name = labels[j]

			if label_name == "Strategy":
				self.tk_labels_basket[symbol][label_name]["text"] = info[j] 
				#self.tk_labels_basket[symbol][label_name]["command"] = tradingplan.clone_cmd

				self.tk_labels_basket[symbol][label_name].bind("<Double-1>", lambda event:  tradingplan.clone_cmd())

			elif label_name == STATUS:
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j] 
				self.tk_labels_basket[symbol][label_name]["command"] = tradingplan.print_positions
				self.tk_labels_basket[symbol][label_name]["background"] = DEFAULT
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

			elif label_name =="MaxU":
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]
				#self.tk_labels_basket[symbol][label_name].bind("<Double-1>", lambda event:  tradingplan.turn_on_inspection())
			elif label_name =="MinU":
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]
				#self.tk_labels_basket[symbol][label_name].bind("<Double-1>", lambda event:  tradingplan.turn_off_inspection())
			elif label_name =="flatten":

				self.tk_labels_basket[symbol][label_name]["command"] = tradingplan.flatten_cmd

			elif label_name =="a-flatten":

				self.tk_labels_basket[symbol][label_name]["command"] = tradingplan.flatten_cmd_aggresive
			elif label_name =="-90%":
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]
				self.tk_labels_basket[symbol][label_name]["command"] = tradingplan.reduce_ninety

			elif label_name =="-50%":
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]
				self.tk_labels_basket[symbol][label_name]["command"] = tradingplan.reduce_one_half

			elif label_name =="+25%":
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]
				self.tk_labels_basket[symbol][label_name]["command"] = tradingplan.increase_one_quarter
				#self.tk_labels_single[symbol][label_name] =tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j],command=tradingplan.flatten_cmd)
			elif label_name =="R100":
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]
				self.tk_labels_basket[symbol][label_name]["command"] = tradingplan.round_to_100	
			elif label_name =="BR":
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]
				self.tk_labels_basket[symbol][label_name]["command"] = tradingplan.break_even_function
			elif label_name =="CANCEL":
				self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]
				self.tk_labels_basket[symbol][label_name]["command"] = tradingplan.cancel	
			else:
				if str(type(info[j]))=="<class 'tkinter.StringVar'>" or str(type(info[j]))=="<class 'tkinter.DoubleVar'>":
					self.tk_labels_basket[symbol][label_name]["textvariable"] = info[j]
					#self.tk_labels_single[symbol][label_name]=tk.Button(self.deployment_frame ,textvariable=info[j],width=self.width[j])
				else:
					#print(self.tk_labels_single[symbol])
					self.tk_labels_basket[symbol][label_name]["text"] = info[j]
					self.tk_labels_basket[symbol][label_name]["background"] = DEFAULT
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

			
			if l[i] =="UNREAL":
				print("creating:",l[i])

				self.b["command"] = self.sort_by_unrealize
			elif l[i] == "REALIZED":
				print("creating:",l[i])
				self.b["command"] = self.sort_by_realize

	def get_current_display(self):



		all_strat = []

		for symbol in range(0,self.algo_limit):
			if self.tk_labels_basket[symbol]['Strategy']['text']!="":
				all_strat.append(self.tk_labels_basket[symbol]['Strategy']['text'])

		all_strat = list(set(all_strat))

		print(all_strat)

		return all_strat


	def sort_by_unrealize(self):

		## whatever is being shown right now. ##

		now = datetime.now()
		ts = now.hour*3600 + now.minute*60 + now.second

		if ts>self.sort_timer+2:
			self.sort_timer = ts 

			l = self.get_current_display()

			data = {}

			for i in l:
				data[i] = self.manager.baskets[i].data[UNREAL]

			if self.sort_reverse_unreal:
				l = [key for key, value in sorted(data.items(), key=lambda item: item[1], reverse=True)]
				self.sort_reverse_unreal = False 
			else:
				l = [key for key, value in sorted(data.items(), key=lambda item: item[1], reverse=False)]
				self.sort_reverse_unreal = True
			

			self.count_current()
			for i in range(0,self.current_display_count):
				#print("evicting,",i)
				self.evict_entry(i)

			self.basket_label_count = 1
			for i in l:
				self.create_new_single_entry(self.manager.baskets[i],"Basket",None)

	def sort_by_realize(self):

		now = datetime.now()
		ts = now.hour*3600 + now.minute*60 + now.second

		if ts>self.sort_timer+2:
			self.sort_timer = ts 

			l = self.get_current_display()

			data = {}

			for i in l:
				data[i] = self.manager.baskets[i].data[REALIZED]

			if self.sort_reverse_unreal:
				l = [key for key, value in sorted(data.items(), key=lambda item: item[1], reverse=True)]
				self.sort_reverse_unreal = False 
			else:
				l = [key for key, value in sorted(data.items(), key=lambda item: item[1], reverse=False)]
				self.sort_reverse_unreal = True


			self.count_current()
			for i in range(0,self.current_display_count):

				#print("evicting,",i)
				self.evict_entry(i)


			self.basket_label_count = 1
			for i in l:
				self.create_new_single_entry(self.manager.baskets[i],"Basket",None)


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
	
	def init_tms_simulation(self):

		try:

			c=1

			ttk.Button(self.tms_pannel, text="Sim 1: 1 Passive, QQQ 10",command=self.manager.sim1).grid(sticky="w",column=1,row=1)
			c+=1
			ttk.Button(self.tms_pannel, text="Sim 2: 2 Passive QQQ 10 SPY -10",command=self.manager.sim2).grid(sticky="w",column=1,row=c)
			c+=1
			ttk.Button(self.tms_pannel, text="Sim 3: 3 Passive (div) IWM 15,-5 VOO -15,5",command=self.manager.sim3).grid(sticky="w",column=1,row=c)
			c+=1
			ttk.Button(self.tms_pannel, text="Sim 4: 1 Aggressive QLD 10",command=self.manager.sim4).grid(sticky="w",column=1,row=c)
			c+=1
			ttk.Button(self.tms_pannel, text="Sim 5: 2 Aggressive QQQM 10 QQJ -5",command=self.manager.sim5).grid(sticky="w",column=1,row=c)
			c+=1

			ttk.Button(self.tms_pannel, text="Sim 6: 3 Aggresive (div) TQQQ 15,-5, SQQQ -15,5",command=self.manager.sim6).grid(sticky="w",column=1,row=c)
			c+=1

			ttk.Button(self.tms_pannel, text="SIM: MM: SQQQ",command=self.manager.sim18).grid(sticky="w",column=1,row=c)
			c+=1
			ttk.Button(self.tms_pannel, text="SIM: AMM : SQQQTQQQ",command=self.manager.sim19).grid(sticky="w",column=1,row=c)
			c+=1
			ttk.Button(self.tms_pannel, text="SIM: AMM : SQQQTQQQ-AGG",command=self.manager.sim19b).grid(sticky="w",column=1,row=c)
			c+=1
			ttk.Button(self.tms_pannel, text="SIM: AMM : RWM/IWM",command=self.manager.sim20).grid(sticky="w",column=1,row=c)
			c+=1
			ttk.Button(self.tms_pannel, text="Sim 7: MOO in",command=self.manager.sim7).grid(sticky="w",column=1,row=c)
			c+=1
			ttk.Button(self.tms_pannel, text="Sim 8: MOO out",command=self.manager.sim8).grid(sticky="w",column=1,row=c)
			c+=1
			ttk.Button(self.tms_pannel, text="Sim 9: MOC out",command=self.manager.sim9).grid(sticky="w",column=1,row=c)
			c+=1

			ttk.Button(self.tms_pannel, text="Sim 9: EURO MOC out",command=self.manager.sim9b).grid(sticky="w",column=1,row=c)
			c+=1

			ttk.Button(self.tms_pannel, text="Sim 10: init failutre",command=self.manager.sim10).grid(sticky="w",column=1,row=c)
			c+=1
			ttk.Button(self.tms_pannel, text="Sim 10b: symbol order checking under rejection",command=self.manager.sim10b).grid(sticky="w",column=1,row=c)
			c+=1
			ttk.Button(self.tms_pannel, text="Sim 11: unable to get out position",command=self.manager.sim11).grid(sticky="w",column=1,row=c)
			c+=1
			ttk.Button(self.tms_pannel, text="Sim 12: accidental flat",command=self.manager.sim12).grid(sticky="w",column=1,row=c)
			c+=1
			ttk.Button(self.tms_pannel, text="Sim 13: accidental more shares",command=self.manager.sim13).grid(sticky="w",column=1,row=c)
			c+=1
			ttk.Button(self.tms_pannel, text="Sim 14: accidental less shares",command=self.manager.sim14).grid(sticky="w",column=1,row=c)
			c+=1
			ttk.Button(self.tms_pannel, text="Sim 15: missing ostats",command=self.manager.sim15).grid(sticky="w",column=1,row=c)
			c+=1
			ttk.Button(self.tms_pannel, text="Sim 16: ppro disconnect",command=self.manager.sim16).grid(sticky="w",column=1,row=c)
			c+=1

			ttk.Button(self.tms_pannel, text="Sim 17: already an position exist",command=self.manager.sim17).grid(sticky="w",column=1,row=c)
			c+=1
		except Exception as e:
			print(e)
	def custom_algo_init(self):

		self.TNV_TAB = ttk.Notebook(self.custom_algo_pannel)
		self.TNV_TAB.place(x=0,rely=0.01,relheight=1,width=640)
		self.frames = {}
		self.algo_groups = []
		self.algos ={}

		self.load_algo_tabs()

		self.create_algo_tabs()
		self.create_each_algos()

		#self.load_all()


		try:
			self.load_all()
		except Exception as e:
			print("LOAD setting faliure",e)

	def load_algo_tabs(self):

		# load each algo, create tab for them
		# for each individual algo, create stuff

		dir_name = "../../custom_algos"
		directory = os.fsencode(dir_name)


		count = 0
		for file in os.listdir(directory):
			filename = os.fsdecode(file)

			strategy = filename[:-4]
			self.algo_groups.append(strategy)
			self.algos[strategy] = {}
			if filename.endswith(".txt"): 
				print(filename)
				a_file = open(dir_name+"/"+filename)
				lines = a_file.read().splitlines()
				for i in lines:

					#"if , then seperate name with despriton"

					if ":" not in i:
						self.algos[strategy][i] = [] 
						self.algos[strategy][i].append(tk.BooleanVar(value=0))
						self.algos[strategy][i].append(tk.IntVar(value=1))
						self.algos[strategy][i].append(tk.IntVar(value=1))
						self.algos[strategy][i].append(tk.BooleanVar(value=0))
						self.algos[strategy][i].append(tk.StringVar(value=""))
					else:
						split = i.split(':')
						i = split[0]
						description = split[1]
						self.algos[strategy][i] = [] 
						self.algos[strategy][i].append(tk.BooleanVar(value=0))
						self.algos[strategy][i].append(tk.IntVar(value=1))
						self.algos[strategy][i].append(tk.IntVar(value=1))
						self.algos[strategy][i].append(tk.BooleanVar(value=0))
						self.algos[strategy][i].append(tk.StringVar(value=description))
	def create_algo_tabs(self):

		for i in self.algo_groups:
			self.frames[i] = tk.Canvas(self.TNV_TAB)
			self.TNV_TAB.add(self.frames[i], text =i)

	def create_each_algos(self):

		for i in self.algo_groups:

			row = 1
			col = 0
			for algo,item in self.algos[i].items():


				label =ttk.Label(self.frames[i], text=algo)
				label.grid(sticky="w",column=col,row=row)
				ttk.Checkbutton(self.frames[i], variable=item[ACTIVE]).grid(sticky="w",column=col+1,row=row)

				# ttk.Label(self.frames[i], text="Risk:").grid(sticky="w",column=col+4,row=row)
				# ttk.Entry(self.frames[i], textvariable=item[RISK],width=4).grid(sticky="w",column=col+5,row=row)

				ttk.Label(self.frames[i], text="Multiplier:").grid(sticky="w",column=col+6,row=row)
				ttk.Entry(self.frames[i], textvariable=item[MULTIPLIER],width=3).grid(sticky="w",column=col+7,row=row)


				ttk.Label(self.frames[i], text="Aggresive:").grid(sticky="w",column=col+2,row=row)
				ttk.Checkbutton(self.frames[i], variable=item[PASSIVE]).grid(sticky="w",column=col+3,row=row)


				if item[DESCRIPTION]!="":
					tip= Tooltip(label,"Algo info",item[DESCRIPTION])

				row+=1

			#print("CUURR",i)
			t = i 
			ttk.Button(self.frames[i], text="Save Config",command= lambda: self.save_all()).grid(sticky="w",column=col,row=row)
			ttk.Button(self.frames[i], text="Load Config",command= lambda: self.load_all()).grid(sticky="w",column=col+2,row=row)

	# def save_setting(self):
	# 	d = {}

	# 	tab =self.TNV_TAB.tab(self.TNV_TAB.select(),"text")
	# 	for algo,item in self.algos[tab].items():
	# 		d[algo]=[]
	# 		for i in item:
	# 			d[algo].append(i.get())
	# 	#print("saving",tab)
	# 	with open('../../custom_algos_config/'+tab+'_setting.json', 'w') as fp:
	# 		json.dump(d, fp)

	# def load_setting(self):
		
	# 	tab =self.TNV_TAB.tab(self.TNV_TAB.select(),"text")
	# 	with open('../../custom_algos_config/'+tab+'_setting.json', 'r') as myfile:
	# 		data=myfile.read()

	# 	# parse file
	# 	d = json.loads(data)
	# 	#print("loading",tab)

	# 	for key,item in d.items():
	# 		#print(self.algos[tab][key])
	# 		try:
	# 			self.algos[tab][key][ACTIVE].set(item[ACTIVE])
	# 			self.algos[tab][key][PASSIVE].set(item[PASSIVE])
	# 			self.algos[tab][key][RISK].set(item[RISK])
	# 			self.algos[tab][key][MULTIPLIER].set(item[MULTIPLIER])
	# 		except:
	# 			pass

	def save_all(self):

		for tab in self.algo_groups:

			try:
				d = {}


				for algo,item in self.algos[tab].items():
					d[algo]=[]

					for i in item:
						d[algo].append(i.get())
				#print("saving",tab)
				with open('../../custom_algos_config/'+tab+'_setting.json', 'w') as fp:
					json.dump(d, fp)
			except Exception as e:
				PrintException("saving error"+tab+item,e)

	def load_all(self):

		for tab in self.algo_groups:

			try:
				with open('../../custom_algos_config/'+tab+'_setting.json', 'r') as myfile:
					data=myfile.read()

				# parse file
				d = json.loads(data)
				#print("loading",tab)

				for key,item in d.items():
					#print(self.algos[tab][key])
					try:
						self.algos[tab][key][ACTIVE].set(item[ACTIVE])
						self.algos[tab][key][PASSIVE].set(item[PASSIVE])
						self.algos[tab][key][RISK].set(item[RISK])
						self.algos[tab][key][MULTIPLIER].set(item[MULTIPLIER])
					except Exception	as e:
						print(key,e)
			except Exception	as e:
				print("loading error ",tab,e)

	def order_complier(self,data,multiplier,risk,aggresive):


		basket = find_between(data,"Basket=",",") 
		symbol = find_between(data,"Order=*","*") 

		new_order = "Order=*"

		z = 0 
		for i in symbol.split(","):
			if z>=1:
				new_order+=","
			k = i.split(":")
			new_order+= k[0]
			new_order+= ":"+str(int(k[1])*multiplier)
			z+=1

		new_order+="*"

		data = "Basket="+basket+","+new_order

		risk__ = risk
		data += ","+"Risk="+str(risk__)+","

		if aggresive:
			data += "Aggresive=1"+","
		else:
			data += "Aggresive=0"+","
		return data


	def get_all_algo_names(self):

		total = {}
		for i in self.algo_groups:
			for algo in self.algos[i].keys():
				#print(algo)

				total[algo] = 0

		return total



	def order_confirmation(self,basket_name,orders):

		#print("RECEVING:",basket_name,orders)


			## PARSE IT AND RE PARSE IT. ? ADD RISK TO IT. 

		name = basket_name


		for i in self.algo_groups:
			for algo,item in self.algos[i].items():
				#print(algo,name,algo in name,item[ACTIVE].get())
				if algo == name[:len(algo)] and item[ACTIVE].get()==True:

					multiplier= item[MULTIPLIER].get()
					for key in orders.keys():
						orders[key] = orders[key]*multiplier
					
					return True,orders,item[RISK].get(),item[PASSIVE].get(),multiplier
					
		return False,None,0,0,1

	def init_quick_spread(self):

		labels =		{"entry":4,\
						"button":5,\
						"checker":8,\
						"long_label":8,\
						"short_label":4,\
					
		}


		self.spread_timer = 0

		spyqqq = {"name":"SPYQQQ","symbol":["SPY.AM","QQQ.NQ"],"ratio":[1,-1],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		gldslv = {"name":"GLDSLV","symbol":["GLD.AM","SLV.AM"],"ratio":[1,-4],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		spytlt = {"name":"TLTSPY","symbol":["TLT.NQ","SPY.AM"],"ratio":[4,-1],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		spyuso = {"name":"SPYUSO","symbol":["SPY.AM","USO.AM"],"ratio":[1,-3],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		
		spygdx = {"name":"GDXSPY","symbol":["GDX.AM","SPY.AM"],"ratio":[6,-1],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		spyiwm = {"name":"SPYIWM","symbol":["SPY.AM","IWM.AM"],"ratio":[10,-12],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
			
		#tlsaqqq = {"name":"TSLAQQQ","symbol":["TSLA.NQ","QQQ.NQ"],"ratio":[1,-2],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		smhqqq = {"name":"SMHQQQ","symbol":["SMH.NQ","QQQ.NQ"],"ratio":[17,-10],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
	
		gdxgdxj = {"name":"GDXGDXJ","symbol":["GDX.AM","GDXJ.AM"],"ratio":[10,-7],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		gdxgld = {"name":"GDXGLD","symbol":["GDX.AM","GLD.AM"],"ratio":[2,-1],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		
		silslv = {"name":"SLVSLI","symbol":["SLV.AM","SIL.AM"],"ratio":[8,-5],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
				

		xleqqq = {"name":"XLEQQQ","symbol":["XLE.AM","QQQ.NQ"],"ratio":[7,-2],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		
		arkkqqq = {"name":"ARKKQQQ","symbol":["ARKK.AM","QQQ.NQ"],"ratio":[4,-1],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		
		#drivqqq = {"name":"DRIVQQQ","symbol":["DRIV.NQ","QQQ.NQ"],"ratio":[12,-1],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}


		spyxlk = {"name":"XLKSPY","symbol":["XLK.AM","SPY.AM"],"ratio":[18,-10],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		spyxlc = {"name":"XLCSPY","symbol":["XLC.AM","SPY.AM"],"ratio":[49,-10],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		spyxli = {"name":"XLISPY","symbol":["XLI.AM","SPY.AM"],"ratio":[36,-10],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		spyxlu = {"name":"XLUSPY","symbol":["XLU.AM","SPY.AM"],"ratio":[55,-10],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		spyxly = {"name":"XLYSPY","symbol":["XLY.AM","SPY.AM"],"ratio":[24,-10],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
	
		#total = [spyqqq,gldslv,tlsaqqq,smhqqq,gdxgdxj]
		AAPLQQQ = {"name":"AAPLQQQ","symbol":["AAPL.NQ","QQQ.NQ"],"ratio":[24,-13],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		AMDNVDA = {"name":"NVDAQQQ","symbol":["NVDA.NQ","QQQ.NQ"],"ratio":[30,-26],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}

		spyijr = {"name":"IJRSPY","symbol":["IJR.AM","SPY.AM"],"ratio":[22,-10],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
	
		spybitq = {"name":"BITQSPY","symbol":["BITQ.AM","SPY.AM"],"ratio":[42,-10],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
	
		spygbtc = {"name":"GBTCSPY","symbol":["GBTC.AM","SPY.AM"],"ratio":[21,-10],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
	
		# tqqqgbtc = {"name":"TQQQGBTC","symbol":["TQQQ.NQ","GBTC.AM"],"ratio":[20,-15],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		# fxixpev = {"name":"FXIXPEV","symbol":["FXI.AM","XPEV.NQ"],"ratio":[2,-1],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		# DISNFLX = {"name":"DISNFLX","symbol":["DIS.NY","NFLX.NQ"],"ratio":[29,-5],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		# JETSXLE = {"name":"JETSXLE","symbol":["JETS.AM","XLE.AM"],"ratio":[41,-12],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
	
		spyfxi = {"name":"FXISPY","symbol":["FXI.AM","SPY.AM"],"ratio":[80,-6],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		fxifutu = {"name":"FXIFUTU","symbol":["FXI.AM","FUTU.NQ"],"ratio":[80,-9],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
		fxipdd = {"name":"FXIPDD","symbol":["FXI.AM","PDD.NQ"],"ratio":[80,-6],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
	



		unguso = {"name":"UNGUSO","symbol":["UNG.AM","USO.AM"],"ratio":[63,-25],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
	
		tltief = {"name":"TLTIEF","symbol":["TLT.NQ","IEF.NQ"],"ratio":[50,-107],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
	
		spymsmo = {"name":"MSOSSPY","symbol":["MSOS.AM","SPY.AM"],"ratio":[66,-10],"status":tk.StringVar(value="Status:"),"timer":tk.IntVar(),"current":tk.IntVar(),"increment":tk.IntVar(value=1),"lock":tk.IntVar(value=0),"max":tk.IntVar(value=100),"passive":tk.IntVar(value=0)}
	
		spy = [spyqqq,spytlt,spyuso,spygdx,spyiwm]
		spy2 = [spyijr,spybitq,spygbtc,spymsmo]
		etf = [spyxlk,spyxlc,spyxli,spyxlu,spyxly]
		qqq = [smhqqq,AAPLQQQ,AMDNVDA,xleqqq,] #arkkqqq
		gld = [gldslv,gdxgdxj,gdxgld,silslv]
		misc =[spyfxi,fxifutu,fxipdd]
		comm = [unguso,tltief]

		total = [spy,spy2,qqq,gld,misc,etf,comm]
		
		self.qs = {}
		for j in total:
			for i in j:
				self.qs[i['name']] = i


		self.load_quick_spread()

		c=1
		t=2

		ttk.Button(self.quick_spread_pannel, text="Save",command=self.save_quick_spread).grid(sticky="w",column=1,row=1)

		style = ttk.Style()
		style.configure("BW.yellow", background="yellow")

		self.qs_subtab = ttk.Notebook(self.quick_spread_pannel)
		#self.qs_subtab.place(x=0,rely=0.05,relheight=1,relwidth=1)
		self.qs_subtab.grid(column=1,row=2)

		self.qs_subp1 = ttk.LabelFrame(self.qs_subtab,text="") 
		self.qs_subp1b = ttk.LabelFrame(self.qs_subtab,text="") 
		self.qs_subp2 = ttk.LabelFrame(self.qs_subtab,text="")
		self.qs_subp3 = ttk.LabelFrame(self.qs_subtab,text="")
		self.qs_subp4 = ttk.LabelFrame(self.qs_subtab,text="")
		self.qs_subp5 = ttk.LabelFrame(self.qs_subtab,text="")
		self.qs_subp6 = ttk.LabelFrame(self.qs_subtab,text="")

		#self.custom_algo_pannel.place(x=0,y=0,height=950,width=350)
		#self.quick_spread_pannel.place(x=0,y=0,height=950,width=350)

		self.qs_subtab.add(self.qs_subp1,text="SPY")
		self.qs_subtab.add(self.qs_subp1b,text="SPY2")
		self.qs_subtab.add(self.qs_subp2,text="QQQ")
		self.qs_subtab.add(self.qs_subp3,text="GLD")
		self.qs_subtab.add(self.qs_subp4,text="MISC")
		self.qs_subtab.add(self.qs_subp5,text="AM")
		self.qs_subtab.add(self.qs_subp6,text="COMM")

		x = 0 

		for j in total:

			if x==0:
				tab = self.qs_subp1
			elif x==1:
				tab = self.qs_subp1b
			elif x==2:
				tab = self.qs_subp2
			elif x==3:
				tab = self.qs_subp3	

			elif x==4:
				tab = self.qs_subp4

			elif x==5:
				tab = self.qs_subp5
			elif x==6:
				tab = self.qs_subp6
			for i in j:

				c=1
				tk.Label(tab, text=i['name']+str(i['ratio'])).grid(sticky="w",column=c,row=t)
				c+=1

				tk.Label(tab, text=" ").grid(sticky="w",column=c,row=t)
				c+=1

				i['status_bar'] = tk.Label(tab, textvariable=i['status'])
				i['status_bar'].grid(sticky="w",column=c,row=t)
				c+=1



				tk.Label(tab, text="TA:").grid(sticky="w",column=c,row=t)
				c+=1

				# row 1 entry
				i['TA']=tk.Entry(tab,textvariable=i['timer'],width=labels['entry'])
				#i['TA']["state"] = DISABLED
				i['TA'].grid(sticky="w",column=c,row=t)	

				c+=1
				i["set_button"] =tk.Button(tab, text="CANCEL",command=lambda s=i: self.as_is(s),width=labels['button'])
				i["set_button"].grid(sticky="w",column=c,row=t)
				


				t+=1 
				c =1 

				tk.Label(tab, text="SET LOCK:",).grid(sticky="w",column=c,row=t)
				c+=1

				tk.Checkbutton(tab,text=" ",variable=i['lock']).grid(sticky="w",column=c,row=t)
				c+=1



				# LOCK:
				tk.Label(tab, text="Increment:").grid(sticky="w",column=c,row=t)
				c+=1

				# row 1 entry
				i['set_entry']=tk.Entry(tab,textvariable=i['increment'],width=labels['entry'])
				i['set_entry']["state"] = DISABLED
				i['set_entry'].grid(sticky="w",column=c,row=t)	
				c+=1

				# row 1 set 

				i["set_button"] =tk.Button(tab, text="SET",command=lambda s=i,side="direct": self.submit_spread(s,side),width=labels['button'])
				i['set_button']["state"] = DISABLED
				i["set_button"].grid(sticky="w",column=c,row=t)
				c+=1

				i["flat_button"] =tk.Button(tab, text="FLAT",command=lambda s=i,side="flat": self.submit_spread(s,side),width=labels['button'])
				#i['flat_button']["state"] = DISABLED
				i["flat_button"].grid(sticky="w",column=c,row=t)
				c+=1


				t+=1
				c=1
				# LOCK:
				# tk.Label(self.quick_spread_pannel, text="SET LOCK:").grid(sticky="w",column=c,row=t)
				# c+=1


				tk.Label(tab, text="PASSIVE:").grid(sticky="w",column=c,row=t)
				c+=1
				# row 1 cheker 
				i["passive_button"] = tk.Checkbutton(tab,text=" ",variable=i['passive'])
				i['passive_button']["state"] = DISABLED
				i['passive_button'].grid(sticky="w",column=c,row=t)
				c+=1


				tk.Label(tab, text="Holding:").grid(sticky="w",column=c,row=t)
				c+=1

				# row 1 entry
				i['set_current']=tk.Entry(tab,textvariable=i['current'],width=labels['entry'])
				i['set_current']["state"] = DISABLED
				i['set_current'].grid(sticky="w",column=c,row=t)	
				c+=1


				# LOCK:
				tk.Label(tab, text="Max:").grid(sticky="w",column=c,row=t)
				c+=1

				# row 1 entry
				i['set_max']=tk.Entry(tab,textvariable=i['max'],width=labels['entry'])
				i['set_max']["state"] = DISABLED
				i['set_max'].grid(sticky="w",column=c,row=t)	
				c+=1



				# tk.Label(self.quick_spread_pannel, text="   ",width=5).grid(sticky="w",column=c,row=t)
				# c+=1
				# # row 1 flat 
				# tk.Button(self.quick_spread_pannel, text="FLAT", bg="yellow",command=lambda s=i,side="flat": self.submit_spread(s,side),width=labels['button']).grid(sticky="w",column=c,row=t)
				# c+=1



				t+=1

				c = 1

				# LONG:
				tk.Label(tab, text="LONG:").grid(sticky="w",column=c,row=t)
				c+=1

				tk.Button(tab, text="+",command=lambda s=i,side="long": self.submit_spread(s,side),width=labels['button']).grid(sticky="w",column=c,row=t)
				c+=1
				tk.Button(tab, text="-",command=lambda s=i,side="short": self.submit_spread(s,side),width=labels['button']).grid(sticky="w",column=c,row=t)
				c+=1

				#t+=1

				#c = 1

				# LONG:
				tk.Label(tab, text="SHORT:").grid(sticky="w",column=c,row=t)
				c+=1

				tk.Button(tab, text="+",command=lambda s=i,side="short": self.submit_spread(s,side),width=labels['button']).grid(sticky="w",column=c,row=t)
				c+=1
				tk.Button(tab, text="-",command=lambda s=i,side="long": self.submit_spread(s,side),width=labels['button']).grid(sticky="w",column=c,row=t)
				c+=1

				
				c=1
				t+=1
				tk.Label(tab, text="      ").grid(sticky="w",column=c,row=t)

				i['lock'].trace("w", lambda *_, d=i: trace_func(d) )


				t+=1
				c+=1
				## ADD TRACE


			x+=1

if __name__ == '__main__':

	root = tk.Tk() 
	root.title("GoodTrade Algo Manager v5") 
	#root.geometry("1380x780")
	root.geometry("1570x1280")
	UI(root)
	# root.minsize(1600, 1000)
	# root.maxsize(1800, 1200)
	root.mainloop() 