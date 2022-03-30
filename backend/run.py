'''
A single entry-point that resolves theimport dependencies.
In order to run app, point to run.
>>python run.py
'''
from telegram_bot.app import APP, DB, engine
# from routes import *
import pandas as pd
import numpy as np
import telegram_bot.vin_bot
from telegram_bot.vin_bot import updater

# from vin_bot import updater, dispatcher

# from waitress import serve
# # import logging

# logging.basicConfig()
# logging.getLogger().setLevel(logging.CRITICAL) # Basically silence all logs from the root logger


# df = pd.read_excel(r"C:\Users\LogisticsUser02\Documents\VIN_import\VIN LIST.xlsx" , index_col=0, skiprows=range(0,2), usecols="A:L")
# # change column names to lowercase and replace spaces with '_'
# df.columns = df.columns.str.replace(" ", "_",regex=False)
# df.columns = df.columns.str.lower()
# df.columns = df.columns.str.replace(".","",regex=False)
# df.index.name = df.index.name.lower().replace(" ","_")[:-1]

# working instance of database query of vins
# try:
#     with engine.connect() as conn, conn.begin():
#         test = pd.read_sql_query("SELECT * FROM data;", conn, index_col="lot_no")
#         print("\n\n\n")
#         print(type(pd.concat([test, test]).drop_duplicates()))
# except:
#     print("query failed")
# print(test.values[0][0])



if __name__ == "__main__":
    # try:
    #     df.to_sql("data", engine, if_exists='append')
    # except:
    #     print("Attempted duplicate lot no. insertion")
    #     with engine.connect() as con:
    #         con.execute('ALTER TABLE "data" ADD PRIMARY KEY ("lot_no");')
    
    #run telegram

    #serve(APP, host='0.0.0.0', port=19087)
    # APP.run(host="0.0.0.0", port=8050, debug=True)
    updater.start_polling()
    updater.idle()