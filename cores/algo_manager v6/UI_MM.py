from pannel import *
from constant import *
from Util_functions import *
from UI_custom_algo import * 
import time
from TickerMM import *

try:
	from ttkwidgets.frames import Tooltip
except ImportError:
	import pip
	pip.main(['install', 'ttkwidgets'])
	from ttkwidgets.frames import Tooltip


FIELDS_PER_ROW = 6 
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


		self.button_commands = {
			"start_strategy": self.start_strategy,
			"stop_strategy": self.stop_strategy,
			# Add more as needed
		}
		
		self.init_pannel()

		#self.init_entry_pannel()

		# self.custom_algo_init()

	def start_strategy(self):
		print(f"[{self.mm.ticker}] Strategy started")

	def stop_strategy(self):
		print(f"[{self.mm.ticker}] Strategy stopped")

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

		ttk.Label(self.system_pannel, text="Disaster mode:").grid(sticky="w",column=1,row=row,padx=10)

		try:
			ttk.Checkbutton(self.system_pannel, variable=self.manager.disaster_mode).grid(sticky="w",column=2,row=row)
		except:
			pass 



		row +=1
		ttk.Label(self.system_pannel, text="Ticker:").grid(row=row, column=1,  sticky="w",padx=10)
		self.ticker_var = tk.StringVar()
		ttk.Entry(self.system_pannel, textvariable=self.ticker_var, width=15).grid(row=row, column=2,sticky="w")

		ttk.Button(self.system_pannel, text="Load/Create", command=self.load_ticker_tab).grid(row=row, column=3)


		self.ticker_var.set('DEMO.TO')
		self.load_ticker_tab()


	def on_mode_toggle(self, changed_name):
		# Ensure only one mode checkbox is True
		for name in MODE_CHECKBOXES:
			if name != changed_name:
				var, _ = self.mm.vars.get(name, (None, None))
				if var:
					var.set(0)

	def load_ticker_tab(self, force=True):
		ticker = self.ticker_var.get().strip()
		if not ticker:
			return

		# Load or create TickerMM
		if os.path.exists(f"configs/{ticker}.json") and not force:
			mm = TickerMM(ticker)
		else:
			mm = TickerMM(ticker, override=True)
			mm.save()

		self.mm = mm

		# Create new tab
		tab = ttk.Frame(self.marketmaking_notebook)
		self.marketmaking_notebook.add(tab, text=ticker)

		# --- Step 1: Group schema entries by section ---
		sections = {}
		for entry in CONFIG_SCHEMA:
			sec = entry.get("section", "status")
			sections.setdefault(sec, []).append(entry)

		section_frames = {}
		row_counter = 0

		for sec_name, entries in sections.items():
			# Section title
			collapsible = CollapsibleSection(tab, title=sec_name.upper())
			collapsible.grid(row=row_counter, column=0, columnspan=FIELDS_PER_ROW * 2, sticky="w", padx=10)

			section_frame = collapsible.content  # actual frame for widgets
			section_frames[sec_name] = section_frame
			section_frames[sec_name] = section_frame

			row_counter += 2

			row_tracker = {}  # row -> current column count

			for entry in entries:
				name = entry["name"]
				label = entry["label"]
				if name == "Ticker":
					continue

				entry_type = entry["type"]
				readonly = entry.get("readonly", False)
				options = entry.get("options")
				var = mm.vars[name][0] if name in mm.vars else None

				row = entry.get("row", 0)
				col = row_tracker.get(row, 0)

				if entry_type == "button":
					# Button takes 1 cell directly
					cmd_name = entry.get("command")
					cmd_func = self.button_commands.get(cmd_name)
					widget = ttk.Button(section_frame, text=label, command=cmd_func)
					widget.grid(row=row, column=col, sticky="w", padx=5, pady=5)
					row_tracker[row] = col + 1
				else:
					# Label
					ttk.Label(section_frame, text=f"{label}:").grid(
						row=row, column=col * 2, sticky="e", padx=5, pady=5
					)
					# Widget
					if readonly:
						widget = ttk.Entry(section_frame, textvariable=var, state="readonly")
					elif entry_type == "bool":
						if name in MODE_CHECKBOXES:
							widget = ttk.Checkbutton(section_frame, variable=var, command=lambda n=name: self.on_mode_toggle(n))
						else:
							widget = ttk.Checkbutton(section_frame, variable=var)
					elif options:
						widget = ttk.Combobox(section_frame, textvariable=var, values=options, state="readonly", width=14)
					else:
						widget = ttk.Entry(section_frame, textvariable=var, width=14)

					widget.grid(row=row, column=col * 2 + 1, sticky="w", padx=5, pady=5)
					row_tracker[row] = col + 1

		# Save Button at the bottom of the last section
		ttk.Button(tab, text="Save", command=lambda: self.mm.save()).grid(
			row=row_counter + 10, column=0, columnspan=FIELDS_PER_ROW * 2, pady=15, padx=10, sticky="w"
		)



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

		# self.sub_pannel = ttk.LabelFrame(self.root,text="") 
		# self.sub_pannel.place(x=0,y=300,height=950,width=350)

		# self.SUB_TAB = ttk.Notebook(self.sub_pannel)
		# self.SUB_TAB.place(x=0,rely=0.00,relheight=1,width=640)

		# self.quick_spread_pannel = ttk.LabelFrame(self.SUB_TAB,text="") 

		# self.custom_algo_pannel = ttk.LabelFrame(self.SUB_TAB,text="") 

		# self.tms_pannel = ttk.LabelFrame(self.SUB_TAB,text="") 

		# self.SUB_TAB.add(self.custom_algo_pannel,text="AlgoAuthorization")
		# self.SUB_TAB.add(self.quick_spread_pannel,text="QuickSpread")

		# self.SUB_TAB.add(self.tms_pannel,text="TMS Simulation")

		# self.TNV_TAB = ttk.Notebook(self.custom_algo_pannel)
		# self.TNV_TAB.place(x=0,rely=0.01,relheight=1,width=640)

		self.system_pannel = ttk.LabelFrame(self.root,text="System")
		self.system_pannel.place(x=10,y=10,height=250,width=350)

		self.control_pannel = ttk.LabelFrame(self.root,text="Control") 
		self.control_pannel.place(x=360,y=10,height=200,width=300)

		self.gateway_pannel = ttk.LabelFrame(self.root,text="Default Gateway") 
		self.gateway_pannel.place(x=560,y=10,height=50,width=300)

		# self.badsymbol_pannel = ttk.LabelFrame(self.root,text="Bad Symbols") 
		# self.badsymbol_pannel.place(x=860,y=10,height=50,width=300)

		self.performance_pannel = ttk.LabelFrame(self.root,text="Performance") 
		self.performance_pannel.place(x=360,y=70,height=200,width=700)

		self.notification_pannel = ttk.LabelFrame(self.root,text="Notification") 
		self.notification_pannel.place(x=1000,y=70,height=200,width=360)

		# self.filter_pannel = ttk.LabelFrame(self.root,text="Algorithms Management") 
		# self.filter_pannel.place(x=360,y=200,height=60,width=1300)

		self.mm_pannel = ttk.LabelFrame(self.root,text="MarketMaking") 
		self.mm_pannel.place(x=10,y=270,height=950,width=1350)

		self.marketmaking_notebook = ttk.Notebook(self.mm_pannel)
		self.marketmaking_notebook.place(x=0,rely=0,relheight=1,relwidth=1)


		self.init_system_pannel()
		self.init_performance_pannel()

		#self.init_strategy_filter()
		#self.init_deployment_pannel()

		self.init_control_pannel()

		# self.init_gateway()
		# self.init_tms_simulation()

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

	def get_current_display(self):



		all_strat = []

		for symbol in range(0,self.algo_limit):
			if self.tk_labels_basket[symbol]['Strategy']['text']!="":
				all_strat.append(self.tk_labels_basket[symbol]['Strategy']['text'])

		all_strat = list(set(all_strat))

		print(all_strat)

		return all_strat



if __name__ == '__main__':

	root = tk.Tk() 
	root.title("GoodTrade Algo Manager Market Making v1") 
	#root.geometry("1380x780")
	root.geometry("1520x1280")
	UI(root)
	# root.minsize(1600, 1000)
	# root.maxsize(1800, 1200)
	root.mainloop() 