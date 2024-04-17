import os.path

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from data import config
from utils.admin_panel import AdminPanel
from utils.db_api.sqlite import DatabaseHelper
from utils.files_rw import load_admin_panel, save_admin_panel

bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


db_helper = DatabaseHelper()


def get_admin_panel():
    if os.path.exists("data/admin_panel.pickle"):
        admin_panel = load_admin_panel()
    else:
        admin_panel = AdminPanel()
        save_admin_panel(admin_panel)
    return admin_panel


def get_current_message_id(admin_id):
    return db_helper.get_admin(admin_id)[1]



