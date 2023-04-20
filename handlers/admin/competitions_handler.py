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


async def competitions_view(message: types.Message, edit=False):
    with Session(engine) as session:
        competitions = session.query(CompetitionModel).all()
        
        temp_competition_keyboard = copy.deepcopy(admin_competition_keyboard)

        btns = []
        
        for ind, competition in enumerate(competitions, 1):
            btns.append(InlineKeyboardButton(f"{ind}. {competition.name}", callback_data=f"admin_competition__{competition.id}"))
        
        temp_competition_keyboard.add(*btns)
        
        temp_competition_keyboard.add(
            InlineKeyboardButton("◀️ Назад", callback_data="admin")
        )

    if edit:
        await message.edit_text(MESSAGES["competition_menu"], reply_markup=temp_competition_keyboard)
    else:
        await bot.send_message(message.from_user.id, MESSAGES["competition_menu"], reply_markup=temp_competition_keyboard)


@dp.callback_query_handler(AdminFilter(), lambda cmd: cmd.data == "admin_competitions")
async def competitions_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    await competitions_view(callback_query.message, True)


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
    await competitions_view(message)


# Competition detail


async def competiotion_detail_view(message: types.Message, competition_id: int, edit=False):
    with Session(engine) as session:
        competition = session.query(CompetitionModel).filter(CompetitionModel.id == competition_id).first()
        registrations = session.query(RegistrationModel).filter(RegistrationModel.competition_id == competition_id).count()
        accepted_registrations = session.query(RegistrationModel).filter(RegistrationModel.competition_id == competition_id, RegistrationModel.is_accepted == True).count()
        
        text = f"{competition.name}\n\n{competition.description}\n\n🗓Дата: {competition.date}\n\n👥Максимальное кол-во игроков: {competition.max_participants}\n\n💌Заявок: {registrations}\n\n✅Принятых заявок: {accepted_registrations}"
    
    if edit:
        await message.edit_text(text, reply_markup=admin_competition_detail_keyboard)
    else:
        await message.reply(text, reply_markup=admin_competition_detail_keyboard)


@dp.callback_query_handler(AdminFilter(), lambda cmd: "admin_competition__" in cmd.data, state="*")
async def competition_detail_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    competition_id = callback_query.data.split("__")[-1]
    
    await CompetitionDetailState.competition_id.set()
    await state.update_data(competition_id=competition_id)
    await competiotion_detail_view(callback_query.message, competition_id, True)


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
    
    await bot.send_message(callback_query.from_user.id, f"Событие было удалено")
    await competitions_handler(callback_query)


# Edit competition


@dp.callback_query_handler(AdminFilter(), lambda cmd: cmd.data == "admin_competition_edit_name", state=CompetitionDetailState.competition_id)
async def edit_competition_name_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    await CompetitionDetailState.name.set()
    
    await bot.send_message(callback_query.from_user.id, "Введите новое название для события.")


@dp.message_handler(AdminFilter(), state=CompetitionDetailState.name)
async def edit_competition_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        competition_id = data["competition_id"]
    
    with Session(engine) as session:
        competition = session.query(CompetitionModel).filter(CompetitionModel.id == competition_id).first()
        competition.name = message.text

        session.merge(competition)
        session.commit()
    
    await CompetitionDetailState.competition_id.set()
    
    await bot.send_message(message.from_user.id, f"Установлено название \"{message.text}\" для этого события.")
    await competiotion_detail_view(message, competition_id)


@dp.callback_query_handler(AdminFilter(), lambda cmd: cmd.data == "admin_competition_edit_description", state=CompetitionDetailState.competition_id)
async def edit_competition_description_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    await CompetitionDetailState.description.set()
    
    await bot.send_message(callback_query.from_user.id, "Введите новое описание для события.")


@dp.message_handler(AdminFilter(), state=CompetitionDetailState.description)
async def edit_competition_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        competition_id = data["competition_id"]
    
    with Session(engine) as session:
        competition = session.query(CompetitionModel).filter(CompetitionModel.id == competition_id).first()
        competition.description = message.text

        session.merge(competition)
        session.commit()
    
    await CompetitionDetailState.competition_id.set()
    
    await bot.send_message(message.from_user.id, f"Установлено новое описание для этого события.")
    await competiotion_detail_view(message, competition_id)


@dp.callback_query_handler(AdminFilter(), lambda cmd: cmd.data == "admin_competition_reschedule", state=CompetitionDetailState.competition_id)
async def edit_competition_date_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    await CompetitionDetailState.date.set()
    
    await bot.send_message(callback_query.from_user.id, "Введите дату проведения нового события в формате \"День.Месяц.Год Час:Минуты\", например, \"01.01.2000 10:00\".")


@dp.message_handler(AdminFilter(), state=CompetitionDetailState.date)
async def edit_competition_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        competition_id = data["competition_id"]
        
    new_date = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
    
    with Session(engine) as session:
        session.query(CompetitionModel).filter(CompetitionModel.id == competition_id).update({
            CompetitionModel.date: new_date
        })

        session.commit()
    
    await CompetitionDetailState.competition_id.set()   
    
    await bot.send_message(message.from_user.id, f"Установлена дата \"{new_date.__str__()}\" для этого события.")
    await competiotion_detail_view(message, competition_id)
