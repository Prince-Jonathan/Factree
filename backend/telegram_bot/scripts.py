def get_lot_code(lot):
	char = len(lot)
	if char < 6:
		zeros = 6 - char
		lot = lot[0:2]+"0"*zeros+lot[2:]
	return lot.upper()

def get_vin(vin):
	char = len(vin)
	if char < 17:
		underscores = 17 - char
		vin = "_" *underscores + vin[:char]
	return vin