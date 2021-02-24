#from pywinauto import Desktop
from win32gui import GetWindowText, GetForegroundWindow
import sys
import win32gui
import win32con
import os
import keyboard
#from pynput.keyboard import Key, Controller
import time
import ctypes

def winEnumHandler( hwnd, id_ ):
	#window = "Chiao (DESKTOP-DG05CS8) - VNC Viewer"
	window = "PPro8 nuna-0.23.2"
	if win32gui.IsWindowVisible( hwnd ):
		print (hex(hwnd), win32gui.GetWindowText( hwnd ))
		if win32gui.GetWindowText( hwnd ) == window:
			id_[0] = hwnd

#PPro8.exe -server=OxfordCircus -pproapi_port=8080
def openppro():
	filepath = "C:\\Users\\Chiao\\Desktop\\PPro8_Production_api.cmd - Shortcut"
	os.startfile(filepath)
	time.sleep(2)
	keyboard.press_and_release('enter')

def bringwindow():
	id_ = [0]
	win32gui.EnumWindows( winEnumHandler, id_ )
	print(id_[0])
	win32gui.ShowWindow(id_[0], win32con.SW_RESTORE) 
	win32gui.SetForegroundWindow(id_[0])
	time.sleep(1)

def terminateppro():
	os.system("taskkill /im PPro8.exe /f /t")


#bringwindow()
def login():
	user32 = ctypes.WinDLL('user32', use_last_error=True)
	time.sleep(1)

#bringwindow()
#login()
#win32gui.EnumWindows( winEnumHandler, None )


terminateppro()
time.sleep(5)
openppro()
time.sleep(5)
bringwindow()