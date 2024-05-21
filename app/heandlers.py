from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import Bot

from config import TOKEN

import app.keyboards as kb

places = {
    '1': 'Lidl office',
    '2': 'Lidl 2',
    '3': 'Lidl 3',
    '4': 'Lidl 4',
    '5': 'Lidl 5',
}

bot = Bot(token=TOKEN)  

router = Router()


class Place(StatesGroup):
    id_place = State()
    

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(f'Привет, {message.from_user.full_name}, готов к работе?!',
                         reply_markup=kb.main)
    await bot.send_sticker(chat_id=message.from_user.id, sticker='CAACAgEAAxkBAAEFe79mRoJIqe0ZvMAkGT4SDX12cQzAjAACCAUAAvE7kER93QbBjZ9VlzUE')

    
  
@router.message(Command('place'))
@router.message(F.text == 'Начать работу')
async def select_place(message: Message, state: FSMContext):
    await state.set_state(Place.id_place)
    await message.answer('Привет, для начала работы, напиши на какой точке хуяришь. Введи номер места, который тебе дал владос!',
                         reply_markup=None);

    
@router.message(Place.id_place)
async def place(message: Message, state: FSMContext):
    if message.text not in places:
        await message.answer('Такого места нет!')
        return
    await state.update_data(id_place=message.text)
    data = await state.get_data()
    await message.answer(f'Вы выбрали место: {places[data["id_place"]]}', reply_markup=kb.start_work)
    await state.clear()
    

@router.callback_query(F.data == 'back')
async def back(callback: CallbackQuery):
    await callback.answer('Вы вернулись назад')
    await callback.message.answer('Вы вернулись назад', reply_markup=kb.main)
    

