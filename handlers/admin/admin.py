from aiogram.dispatcher import FSMContext, filters
from aiogram.types import ReplyKeyboardRemove

from .filter import AdminFilter
from keyboards import admin_keyboard
from bot import dp, bot, MESSAGES
from aiogram import types


@dp.message_handler(AdminFilter(), commands=['admin'])
async def admin_handler(message: types.Message):
    await message.reply(MESSAGES["admin"], reply_markup=admin_keyboard)


@dp.callback_query_handler(lambda cb: cb.data == "admin")
async def admin_callback(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(MESSAGES["admin"], reply_markup=admin_keyboard)
    

@dp.message_handler(AdminFilter(), filters.Text(equals='Выйти', ignore_case=True), state='*')
async def goback_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.from_id, "Вы вышли из меню.", reply_markup=ReplyKeyboardRemove())
    await admin_handler(message)
