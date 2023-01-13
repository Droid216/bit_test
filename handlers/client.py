from loguru_bot.logs import logger
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from handlers import client_chat_link, client_pay
from .anti_flood import anti_flood
from create_bot import bot, dp
from data_base import data_base
from keyboards import kb_client


# @dp.message_handler(Text(equals=['/start', '💸Тарифы']))
@dp.throttled(anti_flood, rate=3)
@logger.catch()
async def start_handler(message: types.Message):
    user = await data_base.bd_user(message.from_user.id)
    if not user:
        logger.info(f"New user User: {message.from_user.first_name} ID: {message.from_user.id}")
        await data_base.add_bd_user(message.from_user.id)
    cover_start = await data_base.cover('start')
    cover_tariffs = await data_base.cover('tariffs')
    await bot.send_message(chat_id=message.from_user.id,
                           text=cover_start['caption'],
                           parse_mode='HTML',
                           disable_web_page_preview=True,
                           protect_content=True,
                           reply_markup=kb_client.get_kb_start())
    await bot.send_photo(chat_id=message.from_user.id,
                         photo=cover_tariffs['photo'],
                         caption=cover_tariffs['caption'],
                         parse_mode='HTML',
                         protect_content=True,
                         reply_markup=kb_client.get_ikb_tariffs())


# @dp.message_handler(Text(equals='🔞Моя подписка', ignore_case=True))
@dp.throttled(anti_flood, rate=3)
@logger.catch()
async def sub_handler(message: types.Message):
    user = await data_base.bd_user(message.from_user.id)
    if user['status']:
        link = await data_base.select_link(1)
        await bot.send_message(chat_id=message.from_user.id,
                               text=f'💋Твоя подписка закончится\n{user["date_out"].split(".")[0]}\n\n'
                                    f'{link}',
                               disable_web_page_preview=True,
                               protect_content=True)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text='🥲У тебя пока нет подписки',
                               protect_content=True)


# @dp.message_handler(Text(equals='🤫Ссылка на канал "Eva Snow Preview"🤫', ignore_case=True))
@logger.catch()
async def link_preview_channel(message: types.Message):
    link = await data_base.select_link(2)
    await bot.send_message(chat_id=message.from_user.id,
                           text='<b>Eva Snow Preview</b>',
                           parse_mode='HTML',
                           reply_markup=kb_client.get_link(link),
                           protect_content=True)


# @dp.message_handler(Text(equals='🌸О Еве', ignore_case=True))
@dp.throttled(anti_flood, rate=3)
@logger.catch()
async def about_handler(message: types.Message):
    cover = await data_base.cover('about')
    await bot.send_message(chat_id=message.from_user.id,
                           text=cover['caption'],
                           protect_content=True,
                           disable_web_page_preview=True)


# @dp.callback_query_handler(text=sub')
@dp.throttled(anti_flood, rate=2)
@logger.catch()
async def sub_callback(callback: types.CallbackQuery):
    price = await data_base.price_list(callback.data)
    cover = await data_base.cover('sub')
    text = f'<b>Тариф:</b> 🔞Доступ в приватный канал\n' \
           f'<b>Стоимость:</b> {price["price"]} RUB\n' \
           f'<b>Срок действия:</b> ⏰30 дней \n\n' + cover['caption']
    await bot.edit_message_media(media=types.InputMediaPhoto(media=cover['photo'],
                                                             caption=text,
                                                             parse_mode='HTML'),
                                 chat_id=callback.from_user.id,
                                 message_id=callback.message.message_id,
                                 reply_markup=kb_client.get_ikb_pay('sub'))


# @dp.callback_query_handler(text='contact')
@dp.throttled(anti_flood, rate=2)
@logger.catch()
async def contact_callback(callback: types.CallbackQuery):
    price = await data_base.price_list(callback.data)
    cover = await data_base.cover('contact')
    text = f'<b>Тариф:</b> 💬Общение со мной\n' \
           f'<b>Стоимость:</b> 💵{price["price"]} RUB\n' \
           f'<b>Срок действия:</b> ♾Бесконечно \n\n' + cover['caption']
    await bot.edit_message_media(media=types.InputMediaPhoto(media=cover['photo'],
                                                             caption=text,
                                                             parse_mode='HTML'),
                                 chat_id=callback.from_user.id,
                                 message_id=callback.message.message_id,
                                 reply_markup=kb_client.get_ikb_pay('contact'))


# @dp.callback_query_handler(text='present')
@dp.throttled(anti_flood, rate=2)
@logger.catch()
async def present_callback(callback: types.CallbackQuery):
    service1 = await data_base.price_list('present1')
    service2 = await data_base.price_list('present2')
    service3 = await data_base.price_list('present3')
    service4 = await data_base.price_list('present4')
    cover = await data_base.cover('present')
    text = cover['caption'] + '\n\n' + f'<b>{service1["name"]}:</b> {service1["price"]} RUB\n'\
                                       f'<b>{service2["name"]}:</b> {service2["price"]} RUB\n'\
                                       f'<b>{service3["name"]}:</b> {service3["price"]} RUB\n'\
                                       f'<b>{service4["name"]}:</b> {service4["price"]} RUB\n'
    await bot.edit_message_media(media=types.InputMediaPhoto(media=cover['photo'],
                                                             caption=text,
                                                             parse_mode='HTML'),
                                 chat_id=callback.from_user.id,
                                 message_id=callback.message.message_id,
                                 reply_markup=kb_client.get_ikb_present())


# @dp.callback_query_handler(text='cancel')
@dp.throttled(anti_flood, rate=2)
@logger.catch()
async def cancel_callback(callback: types.CallbackQuery):
    cover = await data_base.cover('tariffs')
    await bot.edit_message_media(media=types.InputMediaPhoto(media=cover['photo'],
                                                             caption=cover['caption'],
                                                             parse_mode='HTML'),
                                 chat_id=callback.from_user.id,
                                 message_id=callback.message.message_id,
                                 reply_markup=kb_client.get_ikb_tariffs())


@logger.catch()
def register_handlers_client(disp: Dispatcher) -> None:
    disp.register_message_handler(start_handler,
                                  Text(equals=['/start', '💸Тарифы'],
                                       ignore_case=True),
                                  is_admin=False)
    disp.register_message_handler(sub_handler,
                                  Text(equals='🔞Моя подписка',
                                       ignore_case=True),
                                  is_admin=False)
    disp.register_message_handler(link_preview_channel,
                                  Text(equals='🤫Ссылка на канал "Eva Snow Preview"🤫',
                                       ignore_case=True),
                                  is_admin=False)
    disp.register_message_handler(about_handler,
                                  Text(equals='🌸О Еве',
                                       ignore_case=True),
                                  is_admin=False)
    disp.register_callback_query_handler(sub_callback,
                                         text='sub')
    disp.register_callback_query_handler(contact_callback,
                                         text='contact')
    disp.register_callback_query_handler(present_callback,
                                         text='present')
    disp.register_callback_query_handler(cancel_callback,
                                         text='cancel')
    client_chat_link.register_handlers_client_chat_link(disp)
    client_pay.register_handlers_client_pay(disp)
