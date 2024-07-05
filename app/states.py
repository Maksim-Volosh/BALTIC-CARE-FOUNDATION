from aiogram.fsm.state import State, StatesGroup

class Register(StatesGroup):
    RegFullName = State()
    RegPhoneNumber = State()
    RegDate = State()
    RegFinish = State()
    

class Place(StatesGroup):
    id_place = State()
    

class Work(StatesGroup):
    worktime_started = State()
    worktime_ended = State()
    collection = State()
    finish = State()