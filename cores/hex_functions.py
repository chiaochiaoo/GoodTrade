
import tkinter as tk                     
from tkinter import ttk 

def hex_to_string(int):
	a = hex(int)[-2:]
	a = a.replace("x","0")

	return a


#want . -1 to 1.  Extreme Green to Extreme Red. 
def hexcolor_green_to_red(level):

	if level>0:
		code = int(510*(level))
		#print(code,"_")
		if code >255:
			first_part = code-255
			return "#FF"+hex_to_string(255-first_part)+"00"
		else:
			return "#FF"+"FF"+hex_to_string(255-code)

	else:
		code = int(255*(abs(level)))
		first_part = 255-code

		return "#"+hex_to_string(first_part)+"FF"+hex_to_string(first_part)

			#return "#"+hex_to_string(255-code)+"FF"+"FF"
#print(times#tamp_seconds("13:23:46"))

#hex color test. to refect serverity.
if __name__ == '__main__':


	root = tk.Tk()
	k=1
	for i in range(10,-1,-1):
		print(-i/10)
		a=tk.Label(root ,text=-i,width=5,background=hexcolor_red(-i/10))
		a.grid(column=1,row=k)
		k+=1
	for i in range(0,10):

		a=tk.Label(root ,text=i,width=5,background=hexcolor_red(i/10))
		a.grid(column=1,row=k)
		k+=1
	root.mainloop()