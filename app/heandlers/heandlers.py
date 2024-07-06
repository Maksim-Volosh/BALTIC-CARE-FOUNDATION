from datetime import datetime
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.states import Place, Register, Work
from aiogram import Bot
from app.database import Database
import app.keyboards.main_keyboards as mainkb
import app.keyboards.work_keyboards as workkb
from app.utils.utils import check_registered, is_admin
import config 
from ..places import places
import re

bot = Bot(token=config.TOKEN)  
router = Router()


# Command /Start
@router.message(CommandStart())
async def start(message: Message):
    await message.answer(f'Привет, {message.from_user.full_name}!!',
                         reply_markup=mainkb.start)
    await bot.send_sticker(chat_id=message.from_user.id,
                           sticker='CAACAgEAAxkBAAEFe79mRoJIqe0ZvMAkGT4SDX12cQzAjAACCAUAAvE7kER93QbBjZ9VlzUE'
                           )
# Cancel
@router.message(F.text == "Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    if await check_registered(message):
        await message.answer("Вы вернулись назад", reply_markup=mainkb.main)
    else:
        await message.answer("Вы вернулись назад", reply_markup=mainkb.start)

# Register
@router.message(F.text == "Зарегестрироваться")
async def start_register(message: Message, state: FSMContext):
    if not await check_registered(message):  
        username = message.from_user.username
        if not username:
            await message.answer('Для начала тебе нужно создать username у себя в профиле!!',
                                 reply_markup=mainkb.start)
        else:
            await message.answer('Привет, давай познакомимся. Как тебя зовут? \n\nВведи имя и фамилию как в паспорте, английскими буквами!',
                                reply_markup=mainkb.cancel)
            await state.set_state(Register.RegFullName)
    else:
        if await is_admin(message):
            await message.answer('Вы администратор', reply_markup=mainkb.main)
        
        else: await message.answer('Вы уже зарегестрированы!',
                             reply_markup=mainkb.main)

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
    await message.answer(f'Ваша дата рождения {message.text}, все данные верны?', reply_markup=mainkb.yes_or_no)
    await state.update_data(regdate=message.text)
    await state.set_state(Register.RegFinish)

@router.message(Register.RegFinish)
async def register_finish(message: Message, state: FSMContext):
    if message.text == 'Да':
        reg_data = await state.get_data()    
    
        reg_fullname = reg_data.get('regfullname')
        reg_phonenumber = reg_data.get('regphonenumber')
        reg_date = reg_data.get('regdate')
        
        db = Database(config.DB_NAME)
            
        db.add_user(reg_fullname, reg_phonenumber, reg_date, message.from_user.username)

        await message.answer('Регистрация прошла успешно! Теперь вы можете начать работу! \n\nДля этого обратитесь к своему менеджеру, возьмите инвентарь и спросите номер места для работ! \n\nПосле, нажимайте - "Начать работу"!',
                            reply_markup=mainkb.main)
        await state.clear()
    else:
        await message.answer('Вы вернулись назад', reply_markup=mainkb.start)
        await state.clear()

@router.message(F.text == 'Начать работу')
async def select_place(message: Message, state: FSMContext):
    if await check_registered(message):
        await state.set_state(Place.id_place)
        await message.answer('Привет, для начала работы, напиши на какой точке хуяришь. Введи номер места, который тебе дал владос!',
                            reply_markup=mainkb.cancel);
    else:
        await message.answer('Вы не зарегестрированы! Для регистрации нажмите "Зарегестрироваться"', 
                             reply_markup=mainkb.start)

# Select place ==> Work started OR Back
@router.message(Place.id_place)
async def place(message: Message, state: FSMContext):
    if message.text not in places:
        await message.answer('Такого места нет!')
        return
    await state.update_data(id_place=message.text)
    data = await state.get_data()
    await message.answer(f'Вы выбрали место: {places[data["id_place"]][0]}\n\nАдрес: {places[data["id_place"]][1]}\n\nGoogle maps: {places[data["id_place"]][2]}',
                         reply_markup=workkb.start_work)
    await state.clear()


# Work started ==> End work
@router.callback_query(F.data == 'work_started')
async def back(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Work.worktime_started)
    await state.update_data(worktime_started=datetime.now().strftime('%Y-%m-%d %H:%M'))
    print("Начало работы: ", datetime.now().strftime('%Y-%m-%d %H:%M'))
    await callback.answer('Вы начали работу')
    await callback.message.edit_text('Вы начали работу!!!\nНе забудь когда закончишь нажать "закончил". Или если перерыв нажми "перерыв"',
                                     reply_markup=workkb.work_started)

# End work ==> Main KB
@router.callback_query(F.data == 'end_work')
async def end_work(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Work.worktime_ended)
    await state.update_data(worktime_ended=datetime.now().strftime('%Y-%m-%d %H:%M'))
    print("Завершение работы: ", datetime.now().strftime('%Y-%m-%d %H:%M'))
    await state.set_state(Work.collection)
    await callback.message.answer('Теперь едь на офис и спроси сколько ты заработал, и после отправь мне сколько ты собрал. Например - "100"')
    
@router.callback_query(F.data == 'pause_work')
async def pause_work(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Work.pause_time)
    await state.update_data(pause_time=datetime.now().strftime('%Y-%m-%d %H:%M'))
    print("Пауза работы: ", datetime.now().strftime('%Y-%m-%d %H:%M'))
    await callback.message.edit_text('Ты взял перерыв, не забудь продолжить или завершить работу!!!', reply_markup=workkb.pause_work)

@router.callback_query(F.data == 'resume_work')
async def resume_work(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Work.resume_time)
    await state.update_data(resume_time=datetime.now().strftime('%Y-%m-%d %H:%M'))
    print("Продолжение работы: ", datetime.now().strftime('%Y-%m-%d %H:%M'))
    await callback.message.edit_text('Ты продолжил работу, не забудь продолжить или завершить работу!!!', reply_markup=workkb.work_started)


@router.message(Work.collection)
async def collection(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Это должно быть целое положительное число, не -100, не 100.22. А например 100')
    else:
        await state.update_data(collection=message.text)
        await message.answer(f'Твой сбор {message.text}, верно??', reply_markup=mainkb.yes_or_no)
        await state.set_state(Work.finish)
        
@router.message(Work.finish)
async def work_finish(message: Message, state: FSMContext):
    if message.text == 'Да':
        data = await state.get_data()
        username = message.from_user.username
        starttime = data.get('worktime_started')
        endtime = data.get('worktime_ended')
        pause_worktime = data.get('pause_time')
        resume_worktime = data.get('resume_time')
        total_pause_time = None
        if pause_worktime:
            if resume_worktime:
                total_pause_time = datetime.strptime(resume_worktime, '%Y-%m-%d %H:%M') - datetime.strptime(pause_worktime, '%Y-%m-%d %H:%M')
                print("total_pause_time", total_pause_time)
                total_time_work = datetime.strptime(endtime, '%Y-%m-%d %H:%M') - datetime.strptime(starttime, '%Y-%m-%d %H:%M') - total_pause_time
                print("total_time_work if resume true", total_time_work)
            else:
                total_time_work = datetime.strptime(pause_worktime, '%Y-%m-%d %H:%M') - datetime.strptime(starttime, '%Y-%m-%d %H:%M')
                print("total_time_work if resume false", total_time_work)
        else:
            total_time_work = datetime.strptime(endtime, '%Y-%m-%d %H:%M') - datetime.strptime(starttime, '%Y-%m-%d %H:%M')
            print("total_time_work if pause has been false", total_time_work)
        collection = int(data.get('collection'))
        earnings = collection / 100 * 20    
        
        await message.answer(f'Ты закончил работу!!!', reply_markup=mainkb.main)
        
        db = Database(config.DB_NAME)
        db.add_work_record(username, str(starttime), str(endtime), str(total_time_work), collection, earnings)
        
        
        hours = total_time_work.seconds // 3600
        minutes = (total_time_work.seconds // 60) % 60
        await message.answer(f'Твое общее время работы: {hours} ч. {minutes} мин.\nТвой сбор: {collection}€. \nТы заработал: {earnings}€.')
        await state.clear()
    else:
        await state.set_state(Work.collection)
        await message.answer('Введи снова')
    
# About us
@router.message(F.text == 'О нас')
async def about_us(message: Message):
    if await check_registered(message):
        await message.answer('Информация о нас', reply_markup=mainkb.main)
    else:
        await message.answer('Информация о нас', reply_markup=mainkb.start)
    
    
# Back
@router.callback_query(F.data == 'back')
async def back(callback: CallbackQuery):
    await callback.answer('Вы вернулись назад')
    await callback.message.answer('Вы вернулись назад', reply_markup=mainkb.main)