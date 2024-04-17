import os

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from filters.is_admin import IsAdmin
from keyboards.inline.admin_panel_keyboard import back_button_keyboard
from loader import bot, get_admin_panel
from states.file_viewing_state import ViewFile
from states.updating_file_state import UpdateFile
from loader import get_current_message_id

router = Router()


@router.callback_query(F.data == "check_keywords_file", IsAdmin())
async def check_keywords_file(call: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(chat_id=call.from_user.id,
                                text="Файл с ключевыми словами отправлен",
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=back_button_keyboard)
    file = FSInputFile("data/keywords.txt")
    bot_message = await bot.send_document(chat_id=call.from_user.id, document=file)
    await state.set_state(ViewFile.ViewFile)
    await state.update_data(message=bot_message)
    await call.answer()


@router.callback_query(F.data.in_(["edit_keywords_file", "create_keywords_file"]), IsAdmin())
async def start_update_keywords_file(call: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(text="Отправьте текстовый файл с ключевыми словами", chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=back_button_keyboard)
    await state.set_state(UpdateFile.UpdateKeywordsFile)
    await call.answer()


@router.message(UpdateFile.UpdateKeywordsFile, IsAdmin())
async def save_keywords_file(message: types.Message, state: FSMContext):
    if message.document:
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.download_file(file_path, "data/keywords.txt")
        await bot.edit_message_text(text="Файл с ключевыми словами изменен", chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
        await state.clear()
    else:
        await bot.edit_message_text(text="Отправьте текстовый файл с ключевыми словами", chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
