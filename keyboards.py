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


competition_list_btn = InlineKeyboardButton("📋 Список событий", callback_data="competition_list")
my_registrations_btn = InlineKeyboardButton("🎮 Мои заявки", callback_data="my_registrations")
profile_btn = InlineKeyboardButton("👤 Профиль", callback_data="profile")
ask_quetion_btn = InlineKeyboardButton("🗣 Задать вопрос", callback_data="ask_question")

main_keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
main_keyboard.add(competition_list_btn, my_registrations_btn)
main_keyboard.add(profile_btn)
main_keyboard.add(ask_quetion_btn)


ask_question_keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
ask_question_keyboard.add(*[
    InlineKeyboardButton("🗣 Спросить", callback_data="ask"),
    InlineKeyboardButton("📝 Мои вопросы", callback_data="answers"),
    InlineKeyboardButton("◀️ Назад", callback_data="menu"),
])


admin_question_keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
admin_question_keyboard.add(*[
    InlineKeyboardButton("💌 Новые", callback_data="admin_view_questions"),
    InlineKeyboardButton("📝 Отвеченные", callback_data="admin_answered_questions"),
    InlineKeyboardButton("◀️ Назад", callback_data="admin")
])


profile_keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
profile_keyboard.add(*[
    InlineKeyboardButton("◀️ Назад", callback_data="menu")
])


my_registration_keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
my_registration_keyboard.add(*[
    InlineKeyboardButton("✍️ Поданные", callback_data="submitted_registrations"),
    InlineKeyboardButton("✅ Одобренные", callback_data="approved_registrations"),
    InlineKeyboardButton("◀️ Назад", callback_data="menu")
])


competition_prev_btn = InlineKeyboardButton("<<<", callback_data="competition_prev")
competition_next_btn = InlineKeyboardButton(">>>", callback_data="competition_next")

competition_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
competition_keyboard.row(competition_prev_btn, competition_next_btn)


rcon_btn = InlineKeyboardButton("🖥 RCON", callback_data="admin_rcon")
competition_btn = InlineKeyboardButton("🎮 События", callback_data="admin_competitions")
questions_btn = InlineKeyboardButton("❔ Вопросы", callback_data="admin_questions")
load_meme_btn = InlineKeyboardButton("🖼 Загрузить мем", callback_data="admin_load_meme")

admin_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
admin_keyboard.add(rcon_btn)
admin_keyboard.add(competition_btn)
admin_keyboard.add(questions_btn)
admin_keyboard.add(load_meme_btn)


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
