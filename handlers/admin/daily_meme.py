import random
import asyncio
import os
from aiogram import types
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from aiogram.dispatcher.filters import ContentTypeFilter

from .filter import AdminFilter
from .admin import *

from bot import dp, bot
from states import LoadMemeState
from models import engine, UserModel
from keyboards import go_back_keyboard


IMAGE_DIR = './memes/'


def load_memes():
    images = []

    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            path = IMAGE_DIR + filename
            images.append(path)
    
    return images


async def send_meme():
    meme_path = random.choice(load_memes())
    
    if not meme_path:
        return
    
    with Session(engine) as session:
        users = session.query(UserModel.telegram_id).all()
    
    users = list(map(lambda x: int(x[0]), users))

    with open(meme_path, 'rb') as photo:
        for user in users:
            await bot.send_photo(chat_id=user, photo=photo, caption="🤯🤯🤯 Зарядись настроением! Ежедневный мем!\n🥲")
    
    os.remove(meme_path)


async def send_meme_handler():
    while True:
        now = datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        midday = midnight + timedelta(hours=12, minutes=0)
        
        sleep_time = int((midday - now).total_seconds())
        
        if sleep_time <= 0:
            sleep_time = 24 * 60 * 60 - sleep_time

        await asyncio.sleep(sleep_time)

        await send_meme()


@dp.callback_query_handler(AdminFilter(), lambda cb: cb.data == "admin_load_meme")
async def load_meme_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    await bot.send_message(callback_query.from_user.id, "Отправте картинку для нового ежедневного мема.", reply_markup=go_back_keyboard)
    await LoadMemeState.meme.set()
    

@dp.message_handler(AdminFilter(), content_types=types.ContentType.PHOTO, state=LoadMemeState.meme)
async def load_meme_handler(message: types.Message, state: FSMContext):
    meme = message.photo[-1]
    
    file_path = f"./memes/{message.message_id}.jpg"
    
    await state.finish()
    
    await meme.download(destination_file=file_path)
    await admin_handler(message)
