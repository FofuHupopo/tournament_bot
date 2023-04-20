import copy
from rcon.source import rcon
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, ReplyKeyboardRemove
from sqlalchemy.orm import Session

from .admin import *
from .filter import AdminFilter

from models import engine, RconRuleModel
from bot import dp, bot, MESSAGES
from states import RconCommandState, AddRconRuleState
from keyboards import rcon_keyboard, go_back_keyboard


# Add RCON rule

@dp.callback_query_handler(AdminFilter(), lambda cmd: cmd.data == "admin_add_rcon")
async def start_add_rcon_rule(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    await AddRconRuleState.name.set()
    await bot.send_message(callback_query.from_user.id, text="Введите название нового RCON подключения.", reply_markup=go_back_keyboard)


@dp.message_handler(AdminFilter(), state=AddRconRuleState.name)
async def get_server_ip(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await AddRconRuleState.server_ip.set()
    await message.answer(f"Введите ip адрес для нового rcon подключения.", reply_markup=go_back_keyboard)


@dp.message_handler(AdminFilter(), state=AddRconRuleState.server_ip)
async def get_server_port(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['server_ip'] = message.text

    await AddRconRuleState.server_port.set()
    await message.answer(f"Введите порт для нового rcon подключения.", reply_markup=go_back_keyboard)


@dp.message_handler(AdminFilter(), state=AddRconRuleState.server_port)
async def get_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['server_port'] = message.text

    await AddRconRuleState.password.set()
    await message.answer(f"Введите пароль для нового rcon подключения.", reply_markup=go_back_keyboard)


@dp.message_handler(AdminFilter(), state=AddRconRuleState.password)
async def create_rcon_rule(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text

        name = data['name']
        server_ip = data['server_ip']
        server_port = data['server_port']
        password = data['password']

        with Session(engine) as session:
            new_rule = RconRuleModel(
                name=name,
                ip=server_ip,
                port=server_port,
                password=password
            )
            
            session.add(new_rule)
            session.commit()

    await state.finish()
    await message.answer("Новое RCON подключение было создано.", reply_markup=ReplyKeyboardRemove())
    await rcon_menu_view(message)
    

# RCON Management

async def rcon_menu_view(message: types.Message, edit=False):
    with Session(engine) as session:
        rcon_rules = session.query(RconRuleModel).all()
        
        temp_rcon_keyboard = copy.deepcopy(rcon_keyboard)
        
        btns = []
    
        for ind, rule in enumerate(rcon_rules, 1):
            btns.append(InlineKeyboardButton(f"{ind}. {rule.name}", callback_data=f"admin_rcon_conn__{rule.name}"))
        
        temp_rcon_keyboard.add(*btns)
        
        temp_rcon_keyboard.add(
            InlineKeyboardButton("◀️ Назад", callback_data="admin")
        )

    if edit:
        await message.edit_text(MESSAGES["rcon_menu"], reply_markup=temp_rcon_keyboard)
    else:
        await bot.send_message(message.from_user.id, MESSAGES["rcon_menu"], reply_markup=temp_rcon_keyboard)


@dp.callback_query_handler(AdminFilter(), lambda cmd: cmd.data == "admin_rcon")
async def rcon_menu_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    await rcon_menu_view(callback_query.message, True)


@dp.callback_query_handler(AdminFilter(), lambda cmd: "admin_rcon_conn__" in cmd.data, state=None)
async def rcon_connection_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    server_name = callback_query.data.split("__")[-1]
    
    await RconCommandState.cmd.set()
    
    async with state.proxy() as data:
        data["server_name"] = server_name
        
    with Session(engine) as session:
        server = session.query(RconRuleModel).filter(RconRuleModel.name == server_name).first()

        try:
            response = await rcon(
                "list",
                host=server.ip, port=server.port, passwd=server.password
            )
            
            await bot.send_message(callback_query.from_user.id, f"Вы подключились к серверу \"{server_name}\".\nВведите команду:", reply_markup=go_back_keyboard)
        except ConnectionRefusedError:
            await bot.send_message(callback_query.from_user.id, f"Сервер \"{server_name}\" не доступен.", reply_markup=ReplyKeyboardRemove())
            await state.finish()


@dp.message_handler(AdminFilter(), state=RconCommandState.cmd)
async def send_rcon_cmd_handler(message: types.Message, state: FSMContext):
    cmd = message.text.split()
    
    async with state.proxy() as data:
        server_name = data["server_name"]

    with Session(engine) as session:
        server = session.query(RconRuleModel).filter(RconRuleModel.name == server_name).first()
        
        response = await rcon(
            *cmd,
            host=server.ip, port=server.port, passwd=server.password
        )
    
        await bot.send_message(message.from_user.id, f"Ответ от сервера:\n{response}", reply_markup=go_back_keyboard)
