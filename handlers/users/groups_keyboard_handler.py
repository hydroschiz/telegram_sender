import datetime

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from filters.is_admin import IsAdmin
from keyboards.inline.admin_panel_keyboard import back_button_keyboard, select_parsing_type_buttons
from loader import bot, get_admin_panel
from states.file_viewing_state import ViewFile
from states.past_time_parsing_params_state import PastTimeParsingParams
from states.updating_file_state import UpdateFile
from loader import get_current_message_id
from utils.files_rw import save_admin_panel
from utils.services_api.tg_api import join_groups

router = Router()


@router.callback_query(F.data == "join_groups_button", IsAdmin())
async def join_groups_button(call: types.CallbackQuery):
    await join_groups()
    await call.answer()


@router.callback_query(F.data == "check_groups_file", IsAdmin())
async def check_groups_file(call: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(chat_id=call.from_user.id,
                                text="Файл с группами отправлен",
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=back_button_keyboard)
    file = FSInputFile("data/groups.txt")
    bot_message = await bot.send_document(chat_id=call.from_user.id, document=file)
    await state.set_state(ViewFile.ViewFile)
    await state.update_data(message=bot_message)
    await call.answer()


@router.callback_query(F.data.in_(["edit_groups_file", "create_groups_file"]), IsAdmin())
async def start_update_groups_file(call: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(text="Отправьте текстовый файл с группами", chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=back_button_keyboard)
    await state.set_state(UpdateFile.UpdateGroupsFile)
    await call.answer()


@router.message(UpdateFile.UpdateGroupsFile, IsAdmin())
async def save_groups_file(message: types.Message, state: FSMContext):
    if message.document:
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.download_file(file_path, "data/groups.txt")
        await bot.edit_message_text(text="Файл с группами изменен", chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
        await state.clear()
    else:
        await bot.edit_message_text(text="Ошибка, отправьте текстовый файл с группами", chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)


@router.callback_query(F.data == "start_parsing")
async def start_parsing(call: types.CallbackQuery):
    # admin_panel = get_admin_panel()
    # admin_panel.set_parsing_status(True)
    # save_admin_panel(admin_panel)
    await bot.edit_message_text(text="Выберите тип парсинга", chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=select_parsing_type_buttons)


@router.callback_query(F.data == "select_realtime_parsing")
async def start_realtime_parsing(call: types.CallbackQuery):
    admin_panel = get_admin_panel()
    admin_panel.set_parsing_status(True)
    admin_panel.set_parsing_params(
        {
            'type': 'realtime'
        }
    )
    save_admin_panel(admin_panel)
    await bot.edit_message_text(text="Активирован парсинг в реальном времени", chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=back_button_keyboard)
    await call.answer()


@router.callback_query(F.data == "select_past_time_parsing")
async def start_past_time_parsing(call: types.CallbackQuery):
    admin_panel = get_admin_panel()
    admin_panel.set_parsing_status(True)
    admin_panel.set_parsing_params(
        {
            'type': 'past_time'
        }
    )
    save_admin_panel(admin_panel)
    await bot.edit_message_text(text="Активирован парсинг предыдущих сообщений", chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=back_button_keyboard)
    await call.answer()


@router.callback_query(F.data == "stop_parsing")
async def stop_parsing(call: types.CallbackQuery):
    admin_panel = get_admin_panel()
    admin_panel.set_parsing_status(False)
    admin_panel.set_parsing_params(None)
    save_admin_panel(admin_panel)
    await bot.edit_message_text(text="Парсинг остановлен", chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=back_button_keyboard)
