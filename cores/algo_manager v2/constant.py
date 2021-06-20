#Spirits of the machine, accept my pleas, And walk amidst the gun, and fire it true.


#SYMBOL PARAMETERS
BID = "bid"
ASK = "ask"
RESISTENCE="resistence"
SUPPORT="support"
OPEN="open" 
HIGH="high"
LOW="low" 
TIMESTAMP="timestamp"
PREMARKETHIGH="phigh"
PREMARKETLOW="plow"


#STATS
ATR ='ATR'
OHAVG='OHavg'
OHSTD = 'OHstd'
OLAVG = 'OLavg'
OLSTD ='OLstd'

#TP PARAMETER
AUTORANGE = "AR"
AUTOMANAGE = "AM"
RELOAD = "reload"
SELECTED = "selected"
ANCART_OVERRIDE = "ancartoverride"

FLATTENTIMER = "flattentimer"

TIMER = "timer"
ACTRISK="actrisk"
ESTRISK="estrisk"
RISK_RATIO = "risk_ratio"
SIZE_IN = "size_in"

CURRENT_SHARE = "CURRENT_SHARE"
TARGET_SHARE = "TARGET_SHARE"
INPUT_TARGET_SHARE ="INTPU_SHARE"
RISK_PER_SHARE = "RISK_PER_SHARE"
AVERAGE_PRICE = "AVERAGE_PRICE"
LAST_AVERAGE_PRICE = "Last_average_price"
UNREAL = "UNREAL"
UNREAL_PSHR = "UNREAL_PSHR" 
REALIZED =  "REALIZED"
TOTAL_REALIZED = "TOTAL_REALIZED" 
STOP = "Stop"
STOP_LEVEL = "Stop_level"
SYMBOL = "Symbol"
MIND = "MIND"


BREAKPRICE = "Breakprice"

PXT1 = "tpx1"
PXT2 = "tpx2"
PXT3 = "tpx3"
PXT4 = "tpx4"
PXT5 = "tpx5"
PXTF = "tpxF"

TRIGGER_PRICE_1 = "Trigger_price_1"
TRIGGER_PRICE_2 = "Trigger_price_2"
TRIGGER_PRICE_3 = "Trigger_price_3"
TRIGGER_PRICE_4 = "Trigger_price_4"
TRIGGER_PRICE_5 = "Trigger_price_5"
TRIGGER_PRICE_6 = "Trigger_price_6"
TRIGGER_PRICE_7 = "Trigger_price_7"
TRIGGER_PRICE_8 = "Trigger_price_8"
TRIGGER_PRICE_9 = "Trigger_price_9"

STATUS = "Status"
POSITION="Position"
MANASTRAT = "ManaStart"
ENSTRAT = "EntryStrat"
ENTYPE = "Entrytype"
ENTRYPLAN = "EntryPlan"
MANAGEMENTPLAN = "ManagementPlan"
TRADING_PLAN ="TradingPlan"
RISKTIMER = "Risktimer"

#TRIGGER PARA
SYMBOL_DATA = "symbol_data"
TP_DATA = "TP_DATA" 

#Algo STATUS
DONE = "Done"
PENDING = "Pending"
DEPLOYED = "DEPLOYED"
MATURING = "Maturing"
RUNNING = "Running"
REJECTED = "Rejected"
CANCELED= "Canceled"
#orders sies
LONG  = "Long"
SHORT = "Short"


#Entry Type
INSTANT=      '  Instant'
INCREMENTAL = 'Incrmntl'

#Entry Plan
BREAISH =   "  Bearish"
BULLISH =   "  Bullish"
BREAKUP =   " Break Up"
BREAKDOWN = " Break Dn"
BREAKANY =  "Break Any"
DIPBUY = "Dipbuy"
RIPSELL = "Ripsell"
FADEANY = "Fade Any"
BREAKFIRST = "Break First"
#MANA Plan
NONE =          "NONE"
THREE_TARGETS = "Three tgts "
SMARTTRAIL =  "SmartTrail" 
ANCARTMETHOD =  "AC METHOD"
ONETOTWORISKREWARD = "1:2 Exprmntl"

ONETOTWORISKREWARDOLD = "1:2 RiskReward"
##### ORDER TYPE ####

BUY = "Buy"
SELL = "Sell"
FLATTEN = "Flatten"

LIMITBUY = "Litmit Buy" 
LIMITSELL = "Limit Sell"



##COLOR

GREEN = "#97FEA8"
DEFAULT = "#d9d9d9"
LIGHTYELLOW = "#fef0b8"
YELLOW =  "#ECF57C"
VERYLIGHTGREEN = "#ecf8e1"
LIGHTGREEN = "#97FEA8"
STRONGGREEN = "#3DFC68"
STRONGRED = "#FC433D"
DEEPGREEN = "#059a12"


			
	# def deploy_orders(self,orders):

	# 	coefficient = 1
	# 	action = ""
	# 	if self.tradingplan.data[POSITION] == LONG:
	# 		action = LIMITSELL

	# 	elif self.tradingplan.data[POSITION] == SHORT:
	# 		action = LIMITBUY
	# 		coefficient = -1

	# 	for key in sorted(orders.keys()):
	# 		if orders[key]>0:
	# 			price = round(self.price+coefficient*self.gap*key,2)
	# 			share = orders[key]
	# 			self.ppro_out.send([action,self.symbol_name,price,share,"Exit price "])


