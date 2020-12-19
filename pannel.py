
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
			label["background"] = "green"
