import re
import html
import logging
import os
import json

from wechaty import (
    Contact,
    FileBox,
    Message,
    Wechaty,
    ScanStatus,
)

from wechaty_puppet import (
    # FileBox,
    # MessagePayload,
    # MessageQueryFilter,
    MessageType,
    # get_logger
)

from clickhouse_driver import Client

from config import config

chclient = None

logger = logging.getLogger('chatsum.wechaty')


async def handle_message(msg: Message):
    global outfile, outfile_datestr

    # 现在只处理 text, url 消息
    if msg.message_type() not in [
        MessageType.MESSAGE_TYPE_TEXT,
        MessageType.MESSAGE_TYPE_URL,
    ]:
        return

    # 存一下方便后面调用
    talker = msg.talker()
    await talker.ready()
    # to_contact = msg.to()
    # await to_contact.ready()
    room = msg.room()
    if room:
        await room.ready()


    # 文本格式整理，主要问题
    # 1. 用 re 处理引用消息的情况
    # 2. 替换 " 和 \n
    if msg.message_type() == MessageType.MESSAGE_TYPE_TEXT:
        msgtype = 'text'
        text = msg.text()
        quote_user = ''
        quote_text = ''
        restr = r'「(.+)：([\s\S]+)」\n[- ]+\n([\s\S]+)'
        match = re.fullmatch(restr, text)
        if match is not None:
            quote_user, quote_text, text = match.groups()
            # 还有可能是对引用的引用，处理的不全，不处理了
            # restr = r'[\s\S]*<msg>\s*<appmsg appid="" sdkver="0">\s*<title>([\s\S]+?)<\/title>\s*<des'
            # match = re.match(restr, quote_text)
            # if match is not None:
            #     quote_text = html.unescape(match.groups()[0])
            
            # 重组 text
            # text = f'{text} @{quote_user}:{quote_text}'
    elif msg.message_type() == MessageType.MESSAGE_TYPE_URL:
        msgtype = 'url'
        urllink = await msg.to_url_link()
        data = {
            'title': urllink.title,
            'description': urllink.description,
            'url': urllink.url,
            'thumbnail': urllink.thumbnailUrl,
        }
        text = json.dumps(data)
        quote_user = ''
        quote_text = ''

    # talker_id = talker.contact_id
    # talker_name = talker.payload.name
    # room_id = room.room_id if room else ''
    # room_name = room.payload.topic if room else ''
    # logger.debug(f'{talker_id=}, {talker_name=}, {room_id=}, {room_name=}, '
    #              f'{msgtype=}, '
    #              f'{text=}, {quote_user=}, {quote_text=}')
    
    outlist = [
        msg.date(),
        talker.contact_id,
        talker.payload.name,
        '', # to_contact.contact_id if to_contact else '',
        '', # to_contact.payload.name if to_contact else '',
        room.room_id if room else '',
        room.payload.topic if room else '',
        msgtype,
        text,
        quote_user,
        quote_text
    ]

    chclient.execute(
        f'INSERT INTO {config["clickhouse_table"]} '
        '(dt, sender_id, sender_name, to_id, to_name, room_id, room_name, msg_type, text, quoted_username, quoted_text) '
        'VALUES', [outlist])



async def on_message(msg: Message):
    """
    Message Handler for the Bot
    """
    logger.info(str(msg))
    try:
        await handle_message(msg)
    except Exception as e:
        logger.exception('on_message exception')
        if msg.message_type() == MessageType.MESSAGE_TYPE_TEXT:
            logger.debug(f'on_message exception text: {msg.text()}')


async def on_scan(
        qrcode: str,
        status: ScanStatus,
        _data,
):
    """
    Scan Handler for the Bot
    """
    logger.info(f'{status=}')
    # logger.info('View QR Code Online: https://wechaty.js.org/qrcode/' + quote(qrcode))


async def on_login(user: Contact):
    """
    Login Handler for the Bot
    """
    logger.info(str(user))


def create_database():
    sql = f"""
    CREATE TABLE IF NOT EXISTS {config['clickhouse_table']}
    (
        dt DateTime,
        sender_id String,
        sender_name String,
        to_id String,
        to_name String,
        room_id String,
        room_name String,
        msg_type String,
        text String,
        quoted_username String,
        quoted_text String,
    ) ENGINE = MergeTree()
    ORDER BY dt;
    """
    chclient.execute(sql)

async def main():
    global chclient

    chclient = Client(
        'localhost', port=config['clickhouse_port'],
        user=config['clickhouse_user'], password=config['clickhouse_password'])
    
    create_database()

    """
    Async Main Entry
    """
    #
    # Make sure we have set WECHATY_PUPPET_SERVICE_TOKEN in the environment variables.
    # Learn more about services (and TOKEN) from https://wechaty.js.org/docs/puppet-services/
    #
    # It is highly recommanded to use token like [paimon] and [wxwork].
    # Those types of puppet_service are supported natively.
    # https://wechaty.js.org/docs/puppet-services/paimon
    # https://wechaty.js.org/docs/puppet-services/wxwork
    # 
    # Replace your token here and umcommt that line, you can just run this python file successfully!
    # os.environ['token'] = 'puppet_paimon_your_token'
    # os.environ['token'] = 'puppet_wxwork_your_token'
    #     
    if 'WECHATY_PUPPET_SERVICE_TOKEN' not in os.environ:
        print('''
            Error: WECHATY_PUPPET_SERVICE_TOKEN is not found in the environment variables
            You need a TOKEN to run the Python Wechaty. Please goto our README for details
            https://github.com/wechaty/python-wechaty-getting-started/#wechaty_puppet_service_token
        ''')

    bot = Wechaty()

    bot.on('scan',      on_scan)
    bot.on('login',     on_login)
    bot.on('message',   on_message)

    await bot.start()

    # print('[Python Wechaty] Ding Dong Bot started.')