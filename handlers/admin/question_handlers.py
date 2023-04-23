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
from keyboards import go_back_keyboard


async def view_questions(callback_query: types.CallbackQuery, question_id: int):
    ...


@dp.callback_query_handler(AdminFilter(), lambda cb: cb.data == "admin_questions")
async def view_questions_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    ...
    

@dp.callback_query_handler(AdminFilter(), lambda cb: "admin_view_question_" in cb.data)
async def view_question_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    question_id = int(callback_query.data.replace("admin_view_question_", ""))
    
    ...


@dp.callback_query_handler(AdminFilter(), lambda cb: "admin_answer_question_" in cb.data)
async def answer_question_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    question_id = int(callback_query.data.replace("admin_answer_question_", ""))
    
    ...
