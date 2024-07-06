from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup  


start_work = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Я пришел и начал работу', callback_data='work_started')],
    [InlineKeyboardButton(text='Отмена', callback_data='back')]
])  

work_started = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Сделать перерыв', callback_data='pause_work')],
    [InlineKeyboardButton(text='Закончить работу', callback_data='end_work')]
])  

pause_work = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Продолжить', callback_data='resume_work')],
    [InlineKeyboardButton(text='Закончить работу', callback_data='end_work')]
])
