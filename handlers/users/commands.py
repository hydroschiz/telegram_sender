from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from filters.is_admin import IsAdmin
from keyboards.inline.admin_panel_keyboard import admin_panel_buttons
from loader import get_admin_panel, db_helper, bot
from utils.files_rw import get_keywords

router = Router()


@router.message(CommandStart())
async def command_start(message: Message):
    await message.answer(f"Привет, {message.from_user.full_name}")


@router.message(Command("admin"), IsAdmin())
async def command_admin(message: Message):
    admin_panel = get_admin_panel()
    bots_message = await message.answer(f"Отправлено сообщений всего: {admin_panel.messages_sent}\n",
                                        reply_markup=admin_panel_buttons)
    result = db_helper.add_admin(message.from_user.id, bots_message.message_id)
    if isinstance(result, Exception):
        result = db_helper.update_message_id_of_admin(message.from_user.id, bots_message.message_id)
    if isinstance(result, Exception):
        print(result)
