import json

from environs import Env

env = Env()
env.read_env()

BOT_TOKEN: str = env.str("BOT_TOKEN")
ADMINS: list = env.list("ADMINS")
IP: str = env.str("ip")
ADMIN_NAMES = env.list("ADMIN_NAMES")


def get_lolz_token():
    with open("data/api_data.json", "r") as jsonFile:
        api_data = json.load(jsonFile)
        LOLZ_TOKEN = api_data["LOLZ_TOKEN"]
    return LOLZ_TOKEN


def get_proxy_token():
    with open("data/api_data.json", "r") as jsonFile:
        api_data = json.load(jsonFile)
        PROXY_TOKEN = api_data["PROXY_TOKEN"]
    return PROXY_TOKEN


def get_tg_api_id():
    with open("data/api_data.json", "r") as jsonFile:
        api_data = json.load(jsonFile)
        TG_API_ID = api_data["TG_API_ID"]
    return TG_API_ID


def get_tg_api_hash():
    with open("data/api_data.json", "r") as jsonFile:
        api_data = json.load(jsonFile)
        TG_API_HASH = api_data["TG_API_HASH"]
    return TG_API_HASH
