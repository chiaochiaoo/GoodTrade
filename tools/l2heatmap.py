from tkinter import Tk, Canvas, PhotoImage, mainloop
from math import sin
import threading
import time
WIDTH, HEIGHT = 640, 480

window = Tk()
canvas = Canvas(window, width=WIDTH, height=HEIGHT, bg="#000000")
canvas.pack()
img = PhotoImage(width=WIDTH, height=HEIGHT)
canvas.create_image((WIDTH/2, HEIGHT/2), image=img, state="normal")

def hex_to_string(int):
	a = hex(int)[-2:]
	a = a.replace("x","0")

	return a


def hexcolor(level):
	code = int(510*(level))
	print(code,"_")
	if code >255:
		first_part = code-255
		return "#FF"+hex_to_string(255-first_part)+"00"
	else:
		return "#FF"+"FF"+hex_to_string(255-code)
#hexcolor(i/100)
def change(p):
	time.sleep(1)
	for i in range(1,100):
		for x in range((p-1) * WIDTH,p*WIDTH):
			y = int((HEIGHT+i*10)/2 + (HEIGHT+i*10)/4 * sin(x/80.0))
			img.put("red", (x//4,y))
		time.sleep(2)


change1 = threading.Thread(name="Reiceive info",target=change,args=(1,), daemon=True)
change1.start()
change2 = threading.Thread(name="Reiceive info",target=change,args=(2,), daemon=True)
change2.start()
change3 = threading.Thread(name="Reiceive info",target=change,args=(3,), daemon=True)
change3.start()
change4 = threading.Thread(name="Reiceive info",target=change,args=(4,), daemon=True)
change4.start()
mainloop()


