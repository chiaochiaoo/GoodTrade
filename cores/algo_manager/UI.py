class UI(pannel):
	def __init__(self,root):

		self.root = root

		self.tk_strings=["algo_status","realized","shares","unrealized","unrealized_pshr","average_price"]
		self.tk_labels=["symbol","algo_status","description","AR","break_at","stoplevel","position","act_r/est_r","average_price","shares","AM","pxtgt1","pxtgt2","pxtgt3","unrealized_pshr","unrealized","realized"]

		self.init_pannel()
	def init_pannel(self):
		self.labels = {"Symbol":10,\
						"Algo states":10,\
						"MIND":12,\
						"Strategy":10,\
						"Config":12,\
						"AR":4,\
						"Sup":6,\
						"Res":6,\
						"PosMan":8,\
						"Configm":8,\
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
	