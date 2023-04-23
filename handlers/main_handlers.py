from aiogram import types
from sqlalchemy.orm import Session
from models import engine, UserModel, UnregisteredMessageModel

from bot import dp, bot, MESSAGES
from keyboards import start_keyboard, join_keyboard, main_keyboard


@dp.message_handler(commands=['start'])
async def welcome_handler(message: types.Message):
    with Session(engine) as session:
        user = session.query(UserModel).filter(UserModel.telegram_id == message.from_user.id).first()
    
        if user:
            await main_handler(message)
        else:
            await message.reply(MESSAGES["start"], reply_markup=start_keyboard)


@dp.message_handler(commands=["menu"])
async def main_handler(message: types.Message):
    with Session(engine) as session:
        user = session.query(UserModel).filter(UserModel.telegram_id == message.from_user.id).first()
    
        if user:
            await message.reply(MESSAGES["main_menu"], reply_markup=main_keyboard)
        else:
            await welcome_handler(message)

            
@dp.callback_query_handler(lambda cb: cb.data == "menu")
async def menu_callback(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(MESSAGES["main_menu"], reply_markup=main_keyboard)


@dp.callback_query_handler(lambda cb: cb.data == "empty")
async def empty_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
