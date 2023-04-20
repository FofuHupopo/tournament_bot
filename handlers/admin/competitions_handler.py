import copy
from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, ReplyKeyboardRemove
from sqlalchemy.orm import Session

from .admin import *
from .filter import AdminFilter

from models import engine, CompetitionModel, RegistrationModel
from bot import dp, bot, MESSAGES
from states import (
    CompetitionDetailState, AddCompetitionState
)
from keyboards import go_back_keyboard, admin_competition_keyboard, admin_competition_detail_keyboard


@dp.callback_query_handler(AdminFilter(), lambda cmd: cmd.data == "admin_competitions")
async def competitions_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    with Session(engine) as session:
        competitions = session.query(CompetitionModel).all()
        
        temp_competition_keyboard = copy.deepcopy(admin_competition_keyboard)
    
        for ind, competition in enumerate(competitions, 1):
            competition_btn = InlineKeyboardButton(f"{ind}. {competition.name}", callback_data=f"admin_competition__{competition.id}")
            temp_competition_keyboard.add(competition_btn)

    await callback_query.message.edit_text(MESSAGES["competition_menu"], reply_markup=temp_competition_keyboard)


# Add Competition

@dp.callback_query_handler(AdminFilter(), lambda cmd: cmd.data == "admin_add_competition")
async def start_add_comptetion(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    await AddCompetitionState.name.set()
    await bot.send_message(callback_query.from_user.id, text="Введите название нового события.", reply_markup=go_back_keyboard)


@dp.message_handler(AdminFilter(), state=AddCompetitionState.name)
async def get_competition_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await AddCompetitionState.description.set()
    await message.answer(f"Введите описание для нового события.", reply_markup=go_back_keyboard)


@dp.message_handler(AdminFilter(), state=AddCompetitionState.description)
async def get_competition_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text

    await AddCompetitionState.game.set()
    await message.answer(f"Введите название игры для нового события.", reply_markup=go_back_keyboard)


@dp.message_handler(AdminFilter(), state=AddCompetitionState.game)
async def get_competition_game(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['game'] = message.text

    await AddCompetitionState.server.set()
    await message.answer(f"Введите данные сервера (ip:port) для нового события.", reply_markup=go_back_keyboard)


@dp.message_handler(AdminFilter(), state=AddCompetitionState.server)
async def get_competition_server(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['server'] = message.text

    await AddCompetitionState.max_participants.set()
    await message.answer(f"Введите максимальное кол-во участников для нового события.", reply_markup=go_back_keyboard)


@dp.message_handler(AdminFilter(), state=AddCompetitionState.max_participants)
async def get_competition_max_participants(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['max_participants'] = message.text

    await AddCompetitionState.date.set()
    await message.answer(f"Введите дату проведения нового события в формате \"День.Месяц.Год Час:Минуты\", например, \"01.01.2000 10:00\".", reply_markup=go_back_keyboard)


@dp.message_handler(AdminFilter(), state=AddCompetitionState.date)
async def create_competition(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date'] = message.text

        name = data['name']
        description = data['description']
        game = data['game']
        server = data['server']
        max_participants = data['max_participants']
        date = datetime.strptime(data['date'], "%d.%m.%Y %H:%M")

        with Session(engine) as session:
            new_competition = CompetitionModel(
                name=name,
                description=description,
                game=game,
                server=server,
                max_participants=max_participants,
                date=date
            )
            
            session.add(new_competition)
            session.commit()

    await state.finish()
    await message.answer("Новое событие было создано.", reply_markup=ReplyKeyboardRemove())
    await admin_handler(message)


# Competition detail

@dp.callback_query_handler(AdminFilter(), lambda cmd: "admin_competition__" in cmd.data, state="*")
async def competition_detail_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    competition_id = callback_query.data.split("__")[-1]
    
    with Session(engine) as session:
        competition = session.query(CompetitionModel).filter(CompetitionModel.id == competition_id).first()
        registrations = session.query(RegistrationModel).filter(RegistrationModel.competition_id == competition_id).count()
        accepted_registrations = session.query(RegistrationModel).filter(RegistrationModel.competition_id == competition_id, RegistrationModel.is_accepted == True).count()
        
        text = f"Событие: {competition.name}\n{competition.description}\nДата: {competition.date}\nМаксимальное кол-во игроков: {competition.max_participants}\nЗаявок: {registrations}\nПринятых заявок: {accepted_registrations}"
        
    await CompetitionDetailState.competition_id.set()
    await state.update_data(competition_id=competition_id)
    
    await callback_query.message.edit_text(text, reply_markup=admin_competition_detail_keyboard)


@dp.callback_query_handler(AdminFilter(), lambda cmd: cmd.data == "admin_go_back_competitions", state=CompetitionDetailState.competition_id)
async def competition_detail_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    await state.finish()
    
    await competitions_handler(callback_query)


@dp.callback_query_handler(AdminFilter(), lambda cmd: cmd.data == "admin_competition_cancel", state=CompetitionDetailState.competition_id)
async def competition_detail_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    async with state.proxy() as data:
        competition_id = data["competition_id"]
        
    with Session(engine) as session:
        session.query(CompetitionModel).filter(CompetitionModel.id == competition_id).delete()
        session.commit()
    
    await state.finish()
    
    await competitions_handler(callback_query)


# Edit competition


@dp.callback_query_handler(AdminFilter(), lambda cmd: cmd.data == "admin_competition_edit_name", state=CompetitionDetailState.competition_id)
async def edit_competition_name_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    await CompetitionDetailState.name.set()
    
    await bot.send_message(callback_query.from_user.id, "Введите новое название для события")


@dp.message_handler(AdminFilter(), state=CompetitionDetailState.name)
async def edit_competition_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        competition_id = data["competition_id"]
    
    with Session(engine) as session:
        competition = session.query(CompetitionModel).filter(CompetitionModel.id == competition_id).first()
        competition.name = message.text
        
        session.add(competition)
        session.commit()
    
    await state.finish()
    
    # await bot.send_message(message.from_user.id, f"Установлено \"{message.text}\" название для этого события.")
    await bot.call_back_query_handler(competitions_handler)()
