from .main_handlers import *
from .user_competition_handlers import *
from .signup_handler import *
from .admin import *
from  .profile_handlers import *


@dp.message_handler()
async def unregistered_message(message: types.Message):
    if not message.text:
        return

    with Session(engine) as session:
        message = UnregisteredMessageModel(
            telegram_id=message.chat.id,
            message=message.text
        )
        
        session.add(message)
        session.commit()
