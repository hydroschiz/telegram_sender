import time

from LOLZTEAM import AutoUpdate
from LOLZTEAM import Constants
from LOLZTEAM.API import Forum, Market
from LOLZTEAM.Tweaks import DelaySync, SendAsAsync, CreateJob
from TGConvertor import SessionManager
from data.config import get_lolz_token


def initialize_market():
    market = Market(token=get_lolz_token(), language="en")
    return market


def get_last_purchased_login_data():
    market = initialize_market()
    purchased = market.list.purchased()
    last_purchased_data = purchased.json()["items"][0]["loginData"]
    auth_key = bytes.fromhex(last_purchased_data["login"])
    dc_id = int(last_purchased_data["password"])
    session = SessionManager.to_telethon_string(SessionManager(auth_key=auth_key, dc_id=dc_id))
    return session


def get_available_accounts(max_price: int | None = None):
    market = initialize_market()
    accounts = market.category.telegram.get(
        pmax=max_price,
        order_by="price_to_up",
        origin=[Constants.Market.ItemOrigin.autoreg],
        search_params={"spam": "no", "password": "no", "country[]": "US"}
    ).json()["items"]
    return accounts


def buy_account():
    market = initialize_market()
    time.sleep(4)
    accounts = get_available_accounts()
    time.sleep(4)
    response = market.purchasing.fast_buy(accounts[0]["item_id"], accounts[0]["price"])
    return response.json()


def check_lolzteam_connection(token=None):
    if not token:
        token = get_lolz_token()
    local_market = Market(token=token, language="en")
    response = local_market.profile.get().json()
    try:
        response['user']
    except KeyError:
        return False
    return True
