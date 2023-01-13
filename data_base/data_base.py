import sqlite3 as sq
from asyncio import sleep as asleep
from loguru_bot.logs import logger
from datetime import timedelta, datetime

from create_bot import bot
from config import ID_PRIVATE_CHANNEL, ADMINS

base = sq.connect('./data_base/base.db')
cur = base.cursor()

PHOTO = 'https://disk.yandex.ru/i/kNVtOWXrzGsXDA'


def sql_start() -> None:
    base.execute('''CREATE TABLE IF NOT EXISTS users(id_user INT PRIMARY KEY,
                                                     date_join TEXT,
                                                     date_out TEXT DEFAULT NULL,
                                                     status TEXT DEFAULT NULL,
                                                     contact_buy DEFAULT NULL,
                                                     money INT DEFAULT 0)''')
    base.execute('''CREATE TABLE IF NOT EXISTS price_list(label TEXT PRIMARY KEY,
                                                          name TEXT DEFAULT Имя,
                                                          price INT DEFAULT 10000,
                                                          title TEXT DEFAULT Заголовок,
                                                          description TEXT DEFAULT Описание)''')
    base.execute(f'''CREATE TABLE IF NOT EXISTS cover(label TEXT PRIMARY KEY,
                                                      name TEXT DEFAULT Имя,
                                                      caption TEXT DEFAULT Описание,
                                                      photo TEXT DEFAULT 'https://disk.yandex.ru/i/kNVtOWXrzGsXDA')''')
    base.execute(f'''CREATE TABLE IF NOT EXISTS bill(id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                                     user_id INT, 
                                                     bill_id TEXT,
                                                     date TEXT)''')
    base.execute(f'''CREATE TABLE IF NOT EXISTS quick(id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                                      user_id INT,
                                                      quick_id TEXT,
                                                      date TEXT)''')
    base.execute(f'''CREATE TABLE IF NOT EXISTS links(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                      name TEXT,
                                                      link TEXT,
                                                      channel INT,
                                                      time TEXT)''')
    for label in ('sub', 'contact', 'present1', 'present2', 'present3', 'present4'):
        base.execute('''INSERT OR IGNORE INTO price_list(label) VALUES (?)''', (label,))
    for label in ('tariffs', 'sub', 'contact', 'present', 'about', 'start'):
        base.execute('''INSERT OR IGNORE INTO cover(label) VALUES (?)''', (label,))
    base.commit()


async def add_link(name, link, channel, time):
    cur.execute('INSERT INTO links(name, link, channel, time) VALUES (?, ?, ?, ?)',
                (name, link, channel, time))
    base.commit()


async def select_links(channel):
    links = cur.execute('SELECT * FROM links WHERE channel = ?', (channel,)).fetchall()
    base.commit()
    return links


async def select_link(id_link):
    link = cur.execute('SELECT * FROM links WHERE id = ?', (id_link,)).fetchone()
    base.commit()
    return link[2]


async def del_links(id_link):
    cur.execute('DELETE FROM links WHERE id = ?', (id_link,))
    base.commit()


async def count_link(link):
    cur.execute('UPDATE links SET count = count + 1 WHERE link = ?', (link,))
    base.commit()


async def add_bill(user_id, bill):
    cur.execute('INSERT INTO bill(user_id, bill_id, date) VALUES (?, ?, ?)',
                (user_id, bill, datetime.now()))
    base.commit()


async def check_bill(bill):
    result = cur.execute('SELECT * FROM bill WHERE bill_id = ?', (bill,)).fetchone()
    base.commit()
    if not result:
        return False
    return result[0]


async def del_bill(bill):
    cur.execute('DELETE FROM bill WHERE bill_id = ?', (bill,))
    base.commit()


async def add_quick(user_id, quick):
    cur.execute('INSERT INTO quick(user_id, quick_id, date) VALUES (?, ?, ?)',
                (user_id, quick, datetime.now()))
    base.commit()


async def check_quick(quick):
    result = cur.execute('SELECT * FROM quick WHERE quick_id = ?', (quick,)).fetchone()
    base.commit()
    if not result:
        return False
    return result[0]


async def del_quick(quick):
    cur.execute('DELETE FROM quick WHERE quick_id = ?', (quick,))
    base.commit()


async def cover(label) -> dict:
    data = cur.execute('SELECT * FROM cover WHERE label = ?', (label,)).fetchone()
    cover_data = dict(zip(('label', 'name', 'caption', 'photo'), data))
    base.commit()
    return cover_data


async def edit_cover(state):
    async with state.proxy() as data:
        if data['label'] in ['about', 'start']:
            cur.execute('UPDATE cover SET caption = ? WHERE label = ?', (data['text'], data['label']))
        else:
            cur.execute('UPDATE cover SET caption = ?, photo = ? WHERE label = ?',
                        (data['caption'], data['photo'], data['label']))
    base.commit()


async def price_list(label) -> dict:
    price = cur.execute('SELECT * FROM price_list WHERE label = ?', (label,)).fetchone()
    list_price = dict(zip(('label', 'name', 'price', 'title', 'description'), price))
    base.commit()
    return list_price


async def edit_price(state):
    async with state.proxy() as data:
        cur.execute('UPDATE price_list SET price = ?, title = ?, description = ? WHERE label = ?',
                    (data['price'], data['title'], data['description'], data['label']))
    base.commit()


async def add_bd_user(user_id):
    cur.execute('''INSERT INTO users(id_user, date_join) VALUES (?, ?)''',
                (user_id, datetime.now()))
    base.commit()


async def bd_user(user_id) -> dict:
    user = cur.execute('SELECT * FROM users WHERE id_user = ?', (user_id,)).fetchone()
    base.commit()
    data = dict()
    if user:
        data = dict(zip(('id_user', 'date_join', 'date_out', 'status', 'contact_buy', 'money'), user))
    return data


async def buy_sub(user_id) -> None:
    month = datetime.now() + timedelta(days=30)
    user = cur.execute('SELECT * FROM users WHERE id_user = ?', (user_id,)).fetchone()
    price = await price_list('sub')
    if not user:
        cur.execute('''INSERT INTO users(id_user, date_join, date_out, status, money) 
                       VALUES (?, ?, ?, ?, ?)''',
                    (user_id, datetime.now(), month, 'active', price['price']))
    else:
        if user[3] != 'active':
            cur.execute('UPDATE users SET date_out = ?, status = ?, money = ? WHERE id_user = ?',
                        (month, 'active', user[5] + price['price'], user_id))
        else:
            date_out = datetime.strptime(user[2], '%Y-%m-%d %H:%M:%S.%f') + timedelta(days=30)
            cur.execute('UPDATE users SET date_out = ?, money = ? WHERE id_user = ?',
                        (date_out, user[5] + price['price'], user_id))
    base.commit()


async def buy_contact(user_id):
    user = cur.execute('SELECT * FROM users WHERE id_user = ?', (user_id,)).fetchone()
    price = await price_list('contact')
    if not user:
        cur.execute('''INSERT INTO users(id_user, date_join, contact_buy, money) 
                       VALUES (?, ?, ?, ?)''',
                    (user_id, datetime.now(), 'active', price['price']))
    else:
        cur.execute('UPDATE users SET contact_buy = ?, money = ? WHERE id_user = ?',
                    ('active', user[5] + price['price'], user_id))
    base.commit()


@logger.catch()
async def check_sub_time(time) -> None:
    while True:
        for user in cur.execute('SELECT * FROM users WHERE status = "active"').fetchall():
            if user[0] in ADMINS:
                continue
            date_time_end_sub = datetime.strptime(user[2], '%Y-%m-%d %H:%M:%S.%f')
            if datetime.now() > date_time_end_sub:
                await del_user(user[0])
                logger.info(f"Kick user private chat User: {user[0]} Data: {user[1:]}")
                try:
                    await bot.send_message(chat_id=user[0],
                                           text=f"Ваша подписка закончилась",
                                           protect_content=True)
                except Exception as error:
                    print(error)
                continue
            if (datetime.now() + timedelta(hours=24)) >= date_time_end_sub > (datetime.now() + timedelta(hours=23)) \
                    or (datetime.now() + timedelta(hours=8)) >= date_time_end_sub > (datetime.now() + timedelta(hours=7)):
                try:
                    await bot.send_message(chat_id=user[0],
                                           text=f"Ваша подписка заканчивается {user[2][:18]}",
                                           protect_content=True)
                except Exception as error:
                    print(error)
        for bill in cur.execute('SELECT * FROM bill').fetchall():
            if datetime.now() - datetime.strptime(bill[3], '%Y-%m-%d %H:%M:%S.%f') > timedelta(hours=24):
                await del_bill(bill[2])
        for quick in cur.execute('SELECT * FROM quick').fetchall():
            if datetime.now() - datetime.strptime(quick[3], '%Y-%m-%d %H:%M:%S.%f') > timedelta(hours=24):
                await del_quick(quick[2])
        base.commit()
        await asleep(time)


@logger.catch()
async def del_user(user_id) -> None:
    cur.execute('UPDATE users SET date_out = ?, status = ? WHERE id_user = ?',
                (None, None, user_id))
    base.commit()
    try:
        await bot.kick_chat_member(chat_id=ID_PRIVATE_CHANNEL, user_id=user_id)
        await bot.unban_chat_member(chat_id=ID_PRIVATE_CHANNEL, user_id=user_id)
    except Exception as error:
        print(error)
