from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    KeyboardButton, ReplyKeyboardMarkup
)


rules_confirm_btn = InlineKeyboardButton("Я ознакомился с правилами", callback_data='confirm_rules')

start_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(rules_confirm_btn)


join_btn = InlineKeyboardButton("Участвовать в турнире", callback_data="join")

join_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
join_keyboard.add(join_btn)


competition_list_btn = InlineKeyboardButton("Список турниров", callback_data="competition_list")
registered_btn = InlineKeyboardButton("Мои турниры", callback_data="registered")

main_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(competition_list_btn)
main_keyboard.add(registered_btn)


competition_prev_btn = InlineKeyboardButton("<<<", callback_data="competition_prev")
competition_next_btn = InlineKeyboardButton(">>>", callback_data="competition_next")

competition_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
competition_keyboard.row(competition_prev_btn, competition_next_btn)


rcon_btn = InlineKeyboardButton("RCON", callback_data="admin_rcon")
competition_btn = InlineKeyboardButton("События", callback_data="admin_competitions")

admin_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
admin_keyboard.add(rcon_btn)
admin_keyboard.add(competition_btn)


add_rcon_btn = InlineKeyboardButton("Добавить RCON", callback_data="admin_add_rcon")

rcon_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
rcon_keyboard.add(add_rcon_btn)


go_back_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Выйти")
        ]
    ],
    resize_keyboard=True
)


add_competition_btn = InlineKeyboardButton("Добавить событие", callback_data="admin_add_competition")

competition_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
competition_keyboard.add(add_competition_btn)