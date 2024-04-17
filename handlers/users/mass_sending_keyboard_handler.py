import os.path

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from filters.is_admin import IsAdmin
from keyboards.inline.admin_panel_keyboard import back_button_keyboard
from loader import bot, get_admin_panel, db_helper
from loader import get_current_message_id
from states.file_viewing_state import ViewFile
from states.setting_timings_state import SettingTimings
from utils.db_api.table_to_excel import table_to_xlsx
from utils.files_rw import save_admin_panel

router = Router()


@router.callback_query(F.data == "start_mass_sending", IsAdmin())
async def start_mass_sending(call: types.CallbackQuery):
    admin_panel = get_admin_panel()
    admin_panel.set_sending_status(True)
    await bot.edit_message_text(text="Рассылка активирована", chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id), reply_markup=back_button_keyboard)
    save_admin_panel(admin_panel)
    await call.answer()


@router.callback_query(F.data == "stop_mass_sending", IsAdmin())
async def stop_mass_sending(call: types.CallbackQuery):
    admin_panel = get_admin_panel()
    admin_panel.set_sending_status(False)
    await bot.edit_message_text(text="Рассылка прервана", chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id), reply_markup=back_button_keyboard)
    save_admin_panel(admin_panel)
    await call.answer()


@router.callback_query(F.data == "null_users_mass_sending", IsAdmin())
async def null_users_button(call: types.CallbackQuery):
    db_helper.null_all_users()
    await bot.edit_message_text(text="Пользователи обнулены", chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id), reply_markup=back_button_keyboard)


@router.callback_query(F.data == "show_users_mass_sending", IsAdmin())
async def show_users_button(call: types.CallbackQuery, state: FSMContext):
    success = table_to_xlsx()
    if success:
        if os.path.exists('data/Users.xlsx'):
            await bot.edit_message_text(chat_id=call.from_user.id,
                                        text="Файл с таблицей пользователей отправлен",
                                        message_id=get_current_message_id(call.from_user.id),
                                        reply_markup=back_button_keyboard)
            file = FSInputFile("data/Users.xlsx")
            bot_message = await bot.send_document(chat_id=call.from_user.id, document=file)
            await state.set_state(ViewFile.ViewFile)
            await state.update_data(message=bot_message)
            os.remove('data/Users.xlsx')
    else:
        await bot.edit_message_text(chat_id=call.from_user.id,
                                    text="Возникла ошибка",
                                    message_id=get_current_message_id(call.from_user.id),
                                    reply_markup=back_button_keyboard)
    await call.answer()


@router.callback_query(F.data == "delete_users_mass_sending", IsAdmin())
async def delete_users_button(call: types.CallbackQuery):
    db_helper.delete_users()
    await bot.edit_message_text(text="Пользователи удалены", chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id), reply_markup=back_button_keyboard)


@router.callback_query(F.data == "set_sending_timings", IsAdmin())
async def start_setting_times(call: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(text="Введите нижнюю границу задержки", chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id), reply_markup=back_button_keyboard)
    await state.set_state(SettingTimings.Min)


@router.message(SettingTimings.Min)
async def set_min_delay(message: types.Message, state: FSMContext):
    try:
        min_delay = int(message.text)
    except ValueError:
        await bot.edit_message_text(text="Введите нижнюю границу задержки\n"
                                         "Ошибка: введите число", chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return
    if min_delay < 0:
        await bot.edit_message_text(text="Введите нижнюю границу задержки\n"
                                         "Ошибка: введите неотрицательное число", chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return
    await state.update_data(min_delay=min_delay)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await state.set_state(SettingTimings.Max)
    await bot.edit_message_text(text="Введите верхнюю границу задержки", chat_id=message.from_user.id,
                                message_id=get_current_message_id(message.from_user.id),
                                reply_markup=back_button_keyboard)


@router.message(SettingTimings.Max)
async def set_max_delay(message: types.Message, state: FSMContext):
    try:
        max_delay = int(message.text)
    except ValueError:
        await bot.edit_message_text(text="Введите верхнюю границу задержки\n"
                                         "Ошибка: введите число", chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return
    data = await state.get_data()
    min_delay = data["min_delay"]
    if max_delay < min_delay:
        await bot.edit_message_text(text="Введите верхнюю границу задержки\n"
                                         "Ошибка: верхняя граница не может быть меньше нижней",
                                    chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return
    admin_panel = get_admin_panel()
    admin_panel.set_delay(min_delay, max_delay)
    save_admin_panel(admin_panel)
    await bot.edit_message_text(text=f"Новые границы задержки установлены: от {min_delay} до {max_delay} секунд",
                                chat_id=message.from_user.id,
                                message_id=get_current_message_id(message.from_user.id),
                                reply_markup=back_button_keyboard)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await state.clear()
