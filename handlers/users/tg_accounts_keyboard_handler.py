import os.path

from TGConvertor import SessionManager, TeleSession
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from filters.is_admin import IsAdmin
from keyboards.inline.admin_panel_keyboard import back_button_keyboard, get_login_data_tg_keyboard
from loader import bot, get_admin_panel
from states.editing_tg_login_data_state import TgLoginDataEditing
from loader import get_current_message_id
from states.getting_login_tg_data_state import GetLoginData
from utils.files_rw import save_admin_panel
from utils.services_api.lolzteam_api import buy_account, get_last_purchased_login_data, check_lolzteam_connection, \
    initialize_market
from utils.services_api.tg_api import check_valid, check_can_send_messages

router = Router()


@router.callback_query(F.data == "buy_new_tg_account", IsAdmin())
async def buy_new_tg_account(call: types.CallbackQuery):
    if check_lolzteam_connection():
        response = buy_account()
        errors = None
        try:
            errors = response["errors"]
        except KeyError:
            pass
    else:
        try:
            errors = initialize_market().profile.get().json()['error_description']
        except KeyError:
            errors = "Проблемы с подключением к аккаунту. Проверьте токен."
    if errors:
        await bot.edit_message_text(chat_id=call.from_user.id, text=f"Ошибка: {errors}",
                                    reply_markup=back_button_keyboard,
                                    message_id=get_current_message_id(call.from_user.id))
        await call.answer()
        return
    admin_panel = get_admin_panel()
    result = get_last_purchased_login_data()
    admin_panel.set_current_session(result)
    print(result)
    print(admin_panel.get_current_session())
    save_admin_panel(admin_panel)
    await bot.edit_message_text(chat_id=call.from_user.id, text="Куплен новый аккаунт",
                                reply_markup=back_button_keyboard,
                                message_id=get_current_message_id(call.from_user.id)
                                )
    await call.answer()


@router.callback_query(F.data == "input_new_login_data_tg", IsAdmin())
async def start_input_new_login_data_tg(call: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(text="Введите новые данные для входа",
                                chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=back_button_keyboard)
    await state.set_state(TgLoginDataEditing.TgLoginDataEditing)
    await call.answer()


@router.message(TgLoginDataEditing.TgLoginDataEditing, IsAdmin())
async def set_new_tg_login_data(message: types.Message, state: FSMContext):
    login_data = message.text
    admin_panel = get_admin_panel()
    if await check_valid(login_data):
        admin_panel.set_current_session(login_data)
        save_admin_panel(admin_panel)
        await bot.edit_message_text(text="Данные для входа изменены",
                                    chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
        await state.clear()
    else:
        await bot.edit_message_text(text="Данные для входа неверны. Попробуйте еще раз или проверьте прокси",
                                    chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)


@router.callback_query(F.data == "check_spam_block", IsAdmin())
async def check_spam_block(call: types.CallbackQuery):
    result = await check_can_send_messages()
    if result:
        await bot.edit_message_text(text="Спамблока нет, вы можете отправлять сообщения",
                                    chat_id=call.from_user.id,
                                    message_id=get_current_message_id(call.from_user.id),
                                    reply_markup=back_button_keyboard)
    else:
        await bot.edit_message_text(text="Спамблок есть, вы не можете отправлять сообщения",
                                    chat_id=call.from_user.id,
                                    message_id=get_current_message_id(call.from_user.id),
                                    reply_markup=back_button_keyboard)


@router.callback_query(F.data == "get_login_data_tg", IsAdmin())
async def start_getting_login_data_tg(call: types.CallbackQuery):
    await bot.edit_message_text(text="Выберите формат исходных данных для преобразования в Session String",
                                chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=get_login_data_tg_keyboard)
    await call.answer()


@router.callback_query(F.data == "auth_key_get_login_data", IsAdmin())
async def start_getting_auth_key_login_data(call: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(text="Введите Auth Key",
                                chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=back_button_keyboard)
    await state.set_state(GetLoginData.InputAuthKey)
    await call.answer()


@router.message(GetLoginData.InputAuthKey, IsAdmin())
async def input_auth_key(message: types.Message, state: FSMContext):
    auth_key = message.text
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    try:
        auth_key = bytes.fromhex(auth_key)
    except ValueError:
        await bot.edit_message_text(text="Ошибка: Auth key должен быть строкой формата HEX. Введите Auth Key.",
                                    chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
        return
    await state.update_data(auth_key=auth_key)
    await bot.edit_message_text(text="Введите DC ID",
                                chat_id=message.from_user.id,
                                message_id=get_current_message_id(message.from_user.id),
                                reply_markup=back_button_keyboard)
    await state.set_state(GetLoginData.InputDcId)


@router.message(GetLoginData.InputDcId, IsAdmin())
async def input_dc_id(message: types.Message, state: FSMContext):
    dc_id = message.text
    try:
        dc_id = int(dc_id)
    except ValueError:
        await bot.edit_message_text(text="DC ID должен быть числом. Введите DC ID.",
                                    chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        return
    if dc_id < 1 or dc_id > 5:
        await bot.edit_message_text(text="DC ID должен быть целым числом от 1 до 5. Введите DC ID.",
                                    chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        return
    await state.update_data(dc_id=dc_id)
    await state.set_state(GetLoginData.GetSessionStringFromAuthKey)
    await get_login_data_from_auth_key(message, state)


async def get_login_data_from_auth_key(message: types.Message, state: FSMContext):
    data = await state.get_data()
    auth_key = data["auth_key"]
    dc_id = data["dc_id"]
    session_string = SessionManager.to_telethon_string(SessionManager(auth_key=auth_key, dc_id=dc_id))
    await bot.edit_message_text(text=f"Данные для входа: \n\n"
                                     f"{session_string}"
                                     f"\n\nСохраните их",
                                chat_id=message.from_user.id,
                                message_id=get_current_message_id(message.from_user.id),
                                reply_markup=back_button_keyboard)
    await state.clear()
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)


@router.callback_query(F.data == "session_file_get_login_data", IsAdmin())
async def start_get_login_data_from_file(call: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(text="Отправьте session-файл", chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=back_button_keyboard)
    await state.set_state(GetLoginData.InputFile)
    await call.answer()


@router.message(GetLoginData.InputFile, IsAdmin())
async def get_session_string_from_file(message: types.Message, state: FSMContext):
    if message.document:
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.download_file(file_path, "data/current.session")
    else:
        await bot.edit_message_text(text="Отправьте session-файл", chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
        return
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    current_session = "data/current.session"
    try:
        session = await TeleSession.from_file(path=current_session)
    except Exception as err:
        print(err)
        await bot.edit_message_text(text="Некорректный файл. Отправьте session-файл", chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
        if os.path.exists(current_session):
            os.remove(current_session)
        return

    if os.path.exists(current_session):
        os.remove(current_session)

    session_string = session.to_string()
    await bot.edit_message_text(text=f"Данные для входа: \n\n"
                                     f"{session_string}"
                                     f"\n\nСохраните их",
                                chat_id=message.from_user.id,
                                message_id=get_current_message_id(message.from_user.id),
                                reply_markup=back_button_keyboard)
    await state.clear()
