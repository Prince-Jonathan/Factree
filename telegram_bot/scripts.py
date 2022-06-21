import datetime

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

def get_storage_loc(skd_storage_data, lot):
	'''return location of lot at storage area'''
	x = skd_storage_data.where(skd_storage_data==lot.upper()).dropna(how="all").dropna(axis="columns")
	print(skd_storage_data)
	print('xxxxx\n\n',x)
	loc = "{y}{x}".format(x=x.index[0], y=x.columns[0])
	return loc

def send_error_telegram(update, context,msg):
	context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
	context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))

def format_date(temp):
	return datetime.datetime.strptime(_from,'%y%m%d').strftime('%Y-%m-%d')	