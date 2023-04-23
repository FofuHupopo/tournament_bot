from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from aiogram import types
from sqlalchemy.orm import Session

from bot import dp, bot
from models import engine, CompetitionModel, RegistrationModel, UserModel
from states import RegistrationState
from handlers.main_handlers import main_handler


async def view_competition(callback_query: types.CallbackQuery, competition_id: int):
    with Session(engine) as session:
        competitions = session.query(CompetitionModel).filter(CompetitionModel.date >= datetime.now()).all()
        count = len(competitions)
        
        index = list(map(lambda x: x.id, competitions)).index(competition_id)
        
        text = f"Событие {index + 1} из {count}:\n\n"
        
        competition: CompetitionModel = session.query(CompetitionModel).get({"id": competition_id})
        accepted_registrations: int = session.query(RegistrationModel).filter(
            RegistrationModel.competition_id == competition_id,
            RegistrationModel.is_accepted == True
        ).count()
        
        text += f"{competition.name}\n\n{competition.description}\n\n🎮Игра: {competition.game}\n\n🗓Дата: {competition.date}\n\n👥Кол-во игроков: {accepted_registrations} из {competition.max_participants}"
        
        keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
        
        
        is_registered = session.query(RegistrationModel).join(UserModel, RegistrationModel.user_id == UserModel.id).filter(
            UserModel.telegram_id == callback_query.from_user.id,
            RegistrationModel.competition_id == competition_id
        ).first()
        
        if is_registered:
            if is_registered.is_accepted:
                keyboard.add(
                    InlineKeyboardButton("✅ Вы уже участвуете", callback_data=f"empty")
                )
            else:
                keyboard.add(
                    InlineKeyboardButton("⏳ Вы уже зарегистрировались", callback_data=f"empty")
                )
        else:
            keyboard.add(
                InlineKeyboardButton("🕹 Участвовать", callback_data=f"registrate_to_{competition_id}")
            )
        
        btns = []
        
        if index > 0:
            another_comp_id = competitions[index - 1].id
    
            btns.append(
                InlineKeyboardButton("<<<", callback_data=f"view_competition_{another_comp_id}")
            )
            
        if index < count - 1:
            another_comp_id = competitions[index + 1].id

            btns.append(
                InlineKeyboardButton(">>>", callback_data=f"view_competition_{another_comp_id}")
            )
        
        keyboard.add(*btns)
        keyboard.add(
            InlineKeyboardButton("◀️ Назад", callback_data="menu")
        )
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)


@dp.callback_query_handler(lambda cb: "view_competition_" in cb.data)
async def view_competition_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    competition_id = int(callback_query.data.replace("view_competition_", ""))
    
    await view_competition(callback_query, competition_id)


@dp.callback_query_handler(lambda cmd: cmd.data == "competition_list")
async def competiotion_list(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    with Session(engine) as session:
        competition = session.query(CompetitionModel).filter(CompetitionModel.date >= datetime.now()).order_by(CompetitionModel.id).first()
        
        if competition:
            await view_competition(callback_query, competition.id)
        else:
            await bot.send_message(callback_query.from_user.id, "Пока никаких событий нет.")


@dp.callback_query_handler(lambda cb: "registrate_to_" in cb.data)
async def start_registration_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    competition_id = int(callback_query.data.replace("registrate_to_", ""))
    
    with Session(engine) as session:
        game = session.query(CompetitionModel).filter(CompetitionModel.id == competition_id).first().game
    
    await RegistrationState.nickname.set()
    
    async with state.proxy() as data:
        data["competition_id"] = competition_id
    
    await bot.send_message(callback_query.from_user.id, f"Введите ваш никнейм, который вы использутете в игре {game}:")


@dp.message_handler(state=RegistrationState.nickname)
async def end_registration_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["nickname"] = message.text
        competition_id = data["competition_id"]

    await state.finish()
    
    with Session(engine) as session:
        user = session.query(UserModel).filter(UserModel.telegram_id == message.from_user.id).first()

        registration = RegistrationModel(
            user_id=user.id,
            nickname=message.text,
            competition_id=competition_id,
            is_accepted=False
        )
        
        session.add(registration)
        session.commit()
    
    await bot.send_message(message.from_user.id, "Вы успешно отправили заявку на участие в событии.")
    await main_handler(message)
