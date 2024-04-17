import os

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from loader import get_admin_panel

admin_panel_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Ключевые слова", callback_data="keywords.txt")
        ],
        [
            InlineKeyboardButton(text="Редактировать сообщение", callback_data="edit_message_keys")
        ],
        [
            InlineKeyboardButton(text="Сообщества", callback_data="groups_keys")
        ],
        [
            InlineKeyboardButton(text="Аккаунты тг", callback_data="accounts_tg")
        ],
        [
            InlineKeyboardButton(text="Прокси", callback_data="proxy_keys")
        ],
        [
            InlineKeyboardButton(text="Рассылка", callback_data="mass_sending")
        ],
        [
            InlineKeyboardButton(text="Сервисы", callback_data="services")
        ],
    ]
)

back_button_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_admin_panel")
        ]
    ]
)


def get_keywords_keyboard():
    keywords_buttons = []
    if os.path.exists("data/keywords.txt"):
        keywords_buttons.append([
            InlineKeyboardButton(text="Проверить", callback_data="check_keywords_file")
        ])
        keywords_buttons.append([
            InlineKeyboardButton(text="Изменить", callback_data="edit_keywords_file")
        ])
    else:
        keywords_buttons.append([
            InlineKeyboardButton(text="Создать", callback_data="create_keywords_file")
        ])
    keywords_buttons.append([
        InlineKeyboardButton(text="Назад", callback_data="back_to_admin_panel")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keywords_buttons)


def get_groups_keyboard():
    groups_buttons = []

    if os.path.exists("data/groups.txt"):
        groups_buttons.append([
            InlineKeyboardButton(text="Вступить в группы", callback_data="join_groups_button")
        ])
        groups_buttons.append([
            InlineKeyboardButton(text="Проверить", callback_data="check_groups_file")
        ])
        groups_buttons.append([
            InlineKeyboardButton(text="Изменить", callback_data="edit_groups_file")
        ])
        admin_panel = get_admin_panel()
        if not admin_panel.get_parsing_status():
            groups_buttons.append([
                InlineKeyboardButton(text="Начать парсинг", callback_data="start_parsing")
            ])
        else:
            groups_buttons.append([
                InlineKeyboardButton(text="Остановить парсинг", callback_data="stop_parsing")
            ])
    else:
        groups_buttons.append([
            InlineKeyboardButton(text="Создать файл с группами", callback_data="create_groups_file")
        ])
    groups_buttons.append([
        InlineKeyboardButton(text="Назад", callback_data="back_to_admin_panel")
    ])
    return InlineKeyboardMarkup(inline_keyboard=groups_buttons)


select_parsing_type_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Парсинг в реальном времени", callback_data="select_realtime_parsing")
        ],
        [
            InlineKeyboardButton(text="Парсинг предыдущих сообщений", callback_data="select_past_time_parsing")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_admin_panel")
        ]
    ]
)


edit_message_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Изменить сообщение для рассылки", callback_data="edit_message_button")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_admin_panel")
        ]
    ]
)

services_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Lolzteam Market", callback_data="lolzteam_service")
        ],
        [
            InlineKeyboardButton(text="Proxy6.net", callback_data="proxy6_service")
        ],
        [
            InlineKeyboardButton(text="Telegram API", callback_data="telegram_service")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_admin_panel")
        ]
    ]
)


def get_services_keyboard():
    return services_keyboard


lolzteam_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Изменить API токен", callback_data="lolz_change_token")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_admin_panel")
        ]
    ]
)

proxy6_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Изменить API токен", callback_data="proxy6_change_token")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_admin_panel")
        ]
    ]
)

tg_api_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        # [
        #     InlineKeyboardButton(text="Изменить API id", callback_data="tg_change_api_id")
        # ],
        # [
        #     InlineKeyboardButton(text="Изменить API hash", callback_data="tg_change_api_hash")
        # ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_admin_panel")
        ]
    ]
)

accounts_tg_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Купить новый аккаунт", callback_data="buy_new_tg_account")
        ],
        [
            InlineKeyboardButton(text="Проверить на спамблок", callback_data="check_spam_block")
        ],
        [
            InlineKeyboardButton(text="Ввести новые данные для входа вручную", callback_data="input_new_login_data_tg")
        ],
        [
            InlineKeyboardButton(text="Получить данные для ручного входа", callback_data="get_login_data_tg")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_admin_panel")
        ]
    ]
)

get_login_data_tg_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Auth Key + DC ID", callback_data="auth_key_get_login_data")
        ],
        [
            InlineKeyboardButton(text="Session file", callback_data="session_file_get_login_data")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_admin_panel")
        ]
    ]
)


def get_mass_sending_keyboard():
    keyboard = []
    admin_panel = get_admin_panel()
    if not admin_panel.get_sending_status():
        keyboard.append([
            InlineKeyboardButton(text="Выполнить рассылку", callback_data="start_mass_sending")
        ])
        keyboard.append([
            InlineKeyboardButton(text="Обнулить всех пользователей", callback_data="null_users_mass_sending")
        ])
        keyboard.append([
            InlineKeyboardButton(text="Показать всех пользователей", callback_data="show_users_mass_sending")
        ])
        keyboard.append([
            InlineKeyboardButton(text="Удалить всех пользователей", callback_data="delete_users_mass_sending")
        ])
        keyboard.append([
            InlineKeyboardButton(text="Настроить тайминги рассылки", callback_data="set_sending_timings")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton(text="Прервать рассылку", callback_data="stop_mass_sending")
        ])
    keyboard.append([
            InlineKeyboardButton(text="Назад", callback_data="back_to_admin_panel")
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


proxy_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Купить новые прокси", callback_data="buy_new_proxy")
        ],
        [
            InlineKeyboardButton(text="Просмотреть мои прокси", callback_data="get_proxy_list")
        ],
        [
            InlineKeyboardButton(text="Выбрать прокси из списка", callback_data="select_proxy_from_list")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_admin_panel")
        ]
    ]
)
