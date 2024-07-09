from aiogram import Bot, F, Router, types
from aiogram.types import (CallbackQuery, FSInputFile, InputMediaPhoto,
                           InputMediaVideo, Message)

import app.keyboards.main_keyboards as mainkb
import config

bot = Bot(token=config.TOKEN)  
router = Router()

# About us
@router.message(F.text == 'О нас')
async def about_us(message: Message):
    """
    Displays information about the organization.
    """
    reply_markup=mainkb.about_us
    await message.answer(
        f'<i><b>Приветствую вас, уважаемые волонтеры!</b></i>🙂\n\n'
        f'📍<i><b>Тут размещена вся информация о фонде, структуре работы, сборах, выполненных запросах и тд. Ниже будут кнопки (нажимаете на кнопку и вас перебросит на инфо о данной теме)</b></i>\n\n'
        f'❗️<i><b>Прошу вас ознакомиться с каждым блоком информации, это поможет вам при выполнении волонтерской деятельности и повысит ваш уровень знаний</b></i>❗️', parse_mode='HTML', reply_markup=reply_markup)
    
@router.callback_query(F.data == 'maininfo')
async def maininfo(callback: CallbackQuery):
    """
    Handles the maininfo callback query. It sends a message with the main information about the organization.
    """
    await callback.message.edit_text(
        f'<u>ОСНОВНАЯ ИНФОРМАЦИЯ О ФОНДЕ</u>❣️\n\n'
        f'Полное имя: <b>Labdaros ir paramos fondas "Baltic care foundation"</b>\n'
        f'Код компании: 306333331\n'
        f'Основатель/учредитель: <b>Дмитрий Жмур</b>',
        parse_mode='HTML', reply_markup=mainkb.inlineback)
    
@router.callback_query(F.data == 'aboutcoll')
async def aboutcoll(callback: CallbackQuery):
    """
    Handles the aboutcoll callback query. It sends a message with the information about the collection.
    """
    await callback.message.edit_text(
        f'<b>СБОРЫ</b> (программы фонда на которые ведется сбор)❣️\n\n'

        f'📍Помощь людям пострадавшим от войны в Украине ❤️🇺🇦\n\n'

        f'📍Помощь Украинским военным🇺🇦🇺🇦\n\n'

        f'📍Помощь детям с ограниченными возможностями, а также детям с серьезными врожденными заболеваниями🤱👶\n\n'

        f'📍Оказание помощи приютам для животных на территории Литвы и Украины😉👣\n\n'

        f'📍Передача гуманитарных грузов для медицинских учереждений (госпитали, реабилитационные центры, родильные дома) 🏥\n\n'

        f'📍Сбор, закупка и выдача продуктовых, гигиенических наборов🍞🥫\n\n', 
        parse_mode='HTML', reply_markup=mainkb.aboutcoll)

@router.callback_query(F.data == 'help1')
async def help1(callback: CallbackQuery):
    caption=(
        '<b>❤️Помощь людям пострадавшим от войны в Украине🇺🇦</b>\n\n'
        '-Эвакуация людей, животных из прифронтовых городов. На данный момент с нашей помощью эвакуировано более 90 семей.\n\n'
        '-Оплата вынужденного переезда для семей из Донецкой, Луганской, Запорожской, Херсонской обласей (по Украине+оплата дороги на территорию Европы)\n\n'
        '-Оплата первых расходов (заселение, вещи первой необходимости)\n\n'
    )
    photo_path = 'app/media/help1.jpg'
    
    await callback.answer()
    await callback.message.answer_photo(
        types.FSInputFile(path=photo_path), caption=caption, parse_mode='HTML'
    )
    
@router.callback_query(F.data == 'help2')
async def help2(callback: CallbackQuery):
    caption=(
        f'<b>🇺🇦Помощь Украинским военным 🇺🇦</b>\n\n'
        f'-Мы закупаем форму, амуницию (плиты для бронежилетов, кевларовые шлемы, тактические штаны, наколенники и иное оборудование)\n\n'
        f'-Покупка автомобилей для военных бригад - на данный момент было отправлено 5 автомобилей для 38 отдельной бригады морской пихоты а также <a href="https://ab3.army/">3 отдельной штурмовой бригады</a>\n\n'
        f'-Закупка и отправка специального оборудывания для военных а именно:\n'
        f'📍дроны и их комплектующие (запрос в процессе выполнения)\n'
        f'📍устройства для безперебойного интернет соединения "StarLink" а также подписка на пакет услуг (оплата каждый месяц)'
    )
    
    
    photo_paths = ['app/media/help2_2.jpg', 'app/media/help2_3.jpg', 'app/media/help2_4.jpg', 'app/media/help2_5.jpg', 'app/media/help2_6.jpg']

    media = [InputMediaPhoto(media=FSInputFile(path='app/media/help2_1.jpg'), caption=caption, parse_mode='HTML'),]
    
    for photo in photo_paths:
        media.append(InputMediaPhoto(media=FSInputFile(path=photo)))
    
    await callback.answer()
    await callback.message.answer_media_group(media=media)
    
@router.callback_query(F.data == 'help3')
async def help3(callback: CallbackQuery):
    caption=(
        f'<b>🤱👶Помощь детям с ограниченными возможностями, а также детям с серьезными врожденными заболеваниями🤱👶</b>\n\n'
        f'-Оплата лечения и реабилитации после операций\n\n'
        f'-Материальная поддержка семей в трудных условиях'
    )
    
    
    photo_paths = ['app/media/help3_2.jpg', 'app/media/help3_3.jpg']

    media = [InputMediaPhoto(media=FSInputFile(path='app/media/help3_1.jpg'), caption=caption, parse_mode='HTML'),]
    
    for photo in photo_paths:
        media.append(InputMediaPhoto(media=FSInputFile(path=photo)))
    
    await callback.answer()
    await callback.message.answer_media_group(media=media)
    
@router.callback_query(F.data == 'help4')
async def help4(callback: CallbackQuery):
    caption=(
        '<b>😉👣Оказание помощи приютам для животных на территории Литвы и Украины😉👣</b>\n\n'
        '-Регулярная отправка кормов для животных\n\n'
        '-Закупка инвентаря для жизни наших маленьких друзей\n\n'
        '-Организация по выгулу животных в городах Вильнюс и Каунас'
    )
    photo_path = 'app/media/help4_1.jpg'
    
    await callback.answer()
    await callback.message.answer_photo(
        types.FSInputFile(path=photo_path), caption=caption, parse_mode='HTML'
    )
    
@router.callback_query(F.data == 'help5')
async def help5(callback: CallbackQuery):
    caption=(
        f'<b>Передача гуманитарных грузов для медицинских учереждений (госпитали, реабилитационные центры, родильные дома) 🏥</b>\n\n'
        f'-Закупка расходных материалов а также медикаментов для медицинских учреждений(уже отправлено более 60 упаковок подгузников для взрослых в госпиталь в Украине, также отправлены бинты, шприцы; также отправлен набор помощи в Запорожский перинатальный центр)'
    )
    
    photo_paths = ['app/media/help5_2.jpg', 'app/media/help5_3.jpg']

    media = [InputMediaPhoto(media=FSInputFile(path='app/media/help5_1.jpg',), caption=caption, parse_mode='HTML'),]
    
    for photo in photo_paths:
        media.append(InputMediaPhoto(media=FSInputFile(path=photo)))
    
    await callback.answer()
    await callback.message.answer_media_group(media=media)
    
@router.callback_query(F.data == 'videos')
async def videos(callback: CallbackQuery):
    videos_paths = ['app/media/video1.mp4', 'app/media/video2.mp4',]

    media = [
        InputMediaVideo(media=FSInputFile(path=videos_paths[0])),
        InputMediaVideo(media=FSInputFile(path=videos_paths[1])),
    ]
    
    await callback.message.answer_media_group(media=media)
    await callback.answer()
    
@router.callback_query(F.data == 'inback')
async def inback(callback: CallbackQuery):
    reply_markup=mainkb.about_us
    await callback.message.edit_text    (
        f'<i><b>Приветствую вас, уважаемые волонтеры!</b></i>🙂\n\n'
        f'📍<i><b>Тут размещена вся информация о фонде, структуре работы, сборах, выполненных запросах и тд. Ниже будут кнопки (нажимаете на кнопку и вас перебросит на инфо о данной теме)</b></i>\n\n'
        f'❗️<i><b>Прошу вас ознакомиться с каждым блоком информации, это поможет вам при выполнении волонтерской деятельности и повысит ваш уровень знаний</b></i>❗️', 
        parse_mode='HTML', reply_markup=reply_markup)