from aiogram.dispatcher import FSMContext
from aiogram import types
from sqlalchemy.orm import Session

from bot import dp, bot, MESSAGES
from models import engine
from states import CompetitionListState
from keyboards import competition_keyboard


@dp.callback_query_handler(lambda cmd: cmd.data == "competition_list")
async def competiotion_list(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.edit_text("Список турниров:", reply_markup=competition_keyboard)


@dp.callback_query_handler(lambda cmd: cmd.data == "competition_next")
async def competiotion_next(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.edit_text("Список турниров 1", reply_markup=competition_keyboard)


@dp.callback_query_handler(lambda cmd: cmd.data == "competition_prev")
async def competiotion_prev(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.edit_text("Список турниров -1", reply_markup=competition_keyboard)
