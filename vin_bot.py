'''
Return the VIN of a specific lot number
'''
import os
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters,  InlineQueryHandler
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, KeyboardButton, ReplyKeyboardMarkup
import logging
import pandas as pd
import numpy as np
import tabula
from telegram_bot.app import engine
import datetime
from telegram_bot.scripts import get_lot_code, get_vin, get_storage_loc, send_error_telegram

PORT = int(os.environ.get('PORT', 5000))
TOKEN = '5105572453:AAGjKUhrM_pKVY-e6ghoWhFWIRo4-Db4vxc'
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = loggin.getLogger(__name__)

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

station_names = ['T1','T4','T5','T6','INSP1', 'INSP2','INSP3','INSP4']
cbu_yard_names = ['Lot1','Lot2','Lot3','Lot4','Lot5', 'Lot6','Lot7','Lot8','Lot9']

#start command function
def start(update: Update, context: CallbackContext):
    print(update)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Let's start...Safety first☝️!")

#start command handler
start_handler = CommandHandler('start', start)


#document import function
def import_doc(update: Update, context: CallbackContext):
    # download file to temp.xlsx 
    sheet_no = 0
    if update.message.caption.upper() == 'VIN':
        with open("vin_temp", 'wb') as f:
            context.bot.get_file(update.message.document).download(out=f)
        # df = pd.read_excel("vin_temp.xlsx", index_col=0, skiprows=range(0,3), usecols="A:L")
        try:
            temp = pd.ExcelFile(r"vin_temp")
            df = pd.DataFrame()
            # pick the right sheet with vin list
            for sheet in temp.sheet_names:
                if ("VIN" in sheet.upper()) or ("TTMG" in sheet.upper()):
                    sheet_no +=1
                    # x = df.parse(sheet, index_col=0, skiprows=range(0,3), usecols="A:L")
                    data = temp.parse(sheet)
                    # select header row
                    header_row = data.where(data=='Lot No.').dropna(how='all').dropna(axis="columns").index[0]
                    data.columns=data.iloc[header_row]
                    data.drop(range(0, header_row+1), inplace=True)
                    data.set_index("Lot No.", inplace=True)
                    # format headers
                    data.columns = data.columns.str.replace(" ", "_",regex=False)
                    data.columns = data.columns.str.lower()
                    data.columns = data.columns.str.replace(".","",regex=False)
                    data.index.name = data.index.name.lower().replace(" ","_")[:-1]
                    # select some columns
                    data = data[['job_no','skid_no','vin_no','katashiki','colour', 'engine_no', 'engine_cap', 'container_no']]
                    # remove zero rows, if any
                    data = data.loc[(data!=0).any(axis=1)]
                    df= pd.concat([data,df])
                print(f"No. of accessed sheets: {sheet_no}")
        except:
            df = pd.DataFrame()
            tables = tabula.read_pdf(r"vin_temp", pages = "all",stream=True,area=(138.391,15.26,562.508,794.036))
            for temp in tables:
                temp.columns = temp.columns.str.replace(" ", "_",regex=False)
                temp.columns = temp.columns.str.lower()
                temp.columns = temp.columns.str.replace(".","",regex=False)
                temp.set_index("lot_no", inplace=True)
                temp = temp[['job_no','skid_no','vin_no','katashiki','colour', 'engine_no', 'engine_cap', 'container_no']]
                df = pd.concat([temp, df])
        try:
            # delete temporary file
            # os.remove(r"vin_temp")
            # merge database vin with new vin = merged_list
            dvin = pd.DataFrame()
            with engine.connect() as conn, conn.begin():
                dvin = pd.read_sql_query("SELECT * FROM vin_list;", conn, index_col="lot_no")
                dvin = dvin.drop_duplicates().sort_index(axis=0)
            print("query for database vin list: success")
            print("Existing database list:")
            print(dvin)
        except:
            print("query for database vin list: failed")
        try:
            # merge vin list and drop duplicates
            if not dvin.empty:
                merged_list = pd.concat([dvin, df]).drop_duplicates().sort_index(axis=0)
            else:
                merged_list = df.sort_index(axis=0).drop_duplicates().sort_index(axis=0)
            print("merged list:")
            print(merged_list)
            # commit dataframe to sql database
            # code can be refactored to consolidate vins and then pass to database
            merged_list.to_sql("vin_list", engine, if_exists='replace')
            print("Database vin list updated")
            with engine.connect() as con:
                con.execute('ALTER TABLE "vin_list" ADD PRIMARY KEY ("lot_no");')
            print('Database primary key: set')
            # send success confirmation to telegram
            context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text="alright...done☺️👍")
        except:
            print("An error occured: Inserting into database")
            context.bot.send_message(chat_id=update.effective_chat.id,reply_to_message_id=update.message.message_id,  text="Something went wrong...🤔")
            context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))

    # importing storage area updates
    if update.message.caption.upper() == 'STORAGE AREA':
        with open("storage_area_temp.xlsx", 'wb') as f:
            context.bot.get_file(update.message.document).download(out=f)
        # df = pd.read_excel("storage_area_temp.xlsx", index_col=0, skiprows=range(0,3), usecols="A:L")
        df = pd.read_excel(r"C:\Users\LogisticsUser02\Documents\VIN_import\backend\storage_area_temp.xlsx", sheet_name="SKD Storage", header=2, usecols=['#','A','B','C','D','E','F','G','H','I','J','K'], index_col=0, nrows=5)
        df.index.name = 'row'
        os.remove(r"C:\Users\LogisticsUser02\Documents\VIN_import\backend\storage_area_temp.xlsx")
        try:
            # commit dataframe to sql database
            df.to_sql("skd_storage", engine, if_exists='replace')
            print("Database SKD Storage updated")
            # send success confirmation to telegram
            context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text="alright...done☺️👍")

        except:
            print("An error occured: Inserting into database")
            context.bot.send_message(chat_id=update.effective_chat.id,reply_to_message_id=update.message.message_id,  text="Something went wrong...🤔")
            context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))

    if update.message.caption.upper() == 'SEQ':
        print('Attempting to develop container receiving sequence...')
        with open("vin_sequence", 'wb') as f:
            context.bot.get_file(update.message.document).download(out=f)
            # df = pd.read_excel("vin_sequence.xlsx", index_col=0, skiprows=range(0,3), usecols="A:L")
        df = pd.DataFrame()
        try:
            temp = pd.ExcelFile(r"vin_sequence")
            # pick the right sheet with vin list
            for sheet in temp.sheet_names:
                if ("VIN" in sheet.upper()) or ("TTMG" in sheet.upper()):
                    sheet_no +=1
                    # x = df.parse(sheet, index_col=0, skiprows=range(0,3), usecols="A:L")
                    data = temp.parse(sheet)
                    # select header row
                    header_row = data.where(data=='Lot No.').dropna(how='all').dropna(axis="columns").index[0]
                    data.columns=data.iloc[header_row]
                    data.drop(range(0, header_row+1), inplace=True)
                    # remove zero rows, if any
                    data = data.loc[(data!=0).any(axis=1)]
                    duplicates = data[data.duplicated(subset=['Lot No.'])]['Lot No.']
                    if duplicates.count():
                        context.bot.send_message(chat_id=update.effective_chat.id, text="VIN List has duplicates of: \n {lots}".format(lots=duplicates.to_string()))
                    df= pd.concat([data,df])
                print(df)
                print(f"No. of accessed sheets: {sheet_no}")
        except:
            tables = tabula.read_pdf(r"vin_sequence", pages = "all",stream=True,area=(138.391,15.26,562.508,794.036))
            for temp in tables:
                df = pd.concat([temp, df])
    # try:
        # delete temporary file
        #os.remove(r"vin_sequence")

        # generate container receiving sequence
        df.sort_values(by='Lot No.', ascending=False, inplace=True)
        sequence = df['Container No.'].drop_duplicates()
        # sequence.to_clipboard(index=False)
        sequence = sequence.to_string(index=False)
        context.bot.send_message(chat_id=update.effective_chat.id, text=sequence)
    # except:
    #     print("Generating container receiving sequence: failed")
    #     context.bot.send_message(chat_id=update.effective_chat.id, text="There was a problem generating container receiving sequence😒")
    #     context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))

#implementing import_doc handler
import_doc_handler = MessageHandler(Filters.document, import_doc)

#receiving lot number and returning vin
def vin(update: Update, context: CallbackContext):
    for lot in context.args:
        lot = get_lot_code(lot)
        try:
            df = pd.read_sql_query("SELECT vin_no FROM vin_list WHERE lot_no = \'%s\';"%lot.upper(), 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
            vin = (df.iloc[0,0])
            context.bot.send_message(chat_id=update.effective_chat.id, text=lot.upper()+": "+vin)
            print(f"Requested vin of {lot}:{vin}")
        except:
            print("VIN of queried lot does not exist")
            context.bot.send_message(chat_id=update.effective_chat.id, text="Lot {lot} is not available 😒".format(lot=lot))
            context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))


#implementing vin handler
vin_handler = CommandHandler('vin', vin)

#receiving lot number and returning lot
def lot(update: Update, context: CallbackContext):
    for vin in context.args:
        vin = get_vin(vin)
        try:
            df = pd.read_sql_query(f"SELECT vin_no, lot_no FROM vin_list WHERE vin_no LIKE '{vin}' LIMIT 1;", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
            if not df.empty:
                vin_no, lot = df.iloc[0].values
                context.bot.send_message(chat_id=update.effective_chat.id, text=vin_no+ ": "+lot)
                print(f"Requested lot of {vin_no}:{lot}")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"VIN is not available 😒")
        except:
            print("VIN of queried lot does not exist")
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Something went wrong while accessing lot😒")
            context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))


#implementing lot handler
lot_handler = CommandHandler('lot', lot)

#receiving lot number and returning storage area location
def loc(update: Update, context: CallbackContext):
    try:
        line_data = pd.read_sql_query("SELECT * FROM line_status", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
    except:
        print("Error: No data on line status")
        line_data = pd.DataFrame({"lot_no":[]})
    try:
        cbu_yard_data = pd.read_sql_query("SELECT * FROM cbu_yard_status", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
        cbu_yard = cbu_yard_data["lot_no"].values
        cbu_yard = cbu_yard.tolist()
        cbu_yard.reverse()
    except:
        cbu_yard = []
        print("Error: No data on cbu yard status")
    try:
        repair_area_status = pd.read_sql_query("SELECT * FROM repair_area_status", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
    except:
        repair_area_status = pd.DataFrame({'lot_no':[""]})
    try:
        skd_storage_data = pd.read_sql_query("SELECT * FROM skd_storage", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg', index_col='row')
    except:
        print("Error: No data on skd storage area status")
    for lot in context.args:
        lot = get_lot_code(lot)
        repair_area_status = repair_area_status[repair_area_status["lot_no"].str.startswith(lot)]
        line_data = line_data[line_data["lot_no"]==lot]
        try:
            # todo: check non-dispatch as well

            # search cbu yard
            if lot in cbu_yard:
                loc = "CBU Yard " + cbu_yard_names[cbu_yard.index(lot)]
                context.bot.send_message(chat_id=update.effective_chat.id, text=lot+": "+loc)
                print("Requested loc of {lot}:{loc}".format(loc=loc,lot=lot))
            # search repair area
            elif len(repair_area_status):
                context.bot.send_message(chat_id=update.effective_chat.id, text=lot+": Repair Area")
                print("Requested loc of {lot}:Repair Area".format(lot=lot))
            # search line
            elif len(line_data) != 0:
                line_index = line_data.index[0]
                loc = station_names[line_index]
                context.bot.send_message(chat_id=update.effective_chat.id, text=lot+": "+loc)
                print("Requested loc of {lot}:{loc}".format(loc=loc,lot=lot))
            # search storage area
            else:
                loc = get_storage_loc(skd_storage_data, lot)
                context.bot.send_message(chat_id=update.effective_chat.id, text=lot+": "+loc)
                print("Requested loc of {lot}:{loc}".format(loc=loc,lot=lot))
        except:
            print("Queried lot does not exist")
            context.bot.send_message(chat_id=update.effective_chat.id, text="Lot {lot} is not available 😒".format(lot=lot))
            context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))

#implementing loc handler
loc_handler = CommandHandler('loc', loc)


#receiving lot number and returning colour
def col(update: Update, context: CallbackContext):
    for lot in context.args:
        lot = lot.upper()
        try:
            df = pd.read_sql_query(f"SELECT colour FROM vin_list WHERE lot_no LIKE '{lot[0:2]}____' LIMIT 1;", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
            col = (df.iloc[0,0])
            context.bot.send_message(chat_id=update.effective_chat.id, text=lot.upper()+": "+col)
            print("Requested colour of {lot}:{col}".format(col=col,lot=lot))
        except:
            print("Queried lot does not exist")
            context.bot.send_message(chat_id=update.effective_chat.id, text="Lot {lot} is not available 😒".format(lot=lot))
            context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))

#implementing col handler
col_handler = CommandHandler('col', col)

#receiving lot number and returning katashiki
def katashiki(update: Update, context: CallbackContext):
    for lot in context.args:
        lot = lot.upper()
        try:
            df = pd.read_sql_query(f"SELECT katashiki FROM vin_list WHERE lot_no LIKE '{lot[0:2]}____' LIMIT 1;", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
            kat = (df.iloc[0,0])
            context.bot.send_message(chat_id=update.effective_chat.id, text=lot.upper()+": "+kat)
            print("Requested Katashiki of {lot}:{kat}".format(kat=kat,lot=lot))
        except:
            print("Queried lot does not exist")
            context.bot.send_message(chat_id=update.effective_chat.id, text="Lot {lot} is not available 😒".format(lot=lot))
            context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))

#implementing katashiki handler
katashiki_handler = CommandHandler('kat', katashiki)

#receiving lot number and returning engine_no
def eng(update: Update, context: CallbackContext):
    for lot in context.args:
        lot = get_lot_code(lot)
        try:
            df = pd.read_sql_query("SELECT engine_no FROM vin_list WHERE lot_no = \'%s\';"%lot, 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
            eng = str(df.iloc[0][0])
            context.bot.send_message(chat_id=update.effective_chat.id, text=lot+": "+eng)
            print("Requested engine_no of {lot}:{eng}".format(eng=eng,lot=lot))
        except:
            print("Engine no. of queried lot is not available")
            context.bot.send_message(chat_id=update.effective_chat.id, text="Lot {lot} is not available 😒".format(lot=lot))
            context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))

#implementing eng handler
eng_handler = CommandHandler('eng', eng)

#receiving lot number and returning VIN+ENGINE NUMBER [A SAGE Application requirement]
def serial(update: Update, context: CallbackContext):
    for lot in context.args:
        lot = get_lot_code(lot)
        try:
            df = pd.read_sql_query("SELECT vin_no,engine_no FROM vin_list WHERE lot_no = \'%s\';"%lot, 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
            serial = df.iloc[0]['vin_no']+str(df.iloc[0]['engine_no'])
            clip_board = pd.DataFrame([serial])
            clip_board.to_clipboard(index=False)
            context.bot.send_message(chat_id=update.effective_chat.id, text=lot+": "+serial)
            print("Requested serial of {lot}:{serial}".format(serial=serial,lot=lot))
        except:
            print("serial of queried lot is not available")
            context.bot.send_message(chat_id=update.effective_chat.id, text="Lot {lot} is not available 😒".format(lot=lot))
            context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))

#implementing serial handler
serial_handler = CommandHandler('ser', serial)

#receiving lot number and returning container_no
def con(update: Update, context: CallbackContext):
    for lot in context.args:
        lot = get_lot_code(lot)
        try:
            df = pd.read_sql_query("SELECT container_no FROM vin_list WHERE lot_no = \'%s\';"%lot, 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
            con = (df.iloc[0,0])
            context.bot.send_message(chat_id=update.effective_chat.id, text=lot+": "+con)
            print("Requested container_no of {lot}:{con}".format(con=con,lot=lot))
        except:
            print("Queried lot does not exist")
            context.bot.send_message(chat_id=update.effective_chat.id, text="Lot {lot} is not available 😒".format(lot=lot))
            context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))

#implementing con handler
con_handler = CommandHandler('con', con)

#receiving lot numbers and returning ok_units list
def ok_units_list(update: Update, context: CallbackContext):
    date = datetime.datetime.now()
    print('ok units list processing')
    ok_list = pd.DataFrame()
    try:
        cbu_yard_status = pd.read_sql_query("SELECT * FROM cbu_yard_status", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
        # remove in repair lots
        cbu_yard_status = cbu_yard_status[np.invert(cbu_yard_status['lot_no'].str.endswith("[In-Repair]"))]
        cbu_yard_status_available = True
    except:
        print('Error while trying to access cbu_yard_status')
        cbu_yard_status_available = False
    for lot in context.args:
        lot = get_lot_code(lot)
        try:
            df = pd.read_sql_query("SELECT lot_no, katashiki, vin_no, engine_no, colour  FROM vin_list WHERE lot_no = '{lot}';".format(lot=lot), 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg').iloc[0]
            ok_list = ok_list.append(df)
            # if cbu_yard_status_available:
            #     # remove lot cbu yard
            #     cbu_yard_status[np.invert(cbu_yard_status['lot_no'].str.startswith(lot)) ]
            # print("Requested ok_units list including {lot}".format(lot=lot))
        except:
            print("Queried lot does not exist")
            context.bot.send_message(chat_id=update.effective_chat.id, text="Lot {lot} is not available 😒".format(lot=lot))
            context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))
    row_count = len(ok_list.index)
    ok_list = ok_list.assign(Final_Inspection=[date.strftime("%d-%b-%y")]*row_count, Release_Date=[(datetime.date.today()+datetime.timedelta(days=1)).strftime("%d-%b-%y")]*row_count)
    ok_list.columns = ok_list.columns.str.replace("_", " ", regex=False)
    ok_list.columns = ok_list.columns.str.title()
    ok_list.index =  list(range(1,len(ok_list.index)+1))

    # file name
    # WITHOUT MACRO
    # f = date.strftime("%y%m%d %b '%y")+" OK Units List.xlsx"
    # 
    f = date.strftime("%y%m%d %b '%y")+" OK Units List.xlsm"

    # export to excel file
    # WITHOUT MACRO
    # ok_list.to_excel(f, index_label="S/No")
    # 
    writer = pd.ExcelWriter("temp.xlsx", engine='xlsxwriter')
    ok_list.to_excel(writer, sheet_name='Sheet1', index_label="S/No")
    workbook  = writer.book
    workbook.filename = f
    workbook.add_vba_project(r'C:\Users\LogisticsUser02\Documents\VIN_import\backend\vbaProject.bin')
    writer.save()
    # if cbu_yard_status_available:
    #     cbu_yard_status.to_sql("cbu_yard_status", engine, index=False, if_exists='replace')
    with open(f, 'rb') as f:
        context.bot.send_document(update.effective_chat.id, f, caption="Here is your draft📃")
        context.bot.send_message(chat_id="848287261", text="{user} successfully accessed function:\n {command} ".format(user=str(update["message"]["chat"]["first_name"]), command=str(update["message"]["text"])))
    os.remove(f)

#implementing ok_units_list handler
ok_units_list_handler = CommandHandler('oul', ok_units_list)

#pushing lots into the line
def supply_line(update: Update, context: CallbackContext):
    try:
        storage_area = pd.read_sql_query("SELECT * FROM skd_storage", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg', index_col='row')
        print("database accessed for storage area status")
    except:
        storage_area = pd.DataFrame()
        print("No storage area information in database")
    try:
        cbu_yard = pd.read_sql_query("SELECT * FROM cbu_yard_status", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
        x = cbu_yard["lot_no"].values
        x = x.tolist()
        print("cbu yard ", x)
    except:
        print("Warning: No data information on cbu yard status")
        x = []
    try:
        line_data = pd.read_sql_query("SELECT * FROM line_status", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
        y = line_data["lot_no"].values
        y = y.tolist()
    except:
        print("Warning: No data information on line status")
        y = []
    for i, lot in enumerate(context.args):
        lot = get_lot_code(lot)
        # try:
        y.reverse()
        if len(y) < 8:
            y.append(lot)
        else:
            y.append(lot.upper())
            x.append(y.pop(0))
        y.reverse()
        if i == len(context.args)-1:
            # update next lot location's info
            print(lot)
            loc = get_storage_loc(storage_area,lot)
            curr_col = loc[0]
            col = storage_area.columns.to_list()
            col.remove(col[-1])
            row = storage_area.index.to_list()
            print("next row", (row.index(int(loc[1]))-1)%len(row))
            next_ind = row[(row.index(int(loc[1]))-1)%len(row)]
            new_col = col[(col.index(curr_col)+1)%len(col)] if curr_col == 5  else curr_col
            next_lot_loc = new_col+str(next_ind)
            next_lot_loc = pd.DataFrame({"next":[next_lot_loc]})
            next_lot_loc.to_sql('next_lot_loc', engine, index=False, if_exists='replace')
        # remove pushed lot from storage area
        storage_area = storage_area[np.invert(storage_area==lot)].fillna(np.nan)
        print("Pushed {lot}".format(lot=lot))
        # except:
        #     print("error while trying to push {}".format(lot))
        #     context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))
        #     context.bot.send_message(chat_id=update.effective_chat.id, text="Pushing {lot} was unsuccessful 😒".format(lot=lot))
    cbu_yard_status = pd.DataFrame({"lot_no":x})
    if not cbu_yard_status.empty:
        cbu_yard_status = cbu_yard_status[np.invert(cbu_yard_status['lot_no'].str.endswith('[In-Repair]'))]
    line_status = pd.DataFrame({"lot_no":y})
    storage_area.to_sql("skd_storage", engine, if_exists='replace')
    cbu_yard_status.to_sql("cbu_yard_status", engine, index=False, if_exists='replace')
    line_status.to_sql("line_status", engine, index=False, if_exists='replace')
    context.bot.send_message(chat_id=update.effective_chat.id, text="Push was successful 👍")
    # with engine.connect() as con:
        # con.execute('ALTER TABLE "cbu_yard_status" ADD PRIMARY KEY ("lot_no");')
        # con.execute('ALTER TABLE "line_status" ADD PRIMARY KEY ("lot_no");')

#implementing handler
supply_line_handler = CommandHandler('push', supply_line)

#quering for line updates
def line(update: Update, context: CallbackContext):
    try:
        line_data = pd.read_sql_query("SELECT * FROM line_status", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
        y = line_data["lot_no"].values
        y = y.tolist()
        print(y)
        msg = ""
        for i,lot in enumerate(y):
            msg += "\n {station_name}: {lot}".format(station_name=station_names[i],lot=lot) if i < 8 else ""
        msg = "➖Line Status➖\n {}".format(msg)
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
        print(msg)
    except:
        print('Line status unavailable in database')
        context.bot.send_message(chat_id=update.effective_chat.id, text="Line Data is currently unavailable")

#implementing handler
line_handler = CommandHandler('line', line)

#quering for cbu updates
def cbu(update: Update, context: CallbackContext):
    try:
        cbu_yard_status = pd.read_sql_query("SELECT * FROM cbu_yard_status", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
        cbu_yard_status = cbu_yard_status[np.invert(cbu_yard_status['lot_no'].str.endswith('[In-Repair]'))]
        y = cbu_yard_status["lot_no"].values
        y = y.tolist()
        print(y)
    except:
        y=[]
    msg = ""
    for i,lot in enumerate(y):
        msg += "\n {station_name}: {lot}".format(station_name=cbu_yard_names[i],lot=lot) if i < 8 else ""
    msg = "➖CBU Yard Status➖\n {}".format(msg if len(msg) else "\nNo Units Available") 
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
    print(msg)

#implementing handler
cbu_handler = CommandHandler('cbu', cbu)

#quering for storage lane SKDs
def lane(update: Update, context: CallbackContext):
    try:
        storage_area = pd.read_sql_query("SELECT * FROM skd_storage", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg', index_col='row')
        storage_area.index.name = ""
    except:
        print("Error: storage area data not available")
        context.bot.send_message(chat_id=update.effective_chat.id, text="Lane {} data is unavailable 😒".format(lane.upper()) + info)
        context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))

    for lane in context.args:
        info = storage_area[lane.upper()].to_string()
        context.bot.send_message(chat_id=update.effective_chat.id, text="➖Storage Area Lane {}➖\n".format(lane.upper()) + info)
        print("Queried for Lots in lane {}\n".format(lane) + info)

#implementing handler
lane_handler = CommandHandler('lane', lane)

#move unit to repairs
def repair(update: Update, context: CallbackContext):
    lot = ""
    try:
        line_data = pd.read_sql_query("SELECT * FROM line_status", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
        temp = line_data['lot_no'].to_list()
        repair_area_status = pd.read_sql_query("SELECT * FROM repair_area_status", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
        repair_area_status_available = True
        if not len(repair_area_status.values):
            repair_area_status_available = False
            repair_area_status = pd.DataFrame({"lot_no":[]}) 
            print("repair area is empty")
    except:
        print("no data available for repair area")
        repair_area_status = pd.DataFrame({"lot_no":[]}) 
        repair_area_status_available = False
    try:
        # query units at non-dispatch area
        non_dispatch_status = pd.read_sql_query("SELECT * FROM non_dispatch_status", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
        non_dispatch_status_available = True
        if not len(non_dispatch_status.values):
            non_dispatch_status_available = False
            non_dispatch_status = pd.DataFrame({"lot_no":[]}) 
            print("Non-Dispatch area is empty")
    except:
        print("no data available from Non-Dispatch area")
        non_dispatch_status = pd.DataFrame({"lot_no":[]}) 
        non_dispatch_status_available = False
    try:
        lots = context.args
        if len(lots) != 0:
            non_dispatch_unit = pd.DataFrame({'lot_no':[]})
            for lot in lots:
                lot = get_lot_code(lot)
                if non_dispatch_status_available:
                    non_dispatch_unit = non_dispatch_status[non_dispatch_status['lot_no'].str.startswith(lot)]
                    if len(non_dispatch_unit):
                        non_dispatch_status = non_dispatch_status[np.invert(non_dispatch_status['lot_no'].str.startswith(lot))]
                        repair_area_status = repair_area_status.append( non_dispatch_unit,ignore_index=True).drop_duplicates()
                        non_dispatch_status.to_sql("non_dispatch_status", engine, index=False, if_exists='replace')

                if non_dispatch_unit.empty:
                    affix = '.a' if temp.index(lot)<4 else '.i'
                    temp = ["{} [In-Repair]".format(x) if x==lot else x for i, x in enumerate(temp) ]
                    temp = pd.DataFrame({"lot_no":temp})

                    # ADD prefix condition

                    temp.to_sql("line_status", engine, index=False, if_exists='replace')
                    repair_area_status = repair_area_status.append( {"lot_no":lot+affix},ignore_index=True).drop_duplicates()
                repair_area_status.to_sql("repair_area_status", engine, index=False, if_exists='replace')
                with engine.connect() as con:
                    con.execute('ALTER TABLE "repair_area_status" ADD PRIMARY KEY ("lot_no");')
                msg = f"{lot} has been moved for repairs"
                context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
                context.bot.send_message(chat_id="848287261", text="{user} moved {lot} for repairs".format(user=str(update["message"]["chat"]["first_name"]), lot=lot))


        else:
            repair_area_status = repair_area_status['lot_no'].values.tolist()
            msg = ''
            for l in repair_area_status:
                msg = msg + "\n" + l.split(".")[0]
            context.bot.send_message(chat_id=update.effective_chat.id, text="➖Repair Area Status➖\n{}".format(msg if repair_area_status_available else "No Units"))
    except:
            print("Error:Could not move unit for repairs")
            context.bot.send_message(chat_id=update.effective_chat.id, text="There was a problem moving unit: {} to repairs 😒".format(lot))
            context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))

#implementing handler
repair_handler = CommandHandler('rep', repair)

# restore unit to line from repair
def restore(update: Update, context: CallbackContext):
    # to-do: modify code so that returning unit does not go ahead of its position if it had not been to repair
    lot = ""
    repair_area_status_available = True
    try:    
        line_data = pd.read_sql_query("SELECT * FROM line_status", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
        temp = line_data['lot_no'].to_list()
        repair_area_status = pd.read_sql_query("SELECT * FROM repair_area_status", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
        if not len(repair_area_status.values):
            repair_area_status_available = False
            repair_area_status = pd.DataFrame({"lot_no":[]}) 
            print("repair area is empty")
    except:
        print("no data available at repair area")
        repair_area_status = pd.DataFrame({"lot_no":[]}) 
        repair_area_status_available = False
    try:
        cbu_yard = pd.read_sql_query("SELECT * FROM cbu_yard_status", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
    except:
        print("Caution: No data information on cbu yard status")
        cbu_yard = pd.DataFrame({"lot_no":[]})
    try:
        lots = context.args
        if len(lots) != 0 and repair_area_status_available:
            for temp in lots:
                temp = get_lot_code(temp)
                lot,affix = repair_area_status[repair_area_status['lot_no'].str.contains(temp)]['lot_no'].values[0].upper().split('.')
                columns = line_data.columns
                # remove lot  In-Repair label and insert restored lot
                line_data = line_data[np.invert(line_data['lot_no'].str.startswith(lot))]
                restore_loc = station_names[7]
                if affix=='A':
                    restore_loc = station_names[4]
                    line_data = pd.DataFrame(np.insert(line_data.values,station_names.index('INSP1'), [lot],0))  
                else:
                    line_data = pd.DataFrame(np.insert(line_data.values,station_names.index('INSP4'), [lot],0))
                line_data.columns = columns
                if len(line_data) > 8:
                    cbu_yard.append(line_data.iloc[8], ignore_index=True)
                    line_data = line_data = line_data.iloc[range(0,8)]                                         
                line_data.to_sql('line_status', engine, if_exists='replace', index=False)
                # delete lot from repair area 
                repair_area_status = repair_area_status[np.invert(repair_area_status['lot_no'].str.startswith(lot))]
                repair_area_status.to_sql("repair_area_status", engine, index=False, if_exists='replace')
                msg = f"{lot} has been restored to {restore_loc}"
                context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
                context.bot.send_message(chat_id="848287261", text="{user} restored {lot} to {restore_loc} ".format(user=str(update["message"]["chat"]["first_name"]), lot=lot, restore_loc=restore_loc))
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You have to specify lot number of unit restored")
    except:
        print("Error:Could not move unit from repairs")
        context.bot.send_message(chat_id=update.effective_chat.id, text="There was a problem moving unit: {} from repairs 😒".format(lot))
        context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))

#implementing handler
restore_handler = CommandHandler('res', restore)

#move unit to non-dispatch units area
def non_dispatch(update: Update, context: CallbackContext):
    lot = ""
    try:
        # query units at repair
        repair_area_status = pd.read_sql_query("SELECT * FROM repair_area_status", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
        non_dispatch_status = pd.read_sql_query("SELECT * FROM non_dispatch_status", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
        non_dispatch_status_available = True
        if not len(non_dispatch_status.values):
            non_dispatch_status_available = False
            non_dispatch_status = pd.DataFrame({"lot_no":[]}) 
            print("Non-Dispatch area is empty")
    except:
        print("no data available from Non-Dispatch area")
        non_dispatch_status = pd.DataFrame({"lot_no":[]}) 
        non_dispatch_status_available = False
    try:
        lots = context.args
        if len(lots) != 0:
            for lot in lots:
                lot = get_lot_code(lot)
                unit = repair_area_status[repair_area_status['lot_no'].str.startswith(lot)]
                # move unit from repair area 
                repair_area_status = repair_area_status[np.invert(repair_area_status['lot_no'].str.startswith(lot))]
                
                # update non-dispatch units area
                non_dispatch_status = non_dispatch_status.append(unit, ignore_index=True).drop_duplicates()
                non_dispatch_status.to_sql("non_dispatch_status", engine, index=False, if_exists='replace')
                repair_area_status.to_sql("repair_area_status", engine, index=False, if_exists='replace')
                with engine.connect() as con:
                    con.execute('ALTER TABLE "non_dispatch_status" ADD PRIMARY KEY ("lot_no");')
                msg = f"{lot} has been moved to Non-Dispatch Location"
                context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
        else:
            non_dispatch_status = non_dispatch_status['lot_no'].values.tolist()
            msg = ''
            for l in non_dispatch_status:
                msg = msg + "\n" + l.split(".")[0]
            context.bot.send_message(chat_id=update.effective_chat.id, text="➖Non-Dispatchables➖\n{}".format(msg if non_dispatch_status_available else "No Units"))
    except:
            print("Error:Could not move unit to Non-Dispatch")
            context.bot.send_message(chat_id=update.effective_chat.id, text="There was a problem moving unit: {} to Non-Dispatch Area 😒".format(lot))
            context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))

#implementing handler
non_dispatch_handler = CommandHandler('ndu', non_dispatch)


# Dispatch units from CBU yard
def dispatch(update: Update, context: CallbackContext):
    try:
        cbu_yard_status = pd.read_sql_query("SELECT * from cbu_yard_status", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
    except:
        cbu_yard_status = pd.DataFrame({'lot':[]})
    try:
        vins = context.args
        if not cbu_yard_status.empty:
            for vin in vins:
                vin = get_vin(vin)
                df = pd.read_sql_query(f"SELECT vin_no, lot_no FROM vin_list WHERE vin_no LIKE '{vin}' LIMIT 1;", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
                if not df.empty:
                    vin_no, lot = df.iloc[0].values
                    available_lot = cbu_yard_status[cbu_yard_status['lot_no'].str.startswith(lot)]
                    if available_lot.empty:
                        context.bot.send_message(chat_id=update.effective_chat.id, text=f'{lot}: {vin_no} ❌ unavailable in yard')
                    else:
                        cbu_yard_status = cbu_yard_status[np.invert(cbu_yard_status['lot_no'].str.startswith(lot))]
                        cbu_yard_status.to_sql('cbu_yard_status', engine, index=False, if_exists='replace')
                        context.bot.send_message(chat_id=update.effective_chat.id, text=f"{lot}: {vin_no} ✔️")
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="VIN does not exist 😒")
                    context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))

        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="There are no Units at CBU Yard")
    except:
        print("Error:Could not run dispatch function")
        context.bot.send_message(chat_id="848287261", text="{user} [@{username}] could not access function: {command} ".format(user=str(update["message"]["chat"]["first_name"]), username=str(update["message"]["chat"]["username"]), command=str(update["message"]["text"])))

# implementing handler
dispatch_handler = CommandHandler('dis', dispatch)

# update line information
def update_line(update:Update, context:CallbackContext):
    station = context.args[0].upper()
    new_lot = get_lot_code(context.args[1])
    print('attempting to update line')
    try:
        line = pd.read_sql_query("SELECT * FROM line_status;", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
        print('successfully accessed line status')
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Line information is currently unavailable")
        return
    try:
        storage_area = pd.read_sql_query("SELECT * FROM skd_storage;", 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
        print('successfully accessed storage area status')
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Attempt to access storage area info was unsuccessful")
        return
    line.iloc[station_names.index(station)]= new_lot
    line.to_sql('line_status', engine, index=False, if_exists='replace')
    # ****refactor code set for deleting lot if it is below*******
    storage_area[np.invert(storage_area==new_lot)].fillna(np.nan)
    storage_area.to_sql('skd_storage', engine, if_exists='replace')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Line station:{station} now has:{new_lot}'.format(station=station, new_lot=new_lot))
    print('Line update: successful')


# implementing handler
update_line_handler = CommandHandler('upl', update_line)

# return next lot to line's location
def next_loc(update:Update, context:CallbackContext):
    # try:
    next_loc = pd.read_sql_query('Select * from next_lot_loc ', 'postgresql://postgres:Jpn@pg13@localhost:5432/ttmg')
    next_loc = next_loc.values[0][0]
    context.bot.send_message(chat_id=update.effective_chat.id, text='Next lot Location at {next_loc}'.format(next_loc=next_loc))
    # except:
    #     send_error_telegram(update, context,"Somethnig went wrong🤔")
    #     print('Error: could not retrieve next lot\'s location')

# implementing handler
next_loc_handler = CommandHandler('nxt', next_loc)

#implementing default (unknown)
def joke(update: Update, context: CallbackContext):
    if  "AGENDA" in update.message.text.upper():
        context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=int(update["message"]["message_id"]), text="Abi you nor...April 25th😜")
    if  "CARE" in update.message.text.upper():
        context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=int(update["message"]["message_id"]), text="Sure...safety first👊")
    if  "LOL" in update.message.text.upper():
        context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=int(update["message"]["message_id"]), text="😂")
    # if  "LOL" in update.message.text.upper():
    #     context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=int(update["message"]["message_id"]), text="😂")

#implementing unknown handler
joke_handler = MessageHandler(Filters.text, joke)

#implementing default (unknown)
def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I'm not sure what you need 🤔...")

#implementing unknown handler
unknown_handler = MessageHandler(Filters.command, unknown)

def error(update:Update, context:CallbackContext):
    logger.warning('Update: {update} caused error: {error}'.format(update=update,error=context.error))

def main():
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(vin_handler)
    dispatcher.add_handler(lot_handler)
    dispatcher.add_handler(loc_handler)
    dispatcher.add_handler(col_handler)
    dispatcher.add_handler(katashiki_handler)
    dispatcher.add_handler(eng_handler)
    dispatcher.add_handler(serial_handler)
    dispatcher.add_handler(con_handler)
    dispatcher.add_handler(ok_units_list_handler)
    dispatcher.add_handler(import_doc_handler)
    dispatcher.add_handler(supply_line_handler)
    dispatcher.add_handler(line_handler)
    dispatcher.add_handler(cbu_handler)
    dispatcher.add_handler(lane_handler)
    dispatcher.add_handler(repair_handler)
    dispatcher.add_handler(restore_handler)
    dispatcher.add_handler(non_dispatch_handler)
    dispatcher.add_handler(dispatch_handler)
    dispatcher.add_handler(update_line_handler)
    dispatcher.add_handler(next_loc_handler)
    dispatcher.add_handler(joke_handler)
    dispatcher.add_handler(unknown_handler)
    dispatcher.add_error_handler(error)

    # updater.start_polling()
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook("https://factree.herokuapp.com/"+ TOKEN)
    updater.idle()

if __name__=='__main__':
    main()