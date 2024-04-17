import asyncio
import logging
import sys
import datetime as dt

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler(f"data/logging/{dt.date.today()}.log", "a+", encoding="utf-8")
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)


from handlers.users import commands, admin_panel_handler, services_keyboard_handler, groups_keyboard_handler, \
    keywords_keyboard_handler, edit_message_keyboard_handler, tg_accounts_keyboard_handler, \
    mass_sending_keyboard_handler, proxy_keyboard_handler
from loader import dp, bot, db_helper, get_admin_panel
from utils.services_api.tg_api import auto_mass_sending, auto_parse_users, auto_check_account


def on_startup():
    task_sending = asyncio.create_task(auto_mass_sending())
    task_parsing = asyncio.create_task(auto_parse_users())
    task_check_account = asyncio.create_task(auto_check_account())
    get_admin_panel()
    return task_sending, task_parsing, task_check_account


async def main() -> None:
    dp.include_routers(
        commands.router,
        admin_panel_handler.router,
        groups_keyboard_handler.router,
        services_keyboard_handler.router,
        keywords_keyboard_handler.router,
        edit_message_keyboard_handler.router,
        tg_accounts_keyboard_handler.router,
        mass_sending_keyboard_handler.router,
        proxy_keyboard_handler.router
    )
    get_admin_panel()
    result = db_helper.create_table_users()
    if isinstance(result, Exception):
        logging.error(result)
    result = db_helper.create_table_admins()
    if isinstance(result, Exception):
        logging.error(result)
    await dp.start_polling(bot,
                           on_startup=on_startup()
                           )


if __name__ == "__main__":
    asyncio.run(main())
