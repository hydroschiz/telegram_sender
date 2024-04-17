from aiogram.fsm.state import StatesGroup, State


class SettingTimings(StatesGroup):
    Min = State()
    Max = State()