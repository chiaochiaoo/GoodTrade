from Triggers import *
from Strategy import *
from Tradingplan import *
from Symbol import *


#### Trading plan is where all the triggers, conditions are.###
#### Orders on a symbol create a basic trading plan. and modifying it chainging the plan.


if __name__ == '__main__':

	#TEST CASES for trigger.
	
	aapl = Symbol("aapl")
	TP = TradingPlan(aapl)
	aapl.set_tradingplan(TP)
	aapl.set_phigh(12)
	aapl.set_plow(10)

	b = BreakDown(0)
	#b = BreakUp(0)
	TP.set_EntryStrategy(b)
	TP.start_EntryStrategy()

	#TP.add_trigger(buyTrigger)
	
	aapl.update_price(10,10,0)
	aapl.update_price(11,11,1)
	aapl.update_price(12,12,2)
	aapl.update_price(13,13,3)
	aapl.update_price(14,14,4)
	aapl.update_price(15,15,5)
	##### DECRESE#######
	aapl.update_price(5,5,6)
	aapl.update_price(13,13,7)

	aapl.update_price(10,10,8)
	###### INCREASE #############
	aapl.update_price(11,11,9)
	aapl.update_price(12,12,10)
	aapl.update_price(13,13,11)
	aapl.update_price(14,14,12)
	aapl.update_price(15,15,13)
	aapl.update_price(16,16,14)
	aapl.update_price(17,17,15)
	aapl.update_price(18,18,16)
	aapl.update_price(19,19,17)

