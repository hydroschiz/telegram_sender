from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from filters.is_admin import IsAdmin
from keyboards.inline.admin_panel_keyboard import back_button_keyboard
from loader import get_admin_panel, bot
from states.selecting_proxy_state import SelectProxy
from loader import get_current_message_id
from utils.files_rw import save_admin_panel
from utils.services_api.proxy6_api import get_proxy_list, buy_proxy

router = Router()


@router.callback_query(F.data == "get_proxy_list", IsAdmin())
async def show_proxy_list(call: types.CallbackQuery):
    proxy_list = get_proxy_list()["list"]
    text = ""
    if proxy_list:
        keys = list(proxy_list.keys())
        for key in keys:
            text += (f"ID: {key}\n"
                     f"Адрес: {proxy_list[key]['host']}:{proxy_list[key]['port']}\n"
                     f"Тип: {proxy_list[key]['type']}\n"
                     f"Логин: {proxy_list[key]['user']}\n"
                     f"Пароль: {proxy_list[key]['pass']}\n"
                     f"Страна: {proxy_list[key]['country']}\n"
                     f"Активно: {bool(int(proxy_list[key]['active']))}\n\n\n")
    else:
        text += "Список пуст"
    await bot.edit_message_text(text=text, chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=back_button_keyboard)


@router.callback_query(F.data == "buy_new_proxy", IsAdmin())
async def buy_new_proxy(call: types.CallbackQuery):
    response = buy_proxy()
    if response["status"] == "yes":
        await bot.edit_message_text(text="Новые прокси успешно куплены", chat_id=call.from_user.id,
                                    message_id=get_current_message_id(call.from_user.id),
                                    reply_markup=back_button_keyboard)
    elif response["status"] == "no":
        await bot.edit_message_text(text=f"Ошибка: {response['error']}", chat_id=call.from_user.id,
                                    message_id=get_current_message_id(call.from_user.id),
                                    reply_markup=back_button_keyboard)


@router.callback_query(F.data == "select_proxy_from_list", IsAdmin())
async def start_selecting_proxy(call: types.CallbackQuery, state: FSMContext):
    proxy_list = get_proxy_list()["list"]
    if proxy_list:
        await bot.edit_message_text(text="Введите ID прокси", chat_id=call.from_user.id,
                                    message_id=get_current_message_id(call.from_user.id),
                                    reply_markup=back_button_keyboard)
        await state.set_state(SelectProxy.SelectProxy)
    else:
        await bot.edit_message_text(text="Список пуст", chat_id=call.from_user.id,
                                    message_id=get_current_message_id(call.from_user.id),
                                    reply_markup=back_button_keyboard)


@router.message(SelectProxy.SelectProxy)
async def select_proxy(message: types.Message, state: FSMContext):
    admin_panel = get_admin_panel()
    proxy_list = get_proxy_list()["list"]
    proxy_id = message.text
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    try:
        proxy_raw = proxy_list[proxy_id]
        print(proxy_raw)
        type = proxy_raw['type']
        if type == "socks":
            type += "5"
        proxy = {
                                'proxy_type': type,
                                'addr': proxy_raw['host'],
                                'port': int(proxy_raw['port']),
                                'username': proxy_raw['user'],
                                'password': proxy_raw['pass'],
                                'rdns': True
                        }
        admin_panel.set_current_proxy(proxy)
        admin_panel.set_current_proxy_id(proxy_id)
        save_admin_panel(admin_panel)
        await bot.edit_message_text(text="Новые прокси установлены",
                                    chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
        await state.clear()
    except KeyError:
        await bot.edit_message_text(text="В списке нет прокси с таким ID, попробуйте еще раз",
                                    chat_id=message.from_user.id,
                                    message_id=get_current_message_id(message.from_user.id),
                                    reply_markup=back_button_keyboard)
