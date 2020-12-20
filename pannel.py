import tkinter as tk 
class pannel:


	def rebind(self,canvas,frame):
		canvas.update_idletasks()
		canvas.config(scrollregion=frame.bbox()) 
		
	def label_default_configure(self,label):
		label.configure(activebackground="#f9f9f9")
		label.configure(activeforeground="black")
		label.configure(background="#d9d9d9")
		label.configure(disabledforeground="#a3a3a3")
		label.configure(relief="ridge")
		label.configure(foreground="#000000")
		label.configure(highlightbackground="#d9d9d9")
		label.configure(highlightcolor="black")

	def status_change_color(self,text,label):

		if text.get() == "Connecting":
			label["background"] = "#ECF57C"
		elif text.get() == "Unfound":
			label["background"] = "red"
		elif text.get() == "Disconnected":
			label["background"] = "red"
		elif text.get() == "Connected":
			label["background"] = "#97FEA8"

	def labels_creator(self,frame):
		for i in range(len(self.labels)): #Rows
			self.b = tk.Button(frame, text=self.labels[i],width=self.width[i])#command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=1, column=i)
