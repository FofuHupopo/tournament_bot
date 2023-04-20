from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    KeyboardButton, ReplyKeyboardMarkup
)


rules_confirm_btn = InlineKeyboardButton("✍️ Зарегистрироваться", callback_data='signup')

start_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(rules_confirm_btn)


signup_btn = InlineKeyboardButton("✍️ Зарегистрироваться", callback_data="signup")

join_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
join_keyboard.add(signup_btn)


competition_list_btn = InlineKeyboardButton("📋 Список турниров", callback_data="competition_list")
my_registrations_btn = InlineKeyboardButton("📝 Мои заявки", callback_data="my_registrations")
profile_btn = InlineKeyboardButton("👤 Профиль", callback_data="profile")

main_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(competition_list_btn, my_registrations_btn)
main_keyboard.add(profile_btn)


competition_prev_btn = InlineKeyboardButton("<<<", callback_data="competition_prev")
competition_next_btn = InlineKeyboardButton(">>>", callback_data="competition_next")

competition_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
competition_keyboard.row(competition_prev_btn, competition_next_btn)


rcon_btn = InlineKeyboardButton("🖥 RCON", callback_data="admin_rcon")
competition_btn = InlineKeyboardButton("🎮 События", callback_data="admin_competitions")

admin_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
admin_keyboard.add(rcon_btn)
admin_keyboard.add(competition_btn)


add_rcon_btn = InlineKeyboardButton("🖥 Добавить RCON", callback_data="admin_add_rcon")

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


add_competition_btn = InlineKeyboardButton("🎮 Добавить событие", callback_data="admin_add_competition")

admin_competition_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
admin_competition_keyboard.add(add_competition_btn)


admin_competition_btns = [
    view_registrations_btn := InlineKeyboardButton("👀 Посмотреть заявки", callback_data="admin_competition_view_registrations"),
    edit_name_btn := InlineKeyboardButton("✏️ название", callback_data="admin_competition_edit_name"),
    edit_description_btn := InlineKeyboardButton("✏️ описание", callback_data="admin_competition_edit_description"),
    reschedule_btn := InlineKeyboardButton("🕓 Перенести", callback_data="admin_competition_reschedule"),
    cancel_btn := InlineKeyboardButton("❌ Отменить", callback_data="admin_competition_cancel"),
]
go_back_btn = InlineKeyboardButton("◀️ Назад", callback_data="admin_go_back_competitions")

admin_competition_detail_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
admin_competition_detail_keyboard.add(admin_competition_btns[0])
admin_competition_detail_keyboard.add(*admin_competition_btns[1:3])
admin_competition_detail_keyboard.add(*admin_competition_btns[3:])
admin_competition_detail_keyboard.add(go_back_btn)


# a_u_sure_btns = [
#     yes_btn := InlineKeyboardButton("Да", callback_data="yes_sure"),
#     no_btn := InlineKeyboardButton("Нет", callback_data="no_sure"),
# ]

# a_u_sure_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
# a_u_sure_keyboard.add(*a_u_sure_btns)
