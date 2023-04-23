from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from aiogram import types
from sqlalchemy.orm import Session

from bot import dp, bot, MESSAGES
from models import engine, UserModel, RegistrationModel, CompetitionModel
from states import UserSignupState
from keyboards import my_registration_keyboard


@dp.callback_query_handler(lambda cb: cb.data == "my_registrations")
async def view_my_registrations_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    await callback_query.message.edit_text("Мои заявки." , reply_markup=my_registration_keyboard)


async def view_my_registration(callback_query: types.CallbackQuery, registration_id):
    with Session(engine) as session:
        is_accepted = session.query(RegistrationModel).filter(RegistrationModel.id == registration_id).first().is_accepted

        registrations = session.query(RegistrationModel).join(
            UserModel, UserModel.id == RegistrationModel.user_id    
        ).join(
            CompetitionModel, RegistrationModel.competition_id == CompetitionModel.id    
        ).filter(
            RegistrationModel.is_accepted == is_accepted,
            CompetitionModel.date >= datetime.now(),
            UserModel.telegram_id == callback_query.from_user.id
        ).all()

        count = len(registrations)
        
        index = list(map(lambda x: x.id, registrations)).index(registration_id)
        competition: CompetitionModel = registrations[index].competition
        
        text = f"Заявка {index + 1} из {count}:\n\n"

        text += f"📋Событие: {competition.name}\n\n🎮Игра: {competition.game}\n\n🗓Дата: {competition.date}"
        
        keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
        
        btns = []

        if index > 0:
            another_reg_id = registrations[index - 1].id
    
            btns.append(
                InlineKeyboardButton("<<<", callback_data=f"view_my_registration_{another_reg_id}")
            )

        if index < count - 1:
            another_reg_id = registrations[index + 1].id

            btns.append(
                InlineKeyboardButton(">>>", callback_data=f"view_my_registration_{another_reg_id}")
            )
        
        keyboard.add(InlineKeyboardButton("❌ Отменить", callback_data=f"cancel_my_registration_{registration_id}"))
        keyboard.add(*btns)
        keyboard.add(
            InlineKeyboardButton("◀️ Назад", callback_data=f"my_registrations")
        )
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)


@dp.callback_query_handler(lambda cb: cb.data == "submitted_registrations")
async def my_submitted_registrations_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    with Session(engine) as session:
        registration = session.query(RegistrationModel).join(
            UserModel, UserModel.id == RegistrationModel.user_id    
        ).join(
            CompetitionModel, RegistrationModel.competition_id == CompetitionModel.id    
        ).filter(
            RegistrationModel.is_accepted == False,
            CompetitionModel.date >= datetime.now(),
            UserModel.telegram_id == callback_query.from_user.id
        ).first()
    
    if registration:
        await view_my_registration(callback_query, registration.id)
    else:
        await bot.send_message(callback_query.from_user.id, "У вас нет поданных заявок.")
        

@dp.callback_query_handler(lambda cb: cb.data == "approved_registrations")
async def my_approved_registrations_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    with Session(engine) as session:
        registration = session.query(RegistrationModel).join(
            UserModel, UserModel.id == RegistrationModel.user_id    
        ).join(
            CompetitionModel, RegistrationModel.competition_id == CompetitionModel.id    
        ).filter(
            RegistrationModel.is_accepted == True,
            CompetitionModel.date >= datetime.now(),
            UserModel.telegram_id == callback_query.from_user.id
        ).first()
    
    if registration:
        await view_my_registration(callback_query, registration.id)
    else:
        await bot.send_message(callback_query.from_user.id, "Вы пока что нигде не участвуете.")


@dp.callback_query_handler(lambda cb: "view_my_registration_" in cb.data)
async def view_my_registration_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    registration_id = int(callback_query.data.replace("view_my_registration_", ""))
    
    await view_my_registration(callback_query, registration_id)
    

@dp.callback_query_handler(lambda cb: "cancel_my_registration_" in cb.data)
async def cencel_my_registration_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    registration_id = int(callback_query.data.replace("cancel_my_registration_", ""))
    
    with Session(engine) as session:
        registration = session.query(RegistrationModel).filter(
            RegistrationModel.id == registration_id
        ).first()
        
        user = session.query(UserModel).filter(
            UserModel.telegram_id == callback_query.from_user.id
        ).first()
        
        competition_name = session.query(CompetitionModel).filter(
            CompetitionModel.id == registration.competition_id
        ).first().name
    
        is_accepted = registration.is_accepted
        
        if registration.is_accepted:
            admins = session.query(UserModel.telegram_id).filter(
                UserModel.is_admin == True
            ).all()
            
            for admin_id, *_ in admins:
                await bot.send_message(admin_id, f"Пользователь {user.name} {user.surname} из {user.class_number} {user.class_letter} отменил свое участие в {competition_name}.")
        
        session.query(RegistrationModel).filter(
            RegistrationModel.id == registration_id
        ).delete()
        session.commit()

    await bot.send_message(callback_query.from_user.id, "Вы удалили свою заявку.")

    if is_accepted:
        await my_approved_registrations_callback(callback_query)
    else:
        await my_submitted_registrations_callback(callback_query)
