from aiogram import types
from aiogram.dispatcher import filters
from sqlalchemy.orm import Session

from models import engine, UserModel


class AdminFilter(filters.Filter):
    async def check(self, message: types.Message):
        with Session(engine) as session:
            user = session.query(UserModel).filter(UserModel.telegram_id == message.from_user.id).first()
            
            # return user and user.is_admin

            return True
