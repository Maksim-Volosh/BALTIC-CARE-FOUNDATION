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

about_us = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Основная информация', callback_data='maininfo')],
    [InlineKeyboardButton(text='О сборах', callback_data='aboutcoll')],
    [InlineKeyboardButton(text='Назад', callback_data='back')],
])

aboutcoll = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Помощь людям пострадавшим от войны', callback_data='help1')],
    [InlineKeyboardButton(text='Помощь Украинским военным', callback_data='help2')],
    [InlineKeyboardButton(text='Помощь детям с ограниченными возможностями', callback_data='help3')],
    [InlineKeyboardButton(text='Оказание помощи приютам для животных', callback_data='help4')],
    [InlineKeyboardButton(text='Передача гуманитарных грузов для медицинских учереждений', callback_data='help5')],
    [InlineKeyboardButton(text='Сбор, закупка и выдача продуктовых, гигиенических наборов', callback_data='help6')],
    [InlineKeyboardButton(text='Архив видео', callback_data='videos')],
    
    [InlineKeyboardButton(text='Назад', callback_data='inback')],
])

inlineback = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='inback')],
])