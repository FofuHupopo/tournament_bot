from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from aiogram import types
from sqlalchemy.orm import Session

from bot import dp, bot
from models import engine, QuestionModel, UserModel
from states import QuestionState
from keyboards import ask_question_keyboard


@dp.callback_query_handler(lambda cb: cb.data == "ask_question")
async def ask_question_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    await callback_query.message.edit_text(f"Меню вопросов.", reply_markup=ask_question_keyboard)


@dp.callback_query_handler(lambda cb: cb.data == "ask")
async def ask_question_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    with Session(engine) as session:
        not_answered_questions_count = session.query(QuestionModel).join(
            UserModel, UserModel.id == QuestionModel.user_id 
        ).filter(
            QuestionModel.is_answered == False,
            UserModel.telegram_id == callback_query.from_user.id
        ).count()
        
        
    if not_answered_questions_count > 0:
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            InlineKeyboardButton("◀️ Назад", callback_data="ask_question")
        )
    
        await callback_query.message.edit_text(f"Вы уже задали вопрос. Дождитесь ответа на предыдущий.", reply_markup=keyboard)
    else:
        await callback_query.message.edit_text(f"Введите текст вопроса:")
        await QuestionState.question.set()


@dp.message_handler(state=QuestionState.question)
async def ask_question_callback(message: types.Message, state: FSMContext):    
    await state.finish()
    
    with Session(engine) as session:
        user = session.query(UserModel).filter(
            UserModel.telegram_id == message.from_user.id
        ).first()

        question = QuestionModel(
            user_id=user.id,
            question=message.text
        )
        
        session.add(question)
        session.commit()
    
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        InlineKeyboardButton("◀️ Назад", callback_data="ask_question")
    )
        
    await bot.send_message(message.from_user.id, "Ваш вопрос отправлен команде администраторов.", reply_markup=keyboard)
    
    with Session(engine) as session:
        admins = session.query(UserModel.telegram_id).filter(
            UserModel.is_admin == True
        ).all()
        user = session.query(UserModel).filter(
            UserModel.telegram_id == message.from_user.id
        ).first()

        admins = list(map(lambda x: int(x[0]), admins))
        
        for admin in admins:
            await bot.send_message(admin, f"Появился новый вопрос от пользователя {user.name} {user.surname} из {user.class_number} {user.class_letter}.")


async def view_my_questions(callback_query: types.CallbackQuery, question_id: int):
    with Session(engine) as session:
        questions = session.query(QuestionModel).join(
            UserModel, UserModel.id == QuestionModel.user_id    
        ).filter(
            UserModel.telegram_id == callback_query.from_user.id
        ).all()

        count = len(questions)
        
        index = list(map(lambda x: x.id, questions)).index(question_id)
        
        text = f"Вопрос {index + 1} из {count}:\n\n"

        text += f"❔Вопрос: {questions[index].question}\n\n🗓Дата: {questions[index].date}"
        
        if questions[index].is_answered:
            text += f"\n\n📢Ответ: {questions[index].answer}"
        
        keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
        
        btns = []

        if index > 0:
            another_reg_id = questions[index - 1].id
    
            btns.append(
                InlineKeyboardButton("<<<", callback_data=f"view_my_question_{another_reg_id}")
            )

        if index < count - 1:
            another_reg_id = questions[index + 1].id

            btns.append(
                InlineKeyboardButton(">>>", callback_data=f"view_my_question_{another_reg_id}")
            )
        
        keyboard.add(*btns)
        keyboard.add(
            InlineKeyboardButton("◀️ Назад", callback_data=f"ask_question")
        )
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)


@dp.callback_query_handler(lambda cb: "view_my_question_" in cb.data)
async def view_my_question_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    question_id = int(callback_query.data.replace("view_my_question_", ""))
    
    await view_my_questions(callback_query, question_id)


@dp.callback_query_handler(lambda cb: cb.data == "answers")
async def view_my_questions_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    with Session(engine) as session:
        question = session.query(QuestionModel).join(
            UserModel, UserModel.id == QuestionModel.user_id    
        ).filter(
            UserModel.telegram_id == callback_query.from_user.id
        ).first()

    if question:
        await view_my_questions(callback_query, question.id)
    else:
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            InlineKeyboardButton("◀️ Назад", callback_data=f"ask_question")
        )
        
        await callback_query.message.edit_text("Вы пока что не задали ни один вопрос.", reply_markup=keyboard)
