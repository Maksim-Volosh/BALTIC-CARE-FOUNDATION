from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Начать работу'), 
     KeyboardButton(text='О нас')],
],  resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню')    


start_work = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Я пришел и начал работу', callback_data='work_started')],
    [InlineKeyboardButton(text='Отмена', callback_data='back')]
])  
