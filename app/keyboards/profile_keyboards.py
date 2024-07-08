from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import config 

"""========= ADMIN PROFILE ========="""

admin_profile = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пользователи', callback_data='all_users')],
    [InlineKeyboardButton(text='Статистика', callback_data='stats')],
    [InlineKeyboardButton(text='Точки', callback_data='places')],
])

admin_all_places = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить точку', callback_data='add_place')],
    [InlineKeyboardButton(text='Назад', callback_data='pback')],
])

admin_place = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Удалить точку', callback_data='delete_place')],
    [InlineKeyboardButton(text='Назад', callback_data='pback')],
])

admin_delete_place = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='delete_place_yes')],
    [InlineKeyboardButton(text='Нет', callback_data='pback')],
])

admin_add_place = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='add_place_yes')],
    [InlineKeyboardButton(text='Нет', callback_data='add_place_no')],
])

admin_place_added = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить еще точку', callback_data='add_place')],
    [InlineKeyboardButton(text='Назад', callback_data='pback')],
])

admin_profile_users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Выбрать пользователя', callback_data='all_users')],
    [InlineKeyboardButton(text='Назад', callback_data='pback')],
])

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

"""========= USER PROFILE ========="""

user_profile = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Статистика и информация', callback_data='user_stats')],
])

"""========= OTHER ========="""

def get_pagination_markup(page, total_users, per_page=config.DEF_PAGINATE):
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

pback = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='pback')],
])
