

a=[1,2,3,4,5,6,7,8,9,10]
b=[5,3,4,5,2,3,4,5,6,2]

def range_eval(highs,lows):

	#look back 30 minutes. report the one with least amount of change.

	a=highs[-30:]
	b=lows[-30:]

	count_a=0
	init = a[0]
	for i in a:
		if i>init:
			init = i
			count_a+=1

	count_b=0
	init = b[0]
	for i in b:
		if i<init:
			init = i
			count_b+=1

	diff = abs(count_a-count_b)

	return round(diff/30,2)

print(range_eval(a,b))