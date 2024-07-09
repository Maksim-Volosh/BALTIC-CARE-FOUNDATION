from datetime import datetime, timedelta

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import app.keyboards.main_keyboards as mainkb
import app.keyboards.work_keyboards as workkb
import config
from app.database import Database
from app.states import Place, Work
from app.utils.utils import check_registered, validate_place

bot = Bot(token=config.TOKEN)  
router = Router()


# Command /Start
@router.message(CommandStart())
async def start(message: Message):
    """
    The start command is called when the user sends the /start command. It sends a welcome message to the user
    and sends a sticker to the user as well.
    """
    await message.answer(f'Привет, {message.from_user.full_name}!!',
                         reply_markup=mainkb.start)
    await bot.send_sticker(chat_id=message.from_user.id,
                           sticker='CAACAgEAAxkBAAEFe79mRoJIqe0ZvMAkGT4SDX12cQzAjAACCAUAAvE7kER93QbBjZ9VlzUE'
                           )

@router.message(F.text == 'Начать работу')
async def select_place(message: Message, state: FSMContext):
    """
    Selects the place for work.
    
    If the user is registered, the user is sent to the SelectPlace state. Otherwise, the user is sent to the Start state.
    """
    if await check_registered(message):
        await state.set_state(Place.id_place)
        await message.answer('Привет, для начала работы, напиши на какой точке хуяришь. Введи номер места, который тебе дал менеджер!',
                            reply_markup=mainkb.cancel);
    else:
        await message.answer('Вы не зарегестрированы! Для регистрации нажмите "Зарегестрироваться"', 
                             reply_markup=mainkb.start)

# Select place ==> Work started OR Back
@router.message(Place.id_place)
async def place(message: Message, state: FSMContext):
    """
    Handles the selection of a place for work.

    If the user enters a valid place, the state is updated with the selected place and the user is prompted to start working. Otherwise, an error message is sent to the user.
    """
    db = Database(config.DB_NAME)
    place = db.get_place(message.text)
    placeid = message.text
    if validate_place(place, placeid):
        await message.answer(validate_place(place, placeid))
    else:
        await state.update_data(place=place)
        await message.answer(f'Вы выбрали место: {place[1]}\n\nАдрес: {place[2]}\n\nGoogle maps: {place[3]}',
                            reply_markup=workkb.start_work)
        await state.clear()


# Work started ==> End work
@router.callback_query(F.data == 'work_started')
async def back(callback: CallbackQuery, state: FSMContext):
    """
    Set state to worktime_started and update data with current time.
    """
    await state.set_state(Work.worktime_started)
    await state.update_data(worktime_started=datetime.now().strftime('%Y-%m-%d %H:%M'))
    await callback.message.edit_text('Вы начали работу!!!\nНе забудь когда закончишь нажать "Закончить работу". Или если хочешь сделать перерыв нажми "Сделать перерыв"',
                                     reply_markup=workkb.work_started)
    
@router.callback_query(F.data == 'pause_work')
async def pause_work(callback: CallbackQuery, state: FSMContext):
    """
    Set state to pause_time and update data with current time.
    """
    await callback.message.edit_text('Ты взял перерыв, не забудь продолжить или завершить работу!!!', reply_markup=workkb.pause_work)
    data = await state.get_data()
    pause = data.get('pause_time')
    resume = data.get('resume_time')
    total_pause_time = data.get('total_pause_time', timedelta(seconds=0))
    if pause and resume:
        pause_dt = datetime.strptime(pause, '%Y-%m-%d %H:%M')
        resume_dt = datetime.strptime(resume, '%Y-%m-%d %H:%M')
        total_pause_time += resume_dt - pause_dt
    await state.set_state(Work.pause_time)
    await state.update_data(pause_time=datetime.now().strftime('%Y-%m-%d %H:%M'))
    await state.update_data(total_pause_time=total_pause_time)

@router.callback_query(F.data == 'resume_work')
async def resume_work(callback: CallbackQuery, state: FSMContext):
    """
    Set state to resume_time and update data with current time.
    """
    await state.set_state(Work.resume_time)
    await state.update_data(resume_time=datetime.now().strftime('%Y-%m-%d %H:%M'))
    await callback.message.edit_text('Ты продолжил работу, не забудь завершить работу или сделать перерыв!!!', reply_markup=workkb.work_started)
    
@router.callback_query(F.data == 'end_work_sure')
async def end_work_sure(callback: CallbackQuery, state: FSMContext):
    """
    Sure end work?
    """
    await callback.message.edit_text('Ты уверен что хочешь закончить работу? Подтверди свое решение.', reply_markup=workkb.end_work_sure)

@router.callback_query(F.data == 'end_work_no')
async def end_work_no(callback: CallbackQuery, state: FSMContext):
    """
    Set state to worktime_ended and update data with current time.
    """
    await callback.message.edit_text('Работа продолжается, \nНе забудь когда закончишь нажать "Закончить работу". Или если хочешь сделать перерыв нажми "Сделать перерыв"!', reply_markup=workkb.work_started)

# End work ==> Main KB
@router.callback_query(F.data == 'end_work')
async def end_work(callback: CallbackQuery, state: FSMContext):
    """
    Set state to worktime_ended and update data with current time.
    Then set state to collection and send message to user.
    """
    data = await state.get_data()
    total_pause_time = data.get('total_pause_time', timedelta(seconds=0))
    pause = data.get('pause_time')
    resume = data.get('resume_time')
    
    if pause and resume:
        pause_dt = datetime.strptime(pause, '%Y-%m-%d %H:%M')
        resume_dt = datetime.strptime(resume, '%Y-%m-%d %H:%M')
        total_pause_time += resume_dt - pause_dt
    
    await state.set_state(Work.worktime_ended)
    await state.update_data(worktime_ended=datetime.now().strftime('%Y-%m-%d %H:%M'))
    await state.update_data(total_pause_time=total_pause_time)
    await state.set_state(Work.collection)
    await callback.message.answer('Теперь едь на офис и спроси сколько ты заработал, и после отправь мне сколько ты собрал. Например - "100"')

@router.message(Work.collection)
async def collection(message: Message, state: FSMContext):
    """
    Handle user input for collection.
    User should input number without currency sign.
    """
    if not message.text.isdigit():
        await message.answer('Это должно быть целое положительное число, не -100, не 100.22. А например 100')
    else:
        await state.update_data(collection=message.text)
        await message.answer(f'Твой сбор {message.text}, верно??', reply_markup=mainkb.yes_or_no)
        await state.set_state(Work.finish)
        
@router.message(Work.finish)
async def work_finish(message: Message, state: FSMContext):
    """
    Handles the work finish state. Checks if the answer is 'Да' and if so, calculates the total work time and earnings. Stores the work record in the database and sends a message with the total time and earnings.
    """
    if message.text == 'Да':
        await message.answer(f'Ты закончил работу!!!', reply_markup=mainkb.main)
        data = await state.get_data()
        username = message.from_user.username
        starttime = datetime.strptime(data.get('worktime_started'), '%Y-%m-%d %H:%M')
        endtime = datetime.strptime(data.get('worktime_ended'), '%Y-%m-%d %H:%M')
        total_pause_time = data.get('total_pause_time', timedelta(seconds=0))
    
        # Calculate total work time
        total_time_work = endtime - starttime - total_pause_time
        
        collection = int(data.get('collection'))
        earnings = round(collection / 100 * config.PERCENT, 2)
        
        db = Database(config.DB_NAME)
        db.add_work_record(username, str(starttime.strftime('%Y-%m-%d %H:%M')), str(endtime.strftime('%Y-%m-%d %H:%M')), str(total_time_work), collection, earnings)
        
        hours = total_time_work.seconds // 3600
        minutes = (total_time_work.seconds // 60) % 60
        await message.answer(f'Твое общее время работы: {hours} ч. {minutes} мин.\nТвой сбор: {collection}€. \nТы заработал: {earnings}€.')
        await state.clear()
    else:
        await state.set_state(Work.collection)
        await message.answer('Введи снова')
    
# Back
@router.callback_query(F.data == 'back')
async def back(callback: CallbackQuery, state: FSMContext):
    """
    Handles the back callback query. It sends a message and updates the keyboard.
    """
    await state.clear()
    await callback.message.delete()
    if await check_registered(callback):
        await callback.message.answer("Вы вернулись назад", reply_markup=mainkb.main)
    else:
        await callback.message.answer("Вы вернулись назад", reply_markup=mainkb.start)