from aiogram.fsm.state import StatesGroup, State


class UpdateFile(StatesGroup):
    UpdateKeywordsFile = State()
    UpdateGroupsFile = State()