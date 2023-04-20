from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, ReplyKeyboardRemove
from sqlalchemy.orm import Session

from .admin import *
from .filter import AdminFilter

from models import engine, CompetitionModel, RegistrationModel
from bot import dp, bot, MESSAGES
from states import (
    CompetitionDetailState, AddCompetitionState
)
from keyboards import go_back_keyboard