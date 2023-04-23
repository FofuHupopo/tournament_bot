from datetime import datetime
from aiogram import types
from sqlalchemy.orm import Session

from bot import dp, bot
from models import engine, UserModel, RegistrationModel, CompetitionModel
from keyboards import profile_keyboard


async def profile_text_generator(telegram_id):
    with Session(engine) as session:
        user = session.query(UserModel).filter(UserModel.telegram_id == telegram_id).first()
    
        registration = session.query(RegistrationModel).join(
            CompetitionModel, CompetitionModel.id == RegistrationModel.competition_id
        ).filter(
            RegistrationModel.user_id == user.id,
            RegistrationModel.is_accepted == False,
            CompetitionModel.date >= datetime.now()
        ).count()
        participation = session.query(RegistrationModel).join(
            CompetitionModel, CompetitionModel.id == RegistrationModel.competition_id
        ).filter(
            RegistrationModel.user_id == user.id,
            RegistrationModel.is_accepted == True,
            CompetitionModel.date >= datetime.now()
        ).count()

    return f"{user.name} {user.surname}\n\n🏫Класс: {user.class_number} {user.class_letter}\n\n📧Почта: {user.mail}\n\n📋Вы зарегистрировались в {registration} событиях\n\n🎮Вы участвуете в {participation} событиях"


@dp.message_handler(commands=["profile"])
async def profile_handler(message: types.Message):
    text = await profile_text_generator(message.from_user.id)
    
    await message.reply(text, reply_markup=profile_keyboard)


@dp.callback_query_handler(lambda cb: cb.data == "profile")
async def profile_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    text = await profile_text_generator(callback_query.from_user.id)
    
    await callback_query.message.edit_text(text, reply_markup=profile_keyboard)
