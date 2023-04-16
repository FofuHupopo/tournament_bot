from aiogram.dispatcher import FSMContext
from aiogram import types
from sqlalchemy.orm import Session

from states import JoinState
from bot import dp, bot, MESSAGES
from models import UserModel, engine


@dp.callback_query_handler(lambda cmd: cmd.data == "join")
async def join_1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await JoinState.name.set()
    await bot.send_message(callback_query.message.chat.id, MESSAGES["join_1"])


@dp.message_handler(state=JoinState.name)
async def join_2(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await JoinState.next()
    await message.reply(MESSAGES["join_2"])


@dp.message_handler(state=JoinState.mail)
async def join_3(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['mail'] = message.text

    await JoinState.next()
    await message.reply(MESSAGES["join_3"])
    

@dp.message_handler(state=JoinState.nickname)
async def join_success(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['nickname'] = message.text
        
        with Session(engine) as session:
            user = UserModel(
                telegram_id=message.chat.id,
                name=data["name"],
                mail=data["mail"],
                nickname=data["nickname"]
            )
            
            session.add(user)
            session.commit()

    await state.finish()
    await message.reply(MESSAGES["join_success"])
