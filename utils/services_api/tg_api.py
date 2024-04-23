import asyncio
import logging
import re
from datetime import datetime, timezone, timedelta
from random import randint

from telethon import TelegramClient
from telethon.errors import PeerFloodError
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import InputPeerUserFromMessage, InputPeerUser, User

from data.config import get_tg_api_id, get_tg_api_hash, ADMIN_NAMES, ADMINS
from loader import get_admin_panel, db_helper, bot
from utils.admin_panel import AdminPanel
from utils.files_rw import get_groups, get_keywords, save_admin_panel


def check_words_in_string(word_list, input_string):
    pattern = r'\b(?:{})\b'.format('|'.join(map(re.escape, word_list)))
    return bool(re.search(pattern, input_string))


async def check_valid(session, proxy=None, use_ipv6=False):
    client = TelegramClient(StringSession(session),
                            get_tg_api_id(),
                            get_tg_api_hash(),
                            proxy=proxy,
                            use_ipv6=use_ipv6
                            )
    try:
        await client.connect()
        account = await client.get_me()
        await client.disconnect()
        if account:
            return True
        else:
            return False
    except Exception as err:
        print(err)
        return False


def get_client(admin_panel):
    client = TelegramClient(StringSession(admin_panel.current_session),
                            get_tg_api_id(),
                            get_tg_api_hash(),
                            proxy=admin_panel.current_proxy,
                            use_ipv6=admin_panel.use_ipv6
                            )
    return client


async def join_groups():
    admin_panel = get_admin_panel()
    client = TelegramClient(StringSession(admin_panel.current_session),
                            get_tg_api_id(),
                            get_tg_api_hash(),
                            proxy=admin_panel.current_proxy,
                            use_ipv6=admin_panel.use_ipv6
                            )
    await client.connect()
    groups = get_groups()
    print(groups)
    for i in range(len(groups)):
        try:
            request_result = await client(ResolveUsernameRequest(groups[i]))
            print(request_result)
            print(await client(JoinChannelRequest(channel=request_result.peer.channel_id)))
        except Exception as e:
            print(e)

    await client.disconnect()


async def make_realtime_parsing_iteration(admin_panel, users):
    client = get_client(admin_panel)
    await client.connect()
    dialogs = await client.get_dialogs()
    keywords = get_keywords()
    for i in range(len(dialogs)):
        if isinstance(dialogs[i], User):
            continue
        iter_msg = client.iter_messages(entity=dialogs[i], reverse=True,
                                        offset_date=(datetime.now(
                                            tz=timezone.utc) - timedelta(minutes=1)
                                                     ))
        async for message in iter_msg:
            sender = await message.get_sender()
            try:
                if sender and message.text and not sender.bot:
                    msg_text = ("".join(char for char in message.text if char.isalnum() or char == ' ')
                                .lower())
                    match = check_words_in_string(keywords, msg_text)
                    if match:
                        try:
                            users[sender.id] = sender.username
                            print(sender)

                            result = db_helper.add_user(
                                user_id=int(sender.id),
                                username=users[sender.id],
                                chat_from=dialogs[i].entity.username,
                                msg_id_chat_from=message.id,
                                access_hash=sender.access_hash
                            )
                            if isinstance(result, Exception):
                                result = db_helper.update_user(
                                    user_id=int(sender.id),
                                    username=users[sender.id],
                                    chat_from=dialogs[i].entity.username,
                                    msg_id_chat_from=message.id,
                                    access_hash=sender.access_hash
                                )
                            if isinstance(result, Exception):
                                pass

                        except Exception as err:
                            logging.error(err)
                    admin_panel = get_admin_panel()
                    if not admin_panel.get_parsing_status():
                        break
            except Exception as err:
                logging.error(err)
                continue
            if not admin_panel.get_parsing_status():
                break
        if not admin_panel.get_parsing_status():
            break
    await client.disconnect()
    await notify_admins_parsing_iteration(users)


async def make_past_time_parsing_iteration(admin_panel: AdminPanel, users: dict):
    client = get_client(admin_panel)
    await client.connect()
    dialogs = await client.get_dialogs()
    keywords = get_keywords()
    for i in range(len(dialogs)):
        if isinstance(dialogs[i], User):
            continue
        temp_users = dict()
        for keyword in keywords:
            iter_msg = client.iter_messages(entity=dialogs[i], search=keyword)
            async for message in iter_msg:
                sender = await message.get_sender()
                try:
                    if not (sender and message.text and not sender.bot):
                        continue
                    temp_users[sender.id] = sender.username
                    result = db_helper.add_user(
                        user_id=int(sender.id),
                        username=temp_users[sender.id],
                        chat_from=dialogs[i].entity.username,
                        msg_id_chat_from=message.id,
                        access_hash=sender.access_hash
                    )
                    if isinstance(result, Exception):
                        result = db_helper.update_user(
                            user_id=int(sender.id),
                            username=temp_users[sender.id],
                            chat_from=dialogs[i].entity.username,
                            msg_id_chat_from=message.id,
                            access_hash=sender.access_hash
                        )
                    if isinstance(result, Exception):
                        pass
                except Exception as err:
                    logging.error(err)
                admin_panel = get_admin_panel()
                if not admin_panel.get_parsing_status():
                    break
            if not admin_panel.get_parsing_status():
                break
            users = {**users, **temp_users}
        if not admin_panel.get_parsing_status():
            break
    await notify_admins_parsing_iteration(users)
    await client.disconnect()
    admin_panel.set_parsing_status(False)
    admin_panel.set_parsing_params(None)
    save_admin_panel(admin_panel)


async def auto_parse_users(interval=5):
    while True:
        users = dict()
        try:
            await asyncio.sleep(interval)
            admin_panel = get_admin_panel()
            if admin_panel.get_parsing_status():
                if await check_valid(admin_panel.get_current_session(), admin_panel.get_current_proxy()):
                    params = admin_panel.get_parsing_params()
                    if params['type'] == 'realtime':
                        await make_realtime_parsing_iteration(admin_panel=admin_panel, users=users)
                        await asyncio.sleep(60)
                    elif params['type'] == 'past_time':
                        await make_past_time_parsing_iteration(admin_panel, users)
                else:
                    await notify_admins_not_valid()
                    admin_panel.set_parsing_status(False)
                    save_admin_panel(admin_panel)
        except Exception as err:
            if users:
                await notify_admins_parsing_iteration(users)
            logging.error(err)


async def try_send_message_to_user(user, client, admin_panel, success_sent, errors_count):
    if user[5] == 0:
        logging.info(f"Попытка отправки {user[0]}")

        try:
            if user[1]:
                await client.send_message(
                    entity=await client(ResolveUsernameRequest(user[1])),
                    message=admin_panel.generate_message()
                )
            else:
                peer = InputPeerUserFromMessage(
                    user_id=user[0],
                    msg_id=user[3],
                    peer=await client.get_input_entity(await client(ResolveUsernameRequest(user[2])))
                )
                await client(
                    SendMessageRequest(
                        peer=peer,
                        message=admin_panel.generate_message()
                    )
                )
            db_helper.update_user_status_db(user[0], True)
            admin_panel.increment_messages_sent()
            save_admin_panel(admin_panel)
            success_sent[user[0]] = user[1]
            logging.info(f"Отправлено сообщение пользователю {user[0]}")
        except PeerFloodError as err:
            logging.error(err)
            logging.info(f'Ошибка отправки {user[0]}')
            errors_count += 1
            return errors_count
        except Exception as err:
            logging.error(err)
            logging.info(f'Ошибка отправки {user[0]}')
            try:
                peer = InputPeerUser(
                    user_id=user[0],
                    access_hash=user[4]
                )
                await client(
                    SendMessageRequest(
                        peer=peer,
                        message=admin_panel.generate_message()
                    )
                )
            except PeerFloodError as err:
                logging.error(err)
                logging.info(f'Ошибка отправки {user[0]}')
                errors_count += 1
                return errors_count
            except Exception as err:
                logging.error(err)
                logging.info(f'Ошибка отправки {user[0]}')
    return errors_count


async def auto_mass_sending(interval=5):
    while True:
        try:
            await asyncio.sleep(interval)
            admin_panel = get_admin_panel()
            delay_min, delay_max = admin_panel.get_delay()
            if admin_panel.get_sending_status():
                if await check_valid(admin_panel.get_current_session(), admin_panel.get_current_proxy()):
                    if await check_can_send_messages() or True:
                        client = get_client(admin_panel)
                        await client.connect()
                        users = db_helper.select_all_users()
                        errors_count = 0
                        prematurely_ended = False
                        success_sent = dict()
                        for user in users:
                            if not get_admin_panel().get_sending_status():
                                break
                            admin_panel = get_admin_panel()
                            if not await check_valid(admin_panel.get_current_session(),
                                                     admin_panel.get_current_proxy()):
                                await notify_admins_banned()
                                break
                            if not get_admin_panel().get_sending_status():
                                break
                            admin_panel = get_admin_panel()
                            if not await check_valid(admin_panel.get_current_session(),
                                                     admin_panel.get_current_proxy()):
                                await notify_admins_banned()
                                break
                            if user[5] == 0:
                                logging.info(f"Попытка отправки {user[0]}")

                                errors_count = await try_send_message_to_user(user, client, admin_panel,
                                                                              success_sent, errors_count)
                                if errors_count == 5:
                                    prematurely_ended = True
                                    break

                                await asyncio.sleep(randint(delay_min, delay_max))
                        await notify_admins_sending_stopped(success_sent, prematurely_ended)
                    else:
                        await notify_admins_spamblock()
                else:
                    await notify_admins_not_valid()
                admin_panel = get_admin_panel()
                admin_panel.set_sending_status(False)
                save_admin_panel(admin_panel)
                print(f"Установлен статус рассылки {get_admin_panel().get_sending_status()}")
        except Exception as err:
            logging.error(err)


async def check_can_send_messages():
    admin_panel = get_admin_panel()
    client = TelegramClient(StringSession(admin_panel.current_session),
                            get_tg_api_id(),
                            get_tg_api_hash(),
                            proxy=admin_panel.current_proxy,
                            use_ipv6=admin_panel.use_ipv6
                            )
    await client.connect()
    try:
        receiver = await client(ResolveUsernameRequest(ADMIN_NAMES[0]))
        await client.send_message(receiver.peer, "Проверка на блок")
        await client.disconnect()
        return True
    except Exception as err:
        print(err)
        await client.disconnect()
        return False


async def auto_check_account(interval=(60 * 60)):
    while True:
        admin_panel = get_admin_panel()
        if await check_valid(admin_panel.get_current_session(), admin_panel.get_current_proxy()):
            if await check_can_send_messages():
                pass
            else:
                await notify_admins_spamblock()
        else:
            await notify_admins_not_valid()
        await asyncio.sleep(interval)


async def notify_admins_spamblock():
    for admin in ADMINS:
        try:
            await bot.send_message(admin,
                                   "Внимание! На аккаунте спамблок, требуется изменить аккаунт!")
        except Exception as err:
            logging.error(err)


async def notify_admins_not_valid():
    for admin in ADMINS:
        try:
            await bot.send_message(admin,
                                   "Внимание! Проблемы с доступом к аккаунту, проверьте аккаунт и прокси!")
        except Exception as err:
            logging.error(err)


async def notify_admins_sending_stopped(success_sent, prematurely_ended: bool = False):
    notification_text = ""
    if prematurely_ended:
        notification_text += ("Внимание\\! Рассылка завершена досрочно по причине ошибки Too Many Requests\n"
                              "Проверьте аккаунт на спамблок\\, \n"
                              "подождите какое\\-то время или увеличьте тайминги рассылки\n\n")
    if success_sent:
        notification_text += "Рассылка выполнена\nСообщения получили следующие пользователи\\:\n\n"
        for key in success_sent:
            if success_sent[key]:
                notification_text += f"[{key}](tg://user?id={key}): @{success_sent[key]}\n"
            else:
                notification_text += f"[{key}](tg://user?id={key})\n"
    else:
        notification_text += "Рассылка окончена, не было отправлено сообщений"
    for admin in ADMINS:
        try:
            await bot.send_message(admin, notification_text, parse_mode='MarkdownV2')
        except Exception as err:
            logging.error(err)


async def notify_admins_parsing_iteration(users):
    users_keys = list(users.keys())
    notification_text = f""
    if users:
        notification_text += f"Цикл парсинга выполнен\nДобавлены новые пользователи\n\n"
        for key in users_keys:
            if users[key]:
                notification_text += f"[{key}](tg://user?id={key}): @{users[key]}\n"
            else:
                notification_text += f"[{key}](tg://user?id={key})\n"
    else:
        notification_text += f"Цикл парсинга выполнен\nНовых пользователей не добавлено"
    for admin in ADMINS:
        try:
            await bot.send_message(admin, notification_text, parse_mode='MarkdownV2')
        except Exception as err:
            logging.error(err)


async def notify_admins_banned():
    for admin in ADMINS:
        try:
            await bot.send_message(admin, "Аккаунт забанен (проверьте прокси)")
        except Exception as err:
            logging.error(err)
