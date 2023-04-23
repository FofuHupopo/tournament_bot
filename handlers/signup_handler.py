import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, ReplyKeyboardRemove
from sqlalchemy.orm import Session

from .main_handlers import main_handler
from models import engine, UserModel
from bot import dp, bot, MESSAGES
from states import UserSignupState


@dp.callback_query_handler(lambda cb: cb.data == "signup")
async def start_signup(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    await bot.send_message(callback_query.from_user.id, "Введите ваш email")
    await UserSignupState.mail.set()


@dp.message_handler(state=UserSignupState.mail)
async def process_mail(message: types.Message, state: FSMContext):
    mail = message.text.strip()
    
    if not is_valid_email(message.text):
        await message.reply("Некорректный email. Пожалуйста, введите еще раз.")
        return

    await state.update_data(mail=mail)
    await message.answer("Введите вашу фамилию")
    await UserSignupState.surname.set()


@dp.message_handler(state=UserSignupState.surname)
async def process_surname(message: types.Message, state: FSMContext):
    surname = message.text.strip()
    
    if not surname.isalpha():
        await message.reply("Фамилия должна состоять только из букв. Пожалуйста, введите еще раз.")
        return
    
    if len(surname.split()) != 1:
        await message.reply("Фамилия должна состоять только из одного слова. Пожалуйста, введите еще раз.")
        return

    await state.update_data(surname=surname)
    await message.answer("Введите ваше имя")
    await UserSignupState.name.set()


@dp.message_handler(state=UserSignupState.name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    
    if not name.isalpha():
        await message.reply("Имя должно состоять только из букв. Пожалуйста, введите еще раз.")
        return
    
    if len(name.split()) != 1:
        await message.reply("Имя должно состоять только из одного слова. Пожалуйста, введите еще раз.")
        return
    
    await state.update_data(name=name)
    await message.answer("Введите номер вашего класса")
    await UserSignupState.class_number.set()
    
    
@dp.message_handler(state=UserSignupState.class_number)
async def process_class_number(message: types.Message, state: FSMContext):
    class_number = message.text.strip()
    
    if not class_number.isdigit():
        await message.reply("Номер класса должен быть числом. Пожалуйста, введите еще раз.")
        return
    
    if not (1 <= int(class_number) <= 11):
        await message.reply("Номер класса должен быть в промежутке от 1 до 11. Пожалуйста, введите еще раз.")
        return

    await state.update_data(class_number=class_number)
    await message.answer("Введите букву вашего класса")
    await UserSignupState.class_letter.set()


@dp.message_handler(state=UserSignupState.class_letter)
async def process_class_letter(message: types.Message, state: FSMContext):
    class_letter = message.text.strip()
    
    if not class_letter.isalpha():
        await message.reply("Буква класса должна быть буквой. Пожалуйста, введите еще раз.")
        return
    
    if len(class_letter) != 1:
        await message.reply("Буква класса должна быть только одной. Пожалуйста, введите еще раз.")
        return
    
    if class_letter.lower() not in ("а", "б", "в"):
        await message.reply("Буква класса должна быть только \"А\", \"Б\" или \"В\". Пожалуйста, введите еще раз.")
        return
    
    await state.update_data(class_letter=class_letter)

    user_data = await state.get_data()
    
    with Session(engine) as session:
        user = UserModel(
            telegram_id=message.from_user.id,
            mail=user_data["mail"],
            name=user_data["name"].title(),
            surname=user_data["surname"].title(),
            class_letter=user_data["class_letter"].title(),
            class_number=user_data["class_number"],
        )
        
        session.add(user)
        session.commit()
    
    await state.finish()
    await message.answer("Вы успешно зарегистрировались!")
    await main_handler(message)


def is_valid_email(mail):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, mail) is not None
