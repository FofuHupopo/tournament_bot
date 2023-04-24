from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.orm import Session

from .admin import *
from .filter import AdminFilter

from models import engine, UserModel, QuestionModel
from bot import dp, bot
from states import AnswerState
from keyboards import admin_question_keyboard


async def view_question(callback_query: types.CallbackQuery, question_id: int):
    with Session(engine) as session:
        is_answered = session.query(QuestionModel).filter(
            QuestionModel.id == question_id
        ).first().is_answered

        questions = session.query(QuestionModel).filter(
            QuestionModel.is_answered == is_answered
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
                InlineKeyboardButton("<<<", callback_data=f"admin_view_question_{another_reg_id}")
            )

        if index < count - 1:
            another_reg_id = questions[index + 1].id

            btns.append(
                InlineKeyboardButton(">>>", callback_data=f"admin_view_question_{another_reg_id}")
            )
            
        if not questions[index].is_answered:
            keyboard.add(
                InlineKeyboardButton("🗣 Ответить", callback_data=f"admin_answer_question_{question_id}")
            )

        keyboard.add(*btns)
        keyboard.add(
            InlineKeyboardButton("◀️ Назад", callback_data=f"admin_questions")
        )
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)


@dp.callback_query_handler(AdminFilter(), lambda cb: cb.data == "admin_questions")
async def view_questions_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    await callback_query.message.edit_text("Меню вопросов.", reply_markup=admin_question_keyboard)
    

@dp.callback_query_handler(AdminFilter(), lambda cb: cb.data == "admin_view_questions")
async def view_questions_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    with Session(engine) as session:
        question = session.query(QuestionModel).filter(
            QuestionModel.is_answered == False
        ).first()

    if question:
        await view_question(callback_query, question.id)
    else:
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            InlineKeyboardButton("◀️ Назад", callback_data="admin_questions")
        )

        await callback_query.message.edit_text("Пока что нет неотвеченных вопросов.", reply_markup=keyboard)


@dp.callback_query_handler(AdminFilter(), lambda cb: "admin_view_question_" in cb.data)
async def view_question_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    question_id = int(callback_query.data.replace("admin_view_question_", ""))
    
    await view_question(callback_query, question_id)


@dp.callback_query_handler(AdminFilter(), lambda cb: "admin_answer_question_" in cb.data)
async def start_answer_question_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    question_id = int(callback_query.data.replace("admin_answer_question_", ""))
    
    async with state.proxy() as data:
        data["question_id"] = question_id

    await AnswerState.answer.set()
    await bot.send_message(callback_query.from_user.id, "Введите текст ответа:")
    

@dp.message_handler(AdminFilter(), state=AnswerState.answer)
async def end_answer_question_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        answer = message.text
        question_id = data["question_id"]
    
    await state.finish()
    
    with Session(engine) as session:
        session.query(QuestionModel).filter(
            QuestionModel.id == question_id
        ).update({
            QuestionModel.answer: answer,
            QuestionModel.is_answered: True
        })
        
        user_telegram_id = session.query(UserModel).join(
            QuestionModel, UserModel.id == QuestionModel.user_id
        ).filter(
            QuestionModel.id == question_id
        ).first().telegram_id
        
        session.commit()

    await bot.send_message(user_telegram_id, "Вам отправлен ответ на ваш вопрос.")
    
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        InlineKeyboardButton("◀️ Назад", callback_data="admin_questions")
    )
    
    await bot.send_message(message.from_user.id, "Ответ был успешно отправлен", reply_markup=keyboard)


@dp.callback_query_handler(AdminFilter(), lambda cb: cb.data == "admin_answered_questions")
async def view_questions_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    with Session(engine) as session:
        question = session.query(QuestionModel).filter(
            QuestionModel.is_answered == True
        ).first()

    if question:
        await view_question(callback_query, question.id)
    else:
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            InlineKeyboardButton("◀️ Назад", callback_data="admin_questions")
        )

        await callback_query.message.edit_text("Вы не ответили ни на один вопрос.", reply_markup=keyboard)