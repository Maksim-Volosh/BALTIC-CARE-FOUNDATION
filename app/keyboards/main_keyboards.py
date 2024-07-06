from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

start = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Зарегестрироваться'),
     KeyboardButton(text='О нас')],
],  resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выберите пункт меню')

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Начать работу'), 
     KeyboardButton(text='О нас')],
    [KeyboardButton(text='Профиль')]
],  resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню')    

cancel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отмена')],
],  resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню')

yes_or_no = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Да'), 
     KeyboardButton(text='Нет')],
],  resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню')
