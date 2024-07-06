import asyncio

from aiogram import Bot, Dispatcher
from app.heandlers.heandlers import router
from app.heandlers.profile import router as profile_router
from app.commands import set_commands

from config import TOKEN

bot = Bot(token=TOKEN)  
dp = Dispatcher()
    
dp.include_router(router)
dp.include_router(profile_router)


async def main():
    await set_commands(bot)
    print('BOT HAS BEEN STARTED')
    await dp.start_polling(bot, skip_updates=False)
    
    
    
if __name__ == '__main__':
    asyncio.run(main())
    