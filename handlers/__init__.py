from .join_handlers import *
from .main_handlers import *
from .competiotion_handlers import *
from .admin import *


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