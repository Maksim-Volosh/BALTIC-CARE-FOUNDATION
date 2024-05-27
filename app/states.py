from aiogram.fsm.state import State, StatesGroup

class Register(StatesGroup):
    RegFullName = State()
    RegPhoneNumber = State()
    RegDate = State()
    

class Place(StatesGroup):
    id_place = State()