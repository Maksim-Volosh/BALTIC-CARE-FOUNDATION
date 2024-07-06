from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

admin_profile = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пользователи', callback_data='all_users')],
    [InlineKeyboardButton(text='Статистика', callback_data='stats')],
])

admin_profile_users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Выбрать пользователя', callback_data='all_users')],
    [InlineKeyboardButton(text='Назад', callback_data='pback')],
])

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_pagination_markup(page, total_users, per_page=15):
    total_pages = (total_users + per_page - 1) // per_page
    navigation_buttons = []

    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text='⬅️ Назад', callback_data=f'page_{page - 1}'))

    if page < total_pages:
        navigation_buttons.append(InlineKeyboardButton(text='Вперед ➡️', callback_data=f'page_{page + 1}'))
    
    back_button = InlineKeyboardButton(text='Назад', callback_data='pback')
    
    # Inline keyboard rows
    keyboard = []
    if navigation_buttons:
        keyboard.append(navigation_buttons)
    keyboard.append([back_button])
    
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    return markup





admin_users_user = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Посмотреть статистику', callback_data='get_user_stats')],
    [InlineKeyboardButton(text='Удалить пользователя', callback_data='delete_user')],
    [InlineKeyboardButton(text='Удалить статистику пользователя', callback_data='delete_user_stats')],
    [InlineKeyboardButton(text='Сменить пользователя', callback_data='all_users')],
    [InlineKeyboardButton(text='Назад', callback_data='pback')],
])

admin_users_user_stats = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Удалить пользователя', callback_data='delete_user')],
    [InlineKeyboardButton(text='Удалить статистику пользователя', callback_data='delete_user_stats')],
    [InlineKeyboardButton(text='Сменить пользователя', callback_data='all_users')],
    [InlineKeyboardButton(text='Назад', callback_data='pback')],   
])

admin_delete_stats = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='delete_stats_yes')],
    [InlineKeyboardButton(text='Нет', callback_data='pback')],
])

admin_delete_user = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='delete_user_yes')],
    [InlineKeyboardButton(text='Нет', callback_data='pback')],
])

admin_profile_stats = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='pback')],
])

pback = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='pback')],
])