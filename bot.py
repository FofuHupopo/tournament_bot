# -*- coding: utf-8 -*-
import logging
import json
import os
from time import sleep
from datetime import datetime

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage


MESSAGES = json.load(open("messages.json", encoding="utf8"))
# API_TOKEN = os.getenv("BOT_TOKEN")
API_TOKEN = "2018923142:AAFRTQXsNLs2GTCR7rVEnSpzo4el1fl7m7E"

logging.basicConfig(level=logging.INFO, filename=f"./logs/log-{datetime.utcnow():%Y-%m-%d_%H:%M:%S}.txt")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


from handlers import *


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(send_meme_handler())

    try:
        executor.start_polling(dp, skip_updates=True, loop=loop)
    except exceptions.BotBlocked:
        print("Bot blocked by user")
    except exceptions.ChatNotFound:
        print("Chat not found")
    except exceptions.RetryAfter as e:
        print(f"Retrying after {e.timeout} seconds.")
        sleep(e.timeout)
    except exceptions.TelegramAPIError:
        print("Error occurred while accessing the Telegram API")
    finally:
        loop.stop()
