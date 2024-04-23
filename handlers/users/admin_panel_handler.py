from aiogram import Router, F, types, exceptions
from aiogram.fsm.context import FSMContext
from telethon import TelegramClient
from telethon.sessions import StringSession

from data.config import get_tg_api_id, get_tg_api_hash
from filters.is_admin import IsAdmin
from keyboards.inline.admin_panel_keyboard import get_keywords_keyboard, admin_panel_buttons, edit_message_buttons, \
    get_groups_keyboard, services_keyboard, get_services_keyboard, accounts_tg_keyboard, \
    proxy_keyboard, get_mass_sending_keyboard
from loader import bot, get_admin_panel, db_helper
from loader import get_current_message_id
from utils.services_api.tg_api import check_valid

router = Router()


@router.callback_query(F.data == "back_to_admin_panel", IsAdmin())
async def get_back_to_admin_panel(call: types.CallbackQuery, state: FSMContext):
    admin_panel = get_admin_panel()
    data = await state.get_data()
    bot_message = data.get("message")
    if bot_message:
        try:
            await bot.delete_message(chat_id=call.from_user.id, message_id=bot_message.message_id)
        except exceptions.TelegramBadRequest:
            pass
    await bot.edit_message_text(chat_id=call.from_user.id,
                                text=f"Отправлено сообщений всего: {admin_panel.get_messages_sent()}\n",
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=admin_panel_buttons)
    await state.clear()
    await call.answer()


@router.callback_query(F.data == "keywords.txt", IsAdmin())
async def keywords_button(call: types.CallbackQuery):
    admin_panel = get_admin_panel()
    await bot.edit_message_text(text="Ключевые слова", chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=get_keywords_keyboard())
    await call.answer()


@router.callback_query(F.data == "edit_message_keys", IsAdmin())
async def edit_message_button(call: types.CallbackQuery):
    admin_panel = get_admin_panel()
    await bot.edit_message_text(text=f"Текущее сообщение: \n{admin_panel.get_message_text()}\n\n"
                                     f"Пример случайно сгенерированного сообщения: \n{admin_panel.generate_message()}",
                                chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id), reply_markup=edit_message_buttons)
    await call.answer()


@router.callback_query(F.data == "groups_keys", IsAdmin())
async def groups_button(call: types.CallbackQuery):
    admin_panel = get_admin_panel()
    await bot.edit_message_text(text=f"Сообщества\nСостояние парсинга: {admin_panel.get_parsing_status()}",
                                chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=get_groups_keyboard())
    await call.answer()


@router.callback_query(F.data == "services", IsAdmin())
async def services_button(call: types.CallbackQuery):
    admin_panel = get_admin_panel()
    await bot.edit_message_text(text="Сервисы", chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=get_services_keyboard())
    await call.answer()


@router.callback_query(F.data == "accounts_tg", IsAdmin())
async def accounts_tg_button(call: types.CallbackQuery):
    text = ""
    admin_panel = get_admin_panel()
    if await check_valid(admin_panel.current_session, admin_panel.current_proxy, admin_panel.use_ipv6):
        client = TelegramClient(StringSession(admin_panel.current_session),
                                get_tg_api_id(),
                                get_tg_api_hash(),
                                proxy=admin_panel.current_proxy,
                                use_ipv6=admin_panel.use_ipv6
                                )
        await client.connect()
        user = await client.get_me()
        await client.disconnect()

        text += (f"Имя: {user.first_name}\nID: {user.id}\nАктивен: да\n\n"
                 f"Данные для входа (telethon session): {admin_panel.current_session}")
    else:
        f"Текущий аккаунт: {admin_panel.current_session}\n"
        text += "\nАктивен: нет (проверьте прокси)"
    await bot.edit_message_text(text=text, chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=accounts_tg_keyboard)
    await call.answer()


@router.callback_query(F.data == "mass_sending", IsAdmin())
async def mass_sending_button(call: types.CallbackQuery):
    admin_panel = get_admin_panel()
    users_count = len(db_helper.select_all_users())
    min_delay, max_delay = admin_panel.get_delay()
    await bot.edit_message_text(text=f"Состояние рассылки: {admin_panel.get_sending_status()}\n"
                                     f"Тайминги рассылки: от {min_delay} до "
                                     f"{max_delay} секунд\n"
                                     f"Примерное время рассылки: от {users_count * (min_delay + 2)} до"
                                     f" {users_count * max_delay} секунд",
                                chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=get_mass_sending_keyboard())
    await call.answer()


@router.callback_query(F.data == "proxy_keys", IsAdmin())
async def proxy_button(call: types.CallbackQuery):
    admin_panel = get_admin_panel()
    proxy = admin_panel.get_current_proxy()
    await bot.edit_message_text(text=f"Текущие прокси: \nАдрес: {proxy['addr']}:{proxy['port']}\n"
                                     f"Тип: {proxy['proxy_type']}\n"
                                     f"Логин: {proxy['username']}\n"
                                     f"Пароль: {proxy['password']}\n"
                                     f"ID: {admin_panel.get_current_proxy_id()}", chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=proxy_keyboard)
    await call.answer()
