

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

#print(timestamp_seconds("13:23:46"))