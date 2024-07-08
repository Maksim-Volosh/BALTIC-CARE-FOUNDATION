from aiogram.types import Message
from app.database import Database
import config 

async def check_registered(message: Message):
    db = Database(config.DB_NAME)
    users = db.get_user(message.from_user.username)
    if await is_admin(message):
        return True
    if not (users):
        return False
    else:
       return True

async def is_admin(message: Message):
    return message.from_user.username == config.ADMIN_USERNAME

def paginate_users(users, page, per_page=config.DEF_PAGINATE):
    start = (page - 1) * per_page
    end = start + per_page
    return users[start:end]

def validate_place(place, placeid):
    if not str(placeid).isdigit():
        return 'Номер должен быть цифрой, и целым положительным числом! Попробуйте ещё раз.'
    if int(placeid) <= 0:
        return 'Номер должен быть цифрой, и целым положительным числом! Попробуйте ещё раз.'
    if not place:
        return 'Такого места нет! Уточните номер места и попробуйте ещё раз.'
    return None