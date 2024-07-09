import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import app.keyboards.main_keyboards as mainkb
from app.commands import set_commands
from app.heandlers.about_us import router as about_us_router
from app.heandlers.admin_profile import router as admin_profile_router
from app.heandlers.register import router as register_router
from app.heandlers.start_and_work import router as start_and_work
from app.heandlers.user_profile import router as user_profile_router
from app.utils.utils import check_registered
from config import TOKEN

bot = Bot(token=TOKEN)  
dp = Dispatcher()

# Cancel
@dp.message(F.text == "Отмена")
async def cancel(message: Message, state: FSMContext):
    """
    Cancels the current state and returns to the main menu.
    """
    await state.clear()
    if await check_registered(message):
        await message.answer("Вы вернулись назад", reply_markup=mainkb.main)
    else:
        await message.answer("Вы вернулись назад", reply_markup=mainkb.start)
    
dp.include_router(register_router)
dp.include_router(start_and_work)
dp.include_router(admin_profile_router)
dp.include_router(user_profile_router)
dp.include_router(about_us_router)


async def main():
    await set_commands(bot)
    print('BOT HAS BEEN STARTED')
    await dp.start_polling(bot, skip_updates=True)
    
if __name__ == '__main__':
    asyncio.run(main())
    