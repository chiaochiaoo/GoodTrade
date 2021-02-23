#from pywinauto import Desktop
from win32gui import GetWindowText, GetForegroundWindow
import sys
import win32gui
import os
#from pynput.keyboard import Key, Controller
import time
import ctypes

def winEnumHandler( hwnd, id_ ):
	#window = "PPro8 nuna-0.23.2"
	window = "PPro8 nuna-0.23.2"
	if win32gui.IsWindowVisible( hwnd ):
		#print (hex(hwnd), win32gui.GetWindowText( hwnd ))
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



import ctypes
from ctypes import wintypes
import time

user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0

# msdn.microsoft.com/en-us/library/dd375731
VK_TAB  = 0x09
VK_MENU = 0x12

# C struct definitions

wintypes.ULONG_PTR = wintypes.WPARAM

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)

def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT, # nInputs
                             LPINPUT,       # pInputs
                             ctypes.c_int)  # cbSize

# Functions

def PressKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def AltTab():
    """Press Alt+Tab and hold Alt key for 2 seconds
    in order to see the overlay.
    """
    PressKey(VK_MENU)   # Alt
    time.sleep(2)
    PressKey(VK_TAB)    # Tab
    ReleaseKey(VK_TAB)  # Tab~
    time.sleep(2)
    ReleaseKey(VK_MENU) # Alt~

import clipboard
import pyperclip

if __name__ == "__main__":
	time.sleep(1)
	# AltTab()	
	# AltTab()	
	# AltTab()	
	# AltTab()	


	# clipboard.copy("abc")  # now the clipboard content will be string "abc"
	# clipboard.paste()		

	pyperclip.copy('xxx')
	pyperclip.paste()