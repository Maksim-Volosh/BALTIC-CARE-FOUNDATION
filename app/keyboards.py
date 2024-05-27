from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

start = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Зарегестрироваться'), KeyboardButton(text='Войти')],
],  resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выберите пункт меню')

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Начать работу'), 
     KeyboardButton(text='О нас')],
],  resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню')    


start_work = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Я пришел и начал работу', callback_data='work_started')],
    [InlineKeyboardButton(text='Отмена', callback_data='back')]
])  

work_started = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Сделать перерыв', callback_data='pause_work')],
    [InlineKeyboardButton(text='Закончить работу', callback_data='end_work')]
])  
