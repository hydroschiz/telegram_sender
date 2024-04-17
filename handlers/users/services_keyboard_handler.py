import json

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from data.config import get_lolz_token, get_proxy_token, get_tg_api_id, get_tg_api_hash
from filters.is_admin import IsAdmin
from keyboards.inline.admin_panel_keyboard import lolzteam_keyboard, proxy6_keyboard, tg_api_keyboard, \
    back_button_keyboard
from loader import bot, get_admin_panel
from states.checking_api_token_state import EditToken
from loader import get_current_message_id
from utils.services_api.lolzteam_api import initialize_market, check_lolzteam_connection
from utils.services_api.proxy6_api import get_balance, check_proxy6_api_connection

router = Router()


@router.callback_query(F.data == "lolzteam_service", IsAdmin())
async def lolzteam_button(call: types.CallbackQuery):
    print(check_lolzteam_connection())
    if check_lolzteam_connection():
        balance = initialize_market().profile.get().json()["user"]["balance"]
        await bot.edit_message_text(text=f"API токен: {get_lolz_token()}\nБаланс: {balance}", chat_id=call.from_user.id,
                                    message_id=get_current_message_id(call.from_user.id),
                                    reply_markup=lolzteam_keyboard)
    else:
        error_description = None
        try:
            error_description = initialize_market().profile.get().json()['error_description']
        except KeyError:
            pass
        await bot.edit_message_text(text=f"Ошибка: {error_description}", chat_id=call.from_user.id,
                                    message_id=get_current_message_id(call.from_user.id),
                                    reply_markup=lolzteam_keyboard)
    await call.answer()


@router.callback_query(F.data == "proxy6_service", IsAdmin())
async def proxy6_button(call: types.CallbackQuery):
    if check_proxy6_api_connection():
        balance = get_balance()
        await bot.edit_message_text(text=f"API токен: {get_proxy_token()}\nБаланс: {balance}", chat_id=call.from_user.id,
                                    message_id=get_current_message_id(call.from_user.id),
                                    reply_markup=proxy6_keyboard)
    else:
        await bot.edit_message_text(text=f"Ошибка подключения к сервису. Проверьте токен.",
                                    chat_id=call.from_user.id,
                                    message_id=get_current_message_id(call.from_user.id),
                                    reply_markup=proxy6_keyboard)
    await call.answer()


@router.callback_query(F.data == "telegram_service", IsAdmin())
async def telegram_api_button(call: types.CallbackQuery):
    await bot.edit_message_text(text=f"API id: {get_tg_api_id()}\nAPI hash: {get_tg_api_hash()}",
                                chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=tg_api_keyboard)
    await call.answer()


@router.callback_query(F.data == "lolz_change_token", IsAdmin())
async def start_editing_lolz_token(call: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(text="Введите новый токен",
                                chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=back_button_keyboard)
    await state.set_state(EditToken.LolzEditToken)
    await call.answer()


@router.message(EditToken.LolzEditToken, IsAdmin())
async def lolz_token_from_message(message: types.Message, state: FSMContext):
    token = message.text
    if check_lolzteam_connection(token):
        with open("data/api_data.json", "r") as jsonFile:
            data = json.load(jsonFile)
            data["LOLZ_TOKEN"] = token
        with open("data/api_data.json", "w") as jsonFile:
            json.dump(data, jsonFile)
        await state.clear()

        await bot.edit_message_text(text="Токен LOLZTEAM API изменен",
                                    chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
    else:
        await bot.edit_message_text(text="Неверный или неактивный токен, попробуйте еще раз",
                                    chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)


@router.callback_query(F.data == "proxy6_change_token", IsAdmin())
async def start_editing_proxy6_api_token(call: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(text="Введите новый токен",
                                chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=back_button_keyboard)
    await state.set_state(EditToken.ProxyEditToken)
    await call.answer()


@router.message(EditToken.ProxyEditToken, IsAdmin())
async def proxy6_token_from_message(message: types.Message, state: FSMContext):
    token = message.text
    if check_proxy6_api_connection(token):
        with open("data/api_data.json", "r") as jsonFile:
            data = json.load(jsonFile)
            data["PROXY_TOKEN"] = token
        with open("data/api_data.json", "w") as jsonFile:
            json.dump(data, jsonFile)
        await state.clear()
        await bot.edit_message_text(text="Токен Proxy6 API изменен",
                                    chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
    else:
        await bot.edit_message_text(text="Неверный или неактивный токен, попробуйте еще раз",
                                    chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
