import asyncio

from aiogram import Bot, Dispatcher
from app.heandlers import router

from config import TOKEN

bot = Bot(token=TOKEN)  
dp = Dispatcher()
    

print('BOT HAS BEEN STARTED')


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)
    
    
if __name__ == '__main__':
    asyncio.run(main())
    