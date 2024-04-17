import random
import re


class AdminPanel:
    def __init__(self):
        self.messages_sent = 0
        self.message_text = "Привет, хочу предложить (вам|тебе) (работу|заработок|подработку)"
        self.parsing_is_active = False
        self.mass_sending_is_active = False
        self.current_session = "1BJWap1sBu69EixpGSzCgbrcR9sxvYcQZ9gkN_fGl1St4qNpT-hewevtqlGJ3CmxcBfa2n9U50WEbCqciEGh3ksbFVcOQ5uLrm3atAsgNsKfJBjHg3hESzHAfvT3hs-5mnqr2qVdS2MGmS2Y_sQeHBN2daQdpFX_T1bj2-eET1R113AsrMSBXoGQNZ6XmuqW4cteb-8unbpQTB4JvQPO2wXn98_vQQVJOoQVJ8hik3sYDao_nfhgSCxm4XicFYXMnIYjKUL9lxe-VjW3kL8_GQu9eqJKS8rJ8h5-TT77qTuQlPon3mureU37l_sBq7DmB5QjNLOXT2WIIedkOxB4tK_nlPFQh_4k="
        self.current_proxy = {
                                'proxy_type': 'http',
                                'addr': "38.152.246.11",
                                'port': 9027,
                                'username': "q9ck6T",
                                'password': "9NsqZQ",
                                'rdns': True
                        }
        self.use_ipv6 = False
        self.delay = (0, 60)
        self.current_proxy_id = "26642759"
        self.parsing_params = dict()

    def increment_messages_sent(self):
        self.messages_sent += 1

    def get_messages_sent(self):
        return self.messages_sent

    def set_current_session(self, new_session):
        self.current_session = new_session

    def get_current_session(self):
        return self.current_session

    def set_message_text(self, text: str):
        self.message_text = text

    def get_message_text(self):
        return self.message_text

    def get_current_proxy(self):
        return self.current_proxy

    def set_current_proxy(self, proxy):
        self.current_proxy = proxy

    def get_current_proxy_id(self):
        return self.current_proxy_id

    def set_current_proxy_id(self, proxy_id):
        self.current_proxy_id = proxy_id

    def get_parsing_status(self):
        return self.parsing_is_active

    def set_parsing_status(self, status):
        self.parsing_is_active = status

    def get_parsing_params(self):
        return self.parsing_params

    def set_parsing_params(self, parsing_params):
        self.parsing_params = parsing_params

    def get_sending_status(self):
        return self.mass_sending_is_active

    def set_sending_status(self, status):
        self.mass_sending_is_active = status

    def generate_message(self):
        subs = re.findall(r"\([^)]+\)", self.get_message_text())
        edited_message = self.get_message_text()
        for sub in subs:
            edited_message = edited_message.replace(sub, random.choice(sub[1:len(sub) - 1].split('|')).strip())
        return edited_message

    def get_delay(self):
        return self.delay

    def set_delay(self, min_delay, max_delay):
        self.delay = (min_delay, max_delay)
