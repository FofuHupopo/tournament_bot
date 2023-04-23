import asyncio
import copy
from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils import exceptions
from aiogram.types import InlineKeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup
from sqlalchemy.orm import Session, joinedload

from .admin import *
from .filter import AdminFilter

from models import engine, CompetitionModel, RegistrationModel, UserModel
from bot import dp, bot, MESSAGES
from states import (
    CompetitionDetailState, AddCompetitionState
)
from keyboards import (
    go_back_keyboard, admin_competition_keyboard,
    admin_competition_detail_keyboard, admin_notification_keyboard,
    admin_view_registrations_keyboard
)


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
    try:
        datetime.strptime(message.text, "%d.%m.%Y %H:%M")
    except ValueError:
        await message.answer("Вы ввели дату в неверном формате. Попробуйте снова.")
        return

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
        
        text = f"{competition.name}\n\n{competition.description}\n\n🎮Игра: {competition.game}\n\n🗓Дата: {competition.date}\n\n👥Максимальное кол-во игроков: {competition.max_participants}\n\n💌Новых заявок: {registrations - accepted_registrations}\n\n👥Участники: {accepted_registrations}"
    
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


@dp.callback_query_handler(AdminFilter(), lambda cmd: cmd.data == "admin_competition_notificate", state=CompetitionDetailState.competition_id)
async def competition_notification_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    await CompetitionDetailState.notification.set()
    
    await callback_query.message.edit_text("Введите текст для рассылки:")


@dp.message_handler(AdminFilter(), state=CompetitionDetailState.notification)
async def competition_notification_set_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["notification"] = message.text
        
    await CompetitionDetailState.competition_id.set()
    
    await bot.send_message(message.from_user.id, "Выберите группу людей для рассылки.", reply_markup=admin_notification_keyboard)


@dp.callback_query_handler(AdminFilter(), lambda cb: cb.data == "notificate_go_back", state=CompetitionDetailState.competition_id)
async def admin_go_back_notification(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    async with state.proxy() as data:
        competition_id = data["competition_id"]
    
    await state.finish()
    
    await competiotion_detail_view(callback_query.message, competition_id, True)


@dp.callback_query_handler(
    AdminFilter(),
    lambda cmd: cmd.data in ["notificate_all", "notificate_registrations", "notificate_participants"],
    state=CompetitionDetailState.competition_id
)
async def send_notification_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    async with state.proxy() as data:
        competition_id = data["competition_id"]
        notification = data["notification"]
    
    with Session(engine) as session:
        if callback_query.data == "notificate_registrations":
            users = session.query(UserModel.telegram_id).join(
                RegistrationModel, UserModel.id == RegistrationModel.user_id
            ).filter(
                RegistrationModel.competition_id == competition_id,
                RegistrationModel.is_accepted == False
            ).options(joinedload('registrations')).all()
        elif callback_query.data == "notificate_participants":
            users = session.query(UserModel.telegram_id).join(
                RegistrationModel, UserModel.id == RegistrationModel.user_id
            ).filter(
                RegistrationModel.competition_id == competition_id,
                RegistrationModel.is_accepted == True
            ).options(joinedload('registrations')).all()
        else:
            users = session.query(UserModel.telegram_id).all()
        
        users = list(map(lambda x: int(x[0]), users))
    
    if users:
        for user in users:
            try:
                await bot.send_message(user, notification)
            except exceptions.RetryAfter as e:
                print(f"Отправлено много запросов, нужно подождать {e.timeout} секунд")
                await asyncio.sleep(e.timeout)
            except exceptions.TelegramAPIError:
                print("Ошибка Telegram API при отправке сообщения")
        
        await bot.send_message(callback_query.from_user.id, f"Было отправлено {len(users)} сообщений.")
    else:
        await bot.send_message(callback_query.from_user.id, f"Нет пользователей, подходящих под эту группу.")
        
    await competiotion_detail_view(callback_query.message, competition_id)


# View participants

async def view_participant(callback_query: types.CallbackQuery, competition_id: int, registration_id: int):
    with Session(engine) as session:
        registrations = session.query(RegistrationModel).join(
            CompetitionModel, CompetitionModel.id == RegistrationModel.competition_id
        ).filter(
            RegistrationModel.is_accepted == True,
            CompetitionModel.id == competition_id
        ).all()
        
        count = len(registrations)
        
        index = list(map(lambda x: x.id, registrations)).index(registration_id)
        
        text = f"Участник {index + 1} из {count}:\n\n"
        
        user = session.query(UserModel).filter(UserModel.telegram_id == callback_query.from_user.id).first()
        
        text += f"👨ФИ: {user.name} {user.surname}\n\n🏫Класс: {user.class_number} {user.class_letter}\n\n📧Почта: {user.mail}\n\n🕹Никнейм: {registrations[index].nickname}"
        
        keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
        
        btns = []
        
        if index > 0:
            another_reg_id = registrations[index - 1].id
    
            btns.append(
                InlineKeyboardButton("<<<", callback_data=f"admin_view_participant_{another_reg_id}")
            )
            
        if index < count - 1:
            another_reg_id = registrations[index + 1].id

            btns.append(
                InlineKeyboardButton(">>>", callback_data=f"admin_view_participant_{another_reg_id}")
            )
        
        keyboard.add(*btns)
        keyboard.add(
            InlineKeyboardButton("◀️ Назад", callback_data=f"admin_competition__{competition_id}")
        )
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        
    
@dp.callback_query_handler(AdminFilter(), lambda cb: cb.data == "admin_view_participants", state=CompetitionDetailState.competition_id)
async def admin_view_participants_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    async with state.proxy() as data:
        competition_id = data["competition_id"]
    
    with Session(engine) as session:
        registration = session.query(RegistrationModel).join(
            CompetitionModel, CompetitionModel.id == RegistrationModel.competition_id    
        ).filter(
            CompetitionModel.id == competition_id,
            RegistrationModel.is_accepted == True
        ).order_by(RegistrationModel.date).first()
        
        if not registration:
            await bot.send_message(callback_query.from_user.id, "Участников нет.")
            return
    
    await view_participant(callback_query, competition_id, registration.id)
    

@dp.callback_query_handler(AdminFilter(), lambda cb: "admin_view_participant_" in cb.data, state=CompetitionDetailState.competition_id)
async def admin_view_participant_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    async with state.proxy() as data:
        competition_id = data["competition_id"]
    
    registration_id = int(callback_query.data.replace("admin_view_participant_", ""))
    
    await view_participant(callback_query, competition_id, registration_id)
    
    
# View new Registrations

async def view_registration(callback_query: types.CallbackQuery, competition_id, registration_id: int):
    with Session(engine) as session:
        registrations = session.query(RegistrationModel).join(
            CompetitionModel, CompetitionModel.id == RegistrationModel.competition_id
        ).filter(
            RegistrationModel.is_accepted == False,
            CompetitionModel.id == competition_id
        ).all()
        
        count = len(registrations)
        
        index = list(map(lambda x: x.id, registrations)).index(registration_id)
        
        text = f"Заявка {index + 1} из {count}:\n\n"
        
        user = session.query(UserModel).filter(UserModel.telegram_id == callback_query.from_user.id).first()
        
        text += f"👨ФИ: {user.name} {user.surname}\n\n🏫Класс: {user.class_number} {user.class_letter}\n\n📧Почта: {user.mail}\n\n🕹Никнейм: {registrations[index].nickname}\n\n🗓Дата заявки: {registrations[index].date}"
        
        keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
        
        btns = [
            InlineKeyboardButton("✅ Одобрить", callback_data=f"admin_approve_registration_{registration_id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"admin_reject_registration_{registration_id}")
        ]
        
        if index > 0:
            another_reg_id = registrations[index - 1].id
    
            btns.append(
                InlineKeyboardButton("<<<", callback_data=f"admin_view_registration_{another_reg_id}")
            )
            
        if index < count - 1:
            another_reg_id = registrations[index + 1].id

            btns.append(
                InlineKeyboardButton(">>>", callback_data=f"admin_view_registration_{another_reg_id}")
            )
        
        keyboard.add(*btns)
        keyboard.add(
            InlineKeyboardButton("◀️ Назад", callback_data=f"admin_competition__{competition_id}")
        )
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)


@dp.callback_query_handler(AdminFilter(), lambda cb: "admin_view_registration_" in cb.data, state=CompetitionDetailState.competition_id)
async def admin_view_registration_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    async with state.proxy() as data:
        competition_id = data["competition_id"]
    
    registration_id = int(callback_query.data.replace("admin_view_registration_", ""))
    
    await view_registration(callback_query, competition_id, registration_id)
    

@dp.callback_query_handler(AdminFilter(), lambda cb: "admin_approve_registration_" in cb.data, state=CompetitionDetailState.competition_id)
async def admin_view_registration_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    async with state.proxy() as data:
        competition_id = data["competition_id"]
    
    registration_id = int(callback_query.data.replace("admin_approve_registration_", ""))

    with Session(engine) as session:
        user_telegram_id = session.query(UserModel).join(
            RegistrationModel, UserModel.id == RegistrationModel.user_id
        ).filter(RegistrationModel.id == registration_id).first().telegram_id
        competition_name = session.query(CompetitionModel).filter(CompetitionModel.id == competition_id).first().name
        
        session.query(RegistrationModel).filter(RegistrationModel.id == registration_id).update({"is_accepted": True})
        session.commit()
        
    
    await bot.send_message(user_telegram_id, f"Ваша заявка на событие \"{competition_name}\" была одобрена.")
    
    await admin_view_registrations_callback(callback_query, state)
    

@dp.callback_query_handler(AdminFilter(), lambda cb: "admin_reject_registration_" in cb.data, state=CompetitionDetailState.competition_id)
async def admin_view_registration_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    async with state.proxy() as data:
        competition_id = data["competition_id"]
    
    registration_id = int(callback_query.data.replace("admin_reject_registration_", ""))

    with Session(engine) as session:
        user_telegram_id = session.query(UserModel).join(
            RegistrationModel, UserModel.id == RegistrationModel.user_id
        ).filter(RegistrationModel.id == registration_id).first().telegram_id
        competition_name = session.query(CompetitionModel).filter(CompetitionModel.id == competition_id).first().name

        session.query(RegistrationModel).filter(RegistrationModel.id == registration_id).delete()
        session.commit()

    
    await bot.send_message(user_telegram_id, f"Ваша заявка на событие \"{competition_name}\" была отклонена.\nПроверьте, не нарушаете ли вы правила.")
    
    await admin_view_registrations_callback(callback_query, state)


@dp.callback_query_handler(AdminFilter(), lambda cb: cb.data == "admin_view_registrations", state=CompetitionDetailState.competition_id)
async def admin_view_registrations_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    async with state.proxy() as data:
        competition_id = data["competition_id"]
    
    with Session(engine) as session:
        registration = session.query(RegistrationModel).join(
            CompetitionModel, CompetitionModel.id == RegistrationModel.competition_id    
        ).filter(
            CompetitionModel.id == competition_id,
            RegistrationModel.is_accepted == False
        ).order_by(RegistrationModel.date).first()
        
        if not registration:
            await bot.send_message(callback_query.from_user.id, "Новых заявок нет.")
            return
    
    await view_registration(callback_query, competition_id, registration.id)



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
    
    try:
        new_date = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
    except ValueError:
        await message.answer("Вы ввели дату в неверном формате. Попробуйте снова.")
        return
        
    
    with Session(engine) as session:
        session.query(CompetitionModel).filter(CompetitionModel.id == competition_id).update({
            CompetitionModel.date: new_date
        })

        session.commit()
    
    await CompetitionDetailState.competition_id.set()   
    
    await bot.send_message(message.from_user.id, f"Установлена дата \"{new_date.__str__()}\" для этого события.")
    await competiotion_detail_view(message, competition_id)

