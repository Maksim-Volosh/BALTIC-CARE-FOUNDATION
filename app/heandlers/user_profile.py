from datetime import datetime, timedelta

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, Message

import app.keyboards.main_keyboards as mainkb
import app.keyboards.profile_keyboards as prkb
import config
from app.database import Database
from app.utils.utils import check_registered

bot = Bot(token=config.TOKEN)  
router = Router()


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
            
            if len(stats) >= 3:
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

            if len(stats) >= 3:
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