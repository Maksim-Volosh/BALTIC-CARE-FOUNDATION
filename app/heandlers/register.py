import re

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import app.keyboards.main_keyboards as mainkb
import config
from app.database import Database
from app.states import Register
from app.utils.utils import check_registered, is_admin

bot = Bot(token=config.TOKEN)  
router = Router()


# Register
@router.message(F.text == "Зарегестрироваться")
async def start_register(message: Message, state: FSMContext):
    """
    The start_register command is called when the user sends the /start_register command. It sends a welcome message
    to the user and sends a sticker to the user as well.
    """
    if not await check_registered(message):  
        username = message.from_user.username
        if not username:
            await message.answer('Для начала тебе нужно создать username у себя в профиле!!',
                                 reply_markup=mainkb.start)
        else:
            await message.answer('Привет, для начала тебе нужно ввести токен который тебе дал менеджер \n\nВведи токен!',
                                reply_markup=mainkb.cancel)
            await state.set_state(Register.RegToken)
    else:
        if await is_admin(message):
            await message.answer('Вы администратор', reply_markup=mainkb.main)
        
        else: await message.answer('Вы уже зарегестрированы!',
                             reply_markup=mainkb.main)
        

@router.message(Register.RegToken)
async def register_token(message: Message, state: FSMContext):
    """
    Handles the registration of the user's token.
    
    This function is called when the user sends a message with their token during the registration process. It updates the user's data with their token and sets the state to RegFullName.
    """
    db = Database(config.DB_NAME)
    validate = db.get_token(message.text)
    if not validate:
        await message.answer('Токен неверный, попробуйте ещё раз', reply_markup=mainkb.cancel)
        return
    else:
        await state.update_data(token=message.text)
        await message.answer('Отлично, токен верный!! Теперь давай познакомимся, как тебя зовут? \n\nВведи имя и фамилию как в паспорте, английскими буквами!',
                                reply_markup=mainkb.cancel)
        await state.set_state(Register.RegFullName)

@router.message(Register.RegFullName)
async def register_fullname(message: Message, state: FSMContext):
    """
    Handles the registration of the user's full name.
    
    This function is called when the user sends a message with their full name during the registration process. It updates the user's data with their full name and sets the state to RegPhoneNumber.
    """
    await message.answer(f'Приятно познакомиться {message.text} \n'
                         f'Теперь напишете свой номер телефона! \n'
                         f'Формат: +370XXXXXXXX')
    await state.update_data(regfullname=message.text)
    await state.set_state(Register.RegPhoneNumber)
    
@router.message(Register.RegPhoneNumber)
async def register_phone(message: Message, state: FSMContext):
    """
    Handles the registration of the user's phone number.
    
    This function is called when the user sends a message with their phone number during the registration process. It updates the user's data with their phone number and sets the state to RegDate.
    """
    if(re.findall(r"\+370\d{8}", message.text)):
        await message.answer(f'Ваш номер {message.text} \n'
                             f'Теперь напишите свою дату рождения! \n'
                             f'Формат: дд.мм.гггг.')
        await state.update_data(regphonenumber=message.text)
        await state.set_state(Register.RegDate)
    else:
        await message.answer('Номер указан в неправильном формате!')

@router.message(Register.RegDate)
async def register_date(message: Message, state: FSMContext):
    """
    Handles the registration of the user's date of birth.
    
    This function is called when the user sends a message with their date of birth during the registration process. It updates the user's data with their date of birth and sets the state to RegFinish.
    """
    await message.answer(f'Ваша дата рождения {message.text}, все данные верны?', reply_markup=mainkb.yes_or_no)
    await state.update_data(regdate=message.text)
    await state.set_state(Register.RegFinish)

@router.message(Register.RegFinish)
async def register_finish(message: Message, state: FSMContext):
    """
    Handles the final step of the registration process.
    
    If the user confirms the registration data, their data is added to the database and a confirmation message is sent to the user. Otherwise, the user is given the option to go back to the registration process.
    """
    if message.text == 'Да':
        reg_data = await state.get_data()    
    
        reg_fullname = reg_data.get('regfullname')
        reg_phonenumber = reg_data.get('regphonenumber')
        reg_date = reg_data.get('regdate')
        token = reg_data.get('token')
        
        db = Database(config.DB_NAME)
            
        db.add_user(reg_fullname, reg_phonenumber, reg_date, message.from_user.username)

        await message.answer('Регистрация прошла успешно! Теперь вы можете начать работу! \n\nДля этого обратитесь к своему менеджеру, возьмите инвентарь и спросите номер места для работ! \n\nПосле, нажимайте - "Начать работу"!',
                            reply_markup=mainkb.main)
        db.delete_token(token)
        await state.clear()
    else:       
        await message.answer('Вы вернулись назад', reply_markup=mainkb.start)
        await state.clear()