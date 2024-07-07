import calendar
from datetime import datetime, timedelta
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.heandlers.heandlers import is_admin
from app.states import ChoiceUser
from aiogram import Bot
from app.database import Database
import app.keyboards.main_keyboards as mainkb
import app.keyboards.profile_keyboards as prkb
from app.utils.utils import paginate_users
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
        await message.answer('Профиль юзера', reply_markup=mainkb.main)

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
        await callback.message.edit_text('Нет пользователей на этой странице.', reply_markup=prkb.get_pagination_markup(page, len(users)))
    
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
                             f'Имя: {user[1]} \n\n'
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
    total_collection_current_month = db.total_collection_current_month()
    count_work_records_current_month = db.count_work_records_current_month()    
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

@router.callback_query(F.data == 'pback')
async def back(callback: CallbackQuery, state: FSMContext):
    """
    Back to admin profile menu.
    """
    await state.clear()
    await callback.message.edit_text('Добро пожаловать в профиль админа!!! \n\nЧто вы хотите сделать?', reply_markup=prkb.admin_profile)