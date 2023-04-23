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
profile_btn = InlineKeyboardButton("👤 Профиль", callback_data="profile")

main_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(competition_list_btn)
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
    view_new_registrations_btn := InlineKeyboardButton("📢 Уведомить о событии", callback_data="admin_competition_notificate"),
    view_new_registrations_btn := InlineKeyboardButton("👀 Новые заявки", callback_data="admin_view_registrations"),
    view_old_registrations_btn := InlineKeyboardButton("👥 Участники", callback_data="admin_view_participants"),
    edit_name_btn := InlineKeyboardButton("✏️ название", callback_data="admin_competition_edit_name"),
    edit_description_btn := InlineKeyboardButton("✏️ описание", callback_data="admin_competition_edit_description"),
    reschedule_btn := InlineKeyboardButton("🕓 Перенести", callback_data="admin_competition_reschedule"),
    cancel_btn := InlineKeyboardButton("❌ Отменить", callback_data="admin_competition_cancel"),
]
go_back_btn = InlineKeyboardButton("◀️ Назад", callback_data="admin_go_back_competitions")

admin_competition_detail_keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
admin_competition_detail_keyboard.add(admin_competition_btns[0])
admin_competition_detail_keyboard.add(*admin_competition_btns[1:7])
admin_competition_detail_keyboard.add(go_back_btn)


admin_view_registrations_btns = [
    InlineKeyboardButton("✅ Одобрить", callback_data="admin_approve_registration"),
    InlineKeyboardButton("❌ Отклонить", callback_data="admin_reject_registration"),
    InlineKeyboardButton("◀️ Назад", callback_data="admin_next_registration"),
]

admin_view_registrations_keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
admin_view_registrations_keyboard.add(*admin_competition_btns)


admin_notification_bnts = [
    to_all_btn := InlineKeyboardButton(text="Всем", callback_data="notificate_all"),
    to_new_btn := InlineKeyboardButton(text="Новым", callback_data="notificate_registrations"),
    to_members_btn := InlineKeyboardButton(text="Участникам", callback_data="notificate_participants"),
    go_back_btn := InlineKeyboardButton(text="Назад", callback_data="notificate_go_back"),
]

admin_notification_keyboard = InlineKeyboardMarkup(resize_keyboards=True, row_width=3)
admin_notification_keyboard.add(*admin_notification_bnts)
