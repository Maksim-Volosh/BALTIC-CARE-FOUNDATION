import calendar
from datetime import datetime, timedelta
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.heandlers.heandlers import is_admin
from app.states import AddPlace, AdminPlace, ChoiceUser, Place
from aiogram import Bot
from app.database import Database
import app.keyboards.main_keyboards as mainkb
import app.keyboards.profile_keyboards as prkb
from app.utils.utils import check_registered, paginate_users, validate_place
import config 
import re

bot = Bot(token=config.TOKEN)  
router = Router()

@router.message(F.text == 'Профиль')
async def profile(message: Message):
    """
    Show user profile.
    """
    if await is_admin(message):
        await admin_profile(message)
    else:
        await user_profile(message)

async def admin_profile(message: Message):
    """
    Show admin profile.
    """
    await message.answer('Добро пожаловать в профиль админа!!! \n\nЧто вы хотите сделать?', reply_markup=prkb.admin_profile)

"""========= USERS ========="""

@router.callback_query(F.data == 'all_users')
async def all_users(callback: CallbackQuery, state: FSMContext):
    """
    Show all users in admin profile.
    """
    await state.set_state(ChoiceUser.username)
    await state.update_data(page=1)
    await show_users(callback, state)

@router.callback_query(F.data.startswith('page_'))
async def show_users(callback: CallbackQuery, state: FSMContext):
    """
    Show all users in admin profile.
    """
    data = await state.get_data()
    page = int(callback.data.split('_')[1]) if 'page_' in callback.data else data.get('page', 1)
    await state.update_data(page=page)
    
    db = Database(config.DB_NAME)
    users = db.all_users()
    paginated_users = paginate_users(users, page)
    
    if paginated_users:
        if page <= 1: page_text = ''
        else: page_text = f' (Страница {page})'
        users_text = '\n'.join([f'{i[0]}. {i[1]} - @{i[4]}' for i in paginated_users])
        await callback.message.edit_text(f'Все пользователи{page_text}:\n\n{users_text}\n\nНапиши username пользователя для взаимодействия с ним', reply_markup=prkb.get_pagination_markup(page, len(users)))
    else:
        await callback.message.edit_text('Пользователи отсутствуют.', reply_markup=prkb.get_pagination_markup(page, len(users)))
    
@router.message(ChoiceUser.username)
async def choice_user_state(message: Message, state: FSMContext):
    """
    Show information about chosen user.
    """
    db = Database(config.DB_NAME)
    username = message.text[1:] if message.text.startswith('@') else message.text
    user = db.get_user(username)
    if user:
        await state.update_data(username=username)
        await message.answer(f'Пользователь: @{username}\n\n'
                             f'Полное имя: {user[1]} \n\n'
                             f'Номер: {user[2]} \n\n'
                             f'Дата рождения: {user[3]}', reply_markup=prkb.admin_users_user)
    else:
        await message.answer('Такого пользователя нет', reply_markup=prkb.admin_profile_users)
    
@router.callback_query(F.data == 'get_user_stats')
async def get_user_stats(callback: CallbackQuery, state: FSMContext):
    """
    Get user stats.
    """
    data = await state.get_data()
    username = data.get('username')
    db = Database(config.DB_NAME)
    user = db.get_user(username)
    if user:
        stats = db.get_work_records(username)
        total_collection = sum([int(record[5]) for record in stats])
        total_earnings = sum([int(record[6]) for record in stats])
        
        total_time_worked = timedelta()
        for record in stats:
            time_str = record[4]  # Предполагается, что это строка в формате 'HH:MM:SS'
            hours, minutes, seconds = map(int, time_str.split(':'))
            total_time_worked += timedelta(hours=hours, minutes=minutes, seconds=seconds)
        total_hours = round(total_time_worked.total_seconds() // 3600)
        total_minutes = round((total_time_worked.total_seconds() % 3600) // 60)
            
        if stats:
            best_day = db.best_day_collection(username)
            best_day_date = datetime.strptime(best_day[2], '%Y-%m-%d %H:%M').date()
            best_day_from = datetime.strptime(best_day[2], '%Y-%m-%d %H:%M').strftime('%H:%M')
            best_day_to = datetime.strptime(best_day[3], '%Y-%m-%d %H:%M').strftime('%H:%M')
            best_day_total_time = datetime.strptime(best_day[4], '%H:%M:%S').time()
            best_day_hours, best_day_minutes = best_day_total_time.hour, best_day_total_time.minute
            
            worse_day = db.worse_day_collection(username)
            worse_day_date = datetime.strptime(worse_day[2], '%Y-%m-%d %H:%M').date()
            worse_day_from = datetime.strptime(worse_day[2], '%Y-%m-%d %H:%M').strftime('%H:%M')
            worse_day_to = datetime.strptime(worse_day[3], '%Y-%m-%d %H:%M').strftime('%H:%M')
            worse_day_total_time = datetime.strptime(worse_day[4], '%H:%M:%S').time()
            worse_day_hours, worse_day_minutes = worse_day_total_time.hour, worse_day_total_time.minute
            
            max_earnings = max([int(record[6]) for record in stats])
            max_collection = max([int(record[5]) for record in stats])
            await callback.message.edit_text(f'Статистика пользователя: @{username}\n\n'
                                             f'Всего выходов: {len(stats)} \n'
                                             f'Всего собрано: {total_collection}€ \n'
                                             f'Всего заработано: {total_earnings}€ \n'
                                             f'Всего проработано: {total_hours}ч {total_minutes}м \n\n'
                                             f'Больше всего собрано за день: {max_collection}€ \n'
                                             f'Больше всего заработано за день: {max_earnings}€ \n\n'
                                             f'🎉 Лучший рабочий день: {best_day_date} \n\n'
                                             f'Часы работы лучшего дня: {best_day_from} - {best_day_to} \n'
                                             f'Общее время работы лучшего дня: {best_day_hours}ч {best_day_minutes}м \n'
                                             f'Общий сбор лучшего дня: {best_day[5]}€\n'
                                             f'Общий заработок лучшего дня: {best_day[6]}€\n\n'
                                             f'😭 Худший рабочий день: {worse_day_date} \n\n'
                                             f'Часы работы худшего дня: {worse_day_from} - {worse_day_to} \n'
                                             f'Общее время работы худшего дня: {worse_day_hours}ч {worse_day_minutes}м \n'
                                             f'Общий сбор худшего дня: {worse_day[5]}€\n'
                                             f'Общий заработок худшего дня: {worse_day[6]}€',
                                             reply_markup=prkb.admin_users_user_stats)
        else:
            await callback.message.edit_text(f'Статистика пользователя: {username}\n\n'
                                             f'Ничего не найдено', reply_markup=prkb.admin_users_user_stats)
    else:
        await callback.message.edit_text('Пользователь не выбран!!', reply_markup=prkb.admin_profile_users)

@router.callback_query(F.data == 'delete_user')
async def delete_user(callback: CallbackQuery, state: FSMContext):
    """
    Delete user.
    """
    data = await state.get_data()
    username = data.get('username')
    await callback.message.edit_text(f'Удалить пользователя @{username}?', reply_markup=prkb.admin_delete_user)
    
@router.callback_query(F.data == 'delete_user_yes')
async def delete_yes(callback: CallbackQuery, state: FSMContext):
    """
    Delete user and his stats.
    """
    data = await state.get_data()
    username = data.get('username')
    db = Database(config.DB_NAME)
    db.delete_user(username)
    await callback.message.edit_text('Пользователь удален, удалить его статистику?', reply_markup=prkb.admin_delete_stats)
    
@router.callback_query(F.data == 'delete_user_stats')
async def delete_user_stats(callback: CallbackQuery, state: FSMContext):
    """
    Delete user stats.
    """
    data = await state.get_data()
    username = data.get('username')
    await callback.message.edit_text(f'Удалить статистику для пользователя @{username}?', reply_markup=prkb.admin_delete_stats)
    
    
@router.callback_query(F.data == 'delete_stats_yes')
async def delete_yes(callback: CallbackQuery, state: FSMContext):
    """
    Nolification for Delete user stats.
    """
    data = await state.get_data()
    username = data.get('username')
    db = Database(config.DB_NAME)
    db.delete_user_stats(username)
    await state.clear()
    await callback.message.edit_text('Статистика @{username} удалена!')
    await callback.message.answer('Добро пожаловать в профиль админа!!! \n\nЧто вы хотите сделать?', reply_markup=prkb.admin_profile)

"""========= STATS ========="""

@router.callback_query(F.data == 'stats')
async def stats(callback: CallbackQuery):
    """
    Admin stats.
    """
    db = Database(config.DB_NAME)
    count_work_records_current_month = db.count_work_records_current_month()
    if count_work_records_current_month > 0:    
        total_collection_current_month = db.total_collection_current_month()
        count_work_hours = db.count_work_hours_current_month()  
        best_user_hours_current_month = db.best_user_hours_current_month()
        best_user_collection_current_month = db.best_user_collection_current_month()
        best_user_by_collection_current_month = db.best_user_by_collection_current_month()
        current_mounth = datetime.now().strftime('%B').capitalize()
        await callback.message.edit_text(
            f'Статистика за {current_mounth}: {total_collection_current_month}€\n'
            f'Всего собрано: {total_collection_current_month}€\n'
            f'Всего выходов: {count_work_records_current_month}\n'
            f'Всего часов работы : {count_work_hours}\n\n'
            f'Больше всех часов работы за день у: @{best_user_hours_current_month[0]}\n'
            f'    Проработал(а): {best_user_hours_current_month[1]}\n\n'
            f'Больше всех сбор за день у: @{best_user_collection_current_month[0]}\n'
            f'    Дата время начала: {best_user_collection_current_month[1]}\n'
            f'    Работал(а): {best_user_collection_current_month[2]}\n'
            f'    Сбор: {best_user_collection_current_month[3]}€\n\n'
            f'Больше всех общий сбор за месяц у: @{best_user_by_collection_current_month[0]}\n'
            f'    Сбор: {best_user_by_collection_current_month[1]}€\n\n',
            reply_markup=prkb.pback)
    else:
        await callback.message.edit_text('Нет данных за текущий месяц', reply_markup=prkb.pback)

@router.callback_query(F.data == 'pback')
async def back(callback: CallbackQuery, state: FSMContext):
    """
    Back to admin or user profile menu.
    """
    await state.clear()
    if await is_admin(callback):
       await callback.message.edit_text('Добро пожаловать в профиль админа!!! \n\nЧто вы хотите сделать?', reply_markup=prkb.admin_profile)
    else:
        await callback.message.edit_text('Добро пожаловать в ваш профиль!!! \n\nЧто вы хотите сделать?', reply_markup=prkb.user_profile)

"""========= PLACE ========="""

@router.callback_query(F.data == 'places')
async def places(callback: CallbackQuery, state: FSMContext):
    """
    Show places.
    """
    db = Database(config.DB_NAME)
    places = db.all_places()
    await state.set_state(AdminPlace.id_place)
    message_text = 'Все точки:\n'
    if places:
        message_text += f'\n'
        for place in places:
            message_text += f"{place[0]}. - {place[1]} - <a href=\"{place[3]}\">{place[2]}</a>\n"
        message_text += '\nНапишите номер точки если хотите взаимодействовать с ней'
    else:
        message_text += 'Точки отсутствуют. Добавьте новую точку!'
        
    
    await callback.message.edit_text(message_text, parse_mode="HTML", reply_markup=prkb.admin_all_places)

@router.message(AdminPlace.id_place)
async def choice_place(message: Message, state: FSMContext):
    """
    Show information about chosen place.
    """
    db = Database(config.DB_NAME)
    place_id = message.text
    place = db.get_place(place_id)
    validate = validate_place(place, place_id)
    if validate:
        await message.answer(validate)
    else:
        await state.update_data(place_id=place_id)
        await message.answer(f'Точка: {place[1]}\n\n'
                            f'Адрес: {place[2]}\n\n'
                            f'Google maps: {place[3]}\n\n',
                            reply_markup=prkb.admin_place
                            )
        
@router.callback_query(F.data == 'delete_place')
async def delete_place(callback: CallbackQuery, state: FSMContext):
    """
    Delete place????.
    """
    await callback.message.edit_text('Вы уверены, что хотите удалить эту точку?', reply_markup=prkb.admin_delete_place)


@router.callback_query(F.data == 'delete_place_yes')
async def delete_place_yes(callback: CallbackQuery, state: FSMContext):
    """
    Delete place yes.
    """
    state_data = await state.get_data()
    place_id = state_data.get('place_id')
    db = Database(config.DB_NAME)
    db.delete_place(place_id)
    await callback.message.edit_text(f'Точка {place_id} была удалена', reply_markup=prkb.pback)
    await callback.answer()
    await state.clear()
    
@router.callback_query(F.data == 'add_place')
async def add_place_info(callback: CallbackQuery, state: FSMContext):
    """
    Add place info.
    """
    await state.set_state(AddPlace.id_place)
    await callback.message.edit_text(
        f'Чтобы добавить точку тебе нужно отправить сообщение вида:\n\n'
        f'name|adress|google_maps_link\n\n'
        f'Например: \nLidl|Žemaitės g. 16, 03201 Vilnius|https://www.google.com/',
        reply_markup=prkb.pback
    )

@router.message(AddPlace.id_place)
async def add_place(message: Message, state: FSMContext):
    """
    Add place.
    """
    place_data = message.text
    place = place_data.split('|')
    if len(place) != 3:
        await message.answer('Неверный формат сообщения. Попробуйте ещё раз!', reply_markup=prkb.pback)
    else:
        await state.update_data(place=place)
        await message.answer(
            f'Название точки: {place[0]}\n\n'
            f'Адрес: {place[1]}\n\n'
            f'Google maps: {place[2]}\n\n'
            f'Верно???', 
            reply_markup=prkb.admin_add_place
        )

@router.callback_query(F.data == 'add_place_yes')
async def add_place_yes(callback: CallbackQuery, state: FSMContext):
    """
    Add place yes.
    """
    state_data = await state.get_data()
    place = state_data.get('place')
    if place:
        db = Database(config.DB_NAME)
        db.add_place(place[0], place[1], place[2])
        await callback.message.edit_text('Точка была добавлена', reply_markup=prkb.admin_place_added)
    else:
        await callback.message.edit_text('Ошибка при добавлении точки', reply_markup=prkb.admin_place_added)
    await callback.answer()
    await state.clear()

@router.callback_query(F.data == 'add_place_no')
async def add_place_no(callback: CallbackQuery, state: FSMContext):
    """
    Add place no.
    """
    await add_place_info(callback, state)

    
"""========= USER PROFILE ========="""

async def user_profile(message: Message):
    """
    Show user profile.
    """
    if await check_registered(message):
        await message.answer('Добро пожаловать в ваш профиль!!! \n\nЧто вы хотите сделать?', reply_markup=prkb.user_profile)
    else:
        await message.answer('Вы не зарегестрированы! Для регистрации нажмите "Зарегестрироваться"', 
                             reply_markup=mainkb.start)
    
@router.callback_query(F.data == 'user_stats')
async def user_stats(callback: CallbackQuery):
    db = Database(config.DB_NAME)
    username = callback.from_user.username
    if username:
        stats = db.get_work_records(username)
            
        if stats:
            total_collection = sum([int(record[5]) for record in stats])
            total_earnings = sum([float(record[6]) for record in stats])
            
            total_time_worked = timedelta()
            for record in stats:
                time_str = record[4]  # Предполагается, что это строка в формате 'HH:MM:SS'
                hours, minutes, seconds = map(int, time_str.split(':'))
                total_time_worked += timedelta(hours=hours, minutes=minutes, seconds=seconds)
            total_hours = round(total_time_worked.total_seconds() // 3600)
            total_minutes = round((total_time_worked.total_seconds() % 3600) // 60)
            
            best_day = db.best_day_collection(username)
            best_day_date = datetime.strptime(best_day[2], '%Y-%m-%d %H:%M').date()
            best_day_from = datetime.strptime(best_day[2], '%Y-%m-%d %H:%M').strftime('%H:%M')
            best_day_to = datetime.strptime(best_day[3], '%Y-%m-%d %H:%M').strftime('%H:%M')
            best_day_total_time = datetime.strptime(best_day[4], '%H:%M:%S').time()
            best_day_hours, best_day_minutes = best_day_total_time.hour, best_day_total_time.minute
            
            if len(stats) >= 4:
                worse_day = db.worse_day_collection(username)
                worse_day_date = datetime.strptime(worse_day[2], '%Y-%m-%d %H:%M').date()
                worse_day_from = datetime.strptime(worse_day[2], '%Y-%m-%d %H:%M').strftime('%H:%M')
                worse_day_to = datetime.strptime(worse_day[3], '%Y-%m-%d %H:%M').strftime('%H:%M')
                worse_day_total_time = datetime.strptime(worse_day[4], '%H:%M:%S').time()
                worse_day_hours, worse_day_minutes = worse_day_total_time.hour, worse_day_total_time.minute
            
            max_earnings = max([float(record[6]) for record in stats])
            max_collection = max([int(record[5]) for record in stats])
            user = db.get_user(username)
            
            message_text = (
                f'Пользователь: @{username}\n\n'
                f'Полное имя: {user[1]} \n'
                f'Номер: {user[2]} \n'
                f'Дата рождения: {user[3]}\n\n'
                f'Статистика:\n\n'
                f'Всего выходов: {len(stats)} \n'
                f'Всего собрано: {total_collection}€ \n'
                f'Всего заработано: {total_earnings}€ \n'
                f'Всего проработано: {total_hours}ч {total_minutes}м \n\n'
                f'Больше всего собрано за день: {max_collection}€ \n'
                f'Больше всего заработано за день: {max_earnings}€ \n\n'
                f'🎉 Лучший рабочий день: {best_day_date} \n\n'
                f'Часы работы лучшего дня: {best_day_from} - {best_day_to} \n'
                f'Общее время работы лучшего дня: {best_day_hours}ч {best_day_minutes}м \n'
                f'Общий сбор лучшего дня: {best_day[5]}€\n'
                f'Общий заработок лучшего дня: {best_day[6]}€\n\n'
            )

            if len(stats) >= 5:
                message_text += (
                    f'😭 Худший рабочий день: {worse_day_date} \n\n'
                    f'Часы работы худшего дня: {worse_day_from} - {worse_day_to} \n'
                    f'Общее время работы худшего дня: {worse_day_hours}ч {worse_day_minutes}м \n'
                    f'Общий сбор худшего дня: {worse_day[5]}€\n'
                    f'Общий заработок худшего дня: {worse_day[6]}€'
                )
            await callback.message.edit_text(message_text, reply_markup=prkb.pback)
        else:
            await callback.message.edit_text(f'Ваша статистика\n\n'
                                             f'Вы не разу не выходили на работу!', reply_markup=prkb.pback)