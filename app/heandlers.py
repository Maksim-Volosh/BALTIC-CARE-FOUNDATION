from datetime import datetime
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.states import Place, Register
from aiogram import Bot
from app.database import Database
import app.keyboards as kb
import config 
from .places import places
import re

bot = Bot(token=config.TOKEN)  
router = Router()
 

# Command /Start
@router.message(CommandStart())
async def start(message: Message):
    await message.answer(f'Привет, {message.from_user.full_name}!!',
                         reply_markup=kb.start)
    await bot.send_sticker(chat_id=message.from_user.id,
                           sticker='CAACAgEAAxkBAAEFe79mRoJIqe0ZvMAkGT4SDX12cQzAjAACCAUAAvE7kER93QbBjZ9VlzUE'
                           )


# Register
@router.message(F.text == "Зарегестрироваться")
async def start_register(message: Message, state: FSMContext):
    db = Database(config.DB_NAME)
    users = db.get_user(message.from_user.username)
    if not (users):  
        await message.answer('Привет, давай познакомимся. Как тебя зовут? \n\nВведи имя и фамилию как в паспорте, английскими буквами!')
        await state.set_state(Register.RegFullName)
    else:
        await message.answer('Вы уже зарегестрированы!',
                             reply_markup=kb.main)

@router.message(Register.RegFullName)
async def register_fullname(message: Message, state: FSMContext):
    await message.answer(f'Приятно познакомиться {message.text} \n'
                         f'Теперь напишете свой номер телефона! \n'
                         f'Формат: +370XXXXXXXX')
    await state.update_data(regfullname=message.text)
    await state.set_state(Register.RegPhoneNumber)
    
@router.message(Register.RegPhoneNumber)
async def register_phone(message: Message, state: FSMContext):
    if(re.findall(r"\+370\d{8}", message.text)):
        await message.answer(f'Ваш номер {message.text} \n'
                             f'Теперь напишите свою дату рождения! \n'
                             f'Формат: дд.мм.гггг.')
        await state.update_data(regphonenumber=message.text)
        await state.set_state(Register.RegDate)
    else:
        await message.answer('Номер указан в неправильном формате!')

@router.message(Register.RegDate)
async def register_date(message: Message, state: FSMContext):
    await message.answer(f'Ваша дата рождения {message.text}')
    await state.update_data(regdate=message.text)
    reg_data = await state.get_data()    
    
    reg_fullname = reg_data.get('regfullname')
    reg_phonenumber = reg_data.get('regphonenumber')
    reg_date = reg_data.get('regdate')
    print(reg_fullname, reg_phonenumber, reg_date)
    
    db = Database(config.DB_NAME)
    db.add_user(reg_fullname, reg_phonenumber, reg_date, message.from_user.username)

    await message.answer('Регистрация прошла успешно! Теперь вы можете начать работу! \n\nДля этого обратитесь к своему менеджеру, возьмите инвентарь и спросите номер места для работ! \n\nПосле, нажимайте - "Начать работу"!',
                         reply_markup=kb.main)
    await state.clear()

        


# Start work ==> Select place
@router.message(F.text == 'Начать работу')
async def select_place(message: Message, state: FSMContext):
    await state.set_state(Place.id_place)
    await message.answer('Привет, для начала работы, напиши на какой точке хуяришь. Введи номер места, который тебе дал владос!',
                         reply_markup=None);

# Select place ==> Work started OR Back
@router.message(Place.id_place)
async def place(message: Message, state: FSMContext):
    if message.text not in places:
        await message.answer('Такого места нет!')
        return
    await state.update_data(id_place=message.text)
    data = await state.get_data()
    await message.answer(f'Вы выбрали место: {places[data["id_place"]][0]}\n\nАдрес: {places[data["id_place"]][1]}\n\nGoogle maps: {places[data["id_place"]][2]}',
                         reply_markup=kb.start_work)
    await state.clear()


# Work started ==> End work
@router.callback_query(F.data == 'work_started')
async def back(callback: CallbackQuery):
    await callback.answer('Вы начали работу')
    print(f"Время начала работы: {datetime.now().strftime('%m-%d %H:%M')}")
    await callback.message.edit_text('Вы начали работу!!!\nНе забудь когда закончишь нажать "закончил". Или если перерыв нажми "перерыв"',
                                     reply_markup=kb.work_started)

# End work ==> Main KB
@router.callback_query(F.data == 'end_work')
async def end_work(callback: CallbackQuery):
    await callback.answer('Ты закончил работу')
    print(f"Время окончания работы: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    await callback.message.answer('Ты закончил работу!!! ОТЛИЧНО ПОРАБОТАЛ!!!', reply_markup=kb.main)
    

# About us
@router.message(F.text == 'О нас')
async def about_us(message: Message):
    await message.answer('Информация о нас', reply_markup=kb.main)
    
    
# Back
@router.callback_query(F.data == 'back')
async def back(callback: CallbackQuery):
    await callback.answer('Вы вернулись назад')
    await callback.message.answer('Вы вернулись назад', reply_markup=kb.main)