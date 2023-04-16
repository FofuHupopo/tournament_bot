from aiogram import types
from sqlalchemy.orm import Session
from models import engine, UserModel, UnregisteredMessageModel

from bot import dp, bot, MESSAGES
from keyboards import start_keyboard, join_keyboard, main_keyboard


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(MESSAGES["start"], reply_markup=start_keyboard)


@dp.callback_query_handler(lambda cmd: cmd.data == "confirm_rules")
async def confirm_rules_btn(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    with Session(engine) as session:
        exists = session.query(
            session.query(UserModel).filter_by(telegram_id=callback_query.message.chat.id).exists()
        ).scalar()
        
        if exists:
            await callback_query.message.edit_text(MESSAGES["already_registered"])
        else:
            await callback_query.message.edit_text(MESSAGES["main_menu"], reply_markup=main_keyboard)
