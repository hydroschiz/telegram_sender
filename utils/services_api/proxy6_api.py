import requests
from data.config import get_proxy_token


def get_base_url():
    base_url = f"https://proxy6.net/api/{get_proxy_token()}/"
    return base_url


def buy_proxy(version="3", country="us", period="30"):
    url = get_base_url() + f"buy?count=1&period={period}&country={country}&type=http&version={version}"
    response = requests.get(url).json()
    # actual_key = list(response["list"].keys())[0]
    return response


def get_proxy_by_key(key):
    url = get_base_url() + "getproxy"
    response = requests.get(url).json()
    proxy = response["list"][key]
    return proxy


def get_proxy_list():
    url = get_base_url() + "getproxy"
    return requests.get(url).json()


def get_balance():
    response = requests.get(get_base_url()).json()
    return response["balance"] + " " + response["currency"]


def check_proxy6_api_connection(token=get_proxy_token()):
    url = f"https://proxy6.net/api/{token}/"
    response = requests.get(url).json()
    if response["status"] == "yes":
        return True
    else:
        return False
