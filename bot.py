# -*- coding: utf-8 -*-
import logging
import json
from datetime import datetime

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage


MESSAGES = json.load(open("messages.json", encoding="utf8"))
API_TOKEN = "2018923142:AAGZWUnihB0GXC9F-qlzMd1jVEmQ9138PmM"

logging.basicConfig(level=logging.INFO) #, filename=f"./logs/log-{datetime.utcnow():%Y-%m-%d_%H:%M:%S}.txt")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


from handlers import *


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
