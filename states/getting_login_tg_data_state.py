from aiogram.fsm.state import StatesGroup, State


class GetLoginData(StatesGroup):
    InputAuthKey = State()
    InputDcId = State()
    GetSessionStringFromAuthKey = State()
    InputFile = State()
