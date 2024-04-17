from typing import Union

from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery

from data.config import ADMINS


class IsAdmin(Filter):
    """Checking if a user is an administrator"""

    def __init__(self) -> None:
        pass

    async def __call__(self, query_or_message: Union[Message, CallbackQuery]) -> bool:
        return str(query_or_message.from_user.id) in ADMINS
