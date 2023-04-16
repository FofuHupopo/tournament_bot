import copy
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, ReplyKeyboardRemove
from sqlalchemy.orm import Session

from .admin import *
from .filter import AdminFilter

from models import engine, CompetitionModel, RegistrationModel
from bot import dp, bot, MESSAGES
from states import *
from keyboards import go_back_keyboard, competition_keyboard


@dp.callback_query_handler(AdminFilter(), lambda cmd: cmd.data == "admin_competitions")
async def competitions_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    with Session(engine) as session:
        competitions = session.query(CompetitionModel).all()
        
        temp_competition_keyboard = copy.deepcopy(competition_keyboard)
    
        for ind, competition in enumerate(competitions, 1):
            competition_btn = InlineKeyboardButton(f"{ind}. {competition.name}", callback_data=f"admin_competition__{competition.id}")
            temp_competition_keyboard.add(competition_btn)

    await callback_query.message.edit_text(MESSAGES["competition_menu"], reply_markup=temp_competition_keyboard)


@dp.callback_query_handler(AdminFilter(), lambda cmd: "admin_competition__" in cmd.data)
async def competition_detail_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    competition_id = callback_query.data.split("__")[-1]
    
    with Session(engine) as session:
        competition = session.query(CompetitionModel).filter(CompetitionModel.id == competition_id).first()
        registrations = session.query(RegistrationModel).filter(RegistrationModel.competition_id == competition_id).count()
        
        text = f"Событие: {competition.name}\n{competition.description}\nДата: {competition.date}\nМаксимальное кол-во игроков: {competition.max_participants}\nЗаявок: {registrations}"
    
    await callback_query.message.edit_text(text)
