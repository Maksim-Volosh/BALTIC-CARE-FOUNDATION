import asyncio

from aiogram import Bot, Dispatcher
from app.heandlers import router
from app.commands import set_commands

from config import TOKEN

bot = Bot(token=TOKEN)  
dp = Dispatcher()
    

print('BOT HAS BEEN STARTED')


async def main():
    await set_commands(bot)
    dp.include_router(router)
    await dp.start_polling(bot, skip_updates=True)
    
    
if __name__ == '__main__':
    asyncio.run(main())
    