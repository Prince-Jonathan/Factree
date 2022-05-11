'''
A single entry-point that resolves theimport dependencies.
In order to run app, point to run.
>>python run.py
'''
import os
from telegram_bot.app import APP, DB, engine
# from routes import *
import pandas as pd
import numpy as np
import telegram_bot.vin_bot
from telegram_bot.vin_bot import updater


# if __name__ == "__main__":
    # try:
    #     df.to_sql("data", engine, if_exists='append')
    # except:
    #     print("Attempted duplicate lot no. insertion")
    #     with engine.connect() as con:
    #         con.execute('ALTER TABLE "data" ADD PRIMARY KEY ("lot_no");')
    #run telegram
    # updater.start_polling()
updater.start_webhook()
updater.idle()