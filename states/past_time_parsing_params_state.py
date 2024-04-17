from aiogram.fsm.state import StatesGroup, State


class PastTimeParsingParams(StatesGroup):
    InputDate = State()
    InputHours = State()