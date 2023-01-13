import os
from loguru_bot.logs import logger
from aiogram import types, Dispatcher
from aiogram.types import InputFile
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from create_bot import bot
from keyboards import kb_admin
from handlers import admin_answer, admin_edit_cover, admin_edit_price, admin_link


# @dp.message_handler(Text(equals=['Отмена', 'Стартовое меню', '/start'], ignore_case=True), is_admin=True, state ='*')
@logger.catch()
async def start_admin_handler(message: types.Message, state: FSMContext):
    await message.delete()
    if state:
        await state.finish()
    await bot.send_message(chat_id=message.from_user.id,
                           text='Стартовое меню',
                           reply_markup=kb_admin.get_kb_start())


# @dp.message_handler(Text(equals='Настройка карточек', ignore_case=True), is_admin=True)
@logger.catch()
async def setting_admin_handler(message: types.Message):
    await message.delete()
    await bot.send_message(chat_id=message.from_user.id,
                           text='Меню настройки',
                           reply_markup=kb_admin.get_ikb_setting_cover())


# @dp.message_handler(Text(equals='Настройка прайса', ignore_case=True), is_admin=True)
@logger.catch()
async def price_admin_handler(message: types.Message):
    await message.delete()
    await bot.send_message(chat_id=message.from_user.id,
                           text='Меню настройки',
                           reply_markup=kb_admin.get_ikb_setting_price())


# @dp.message_handler(Text(equals='Ссылки на канал', ignore_case=True), is_admin=True)
@logger.catch()
async def channel_link_admin_handler(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Выберите канал для управления ссылками',
                           reply_markup=kb_admin.get_ikb_channel_link())


# @dp.message_handler(Text(equals='Логи', ignore_case=True), is_admin=True)
@logger.catch()
async def logs_file(message: types.Message):
    for file in os.listdir('./loguru_bot/filelog'):
        await bot.send_document(chat_id=message.from_user.id,
                                document=InputFile("./loguru_bot/filelog/" + file))


@logger.catch()
def register_handlers_admin(disp: Dispatcher) -> None:
    disp.register_message_handler(start_admin_handler,
                                  Text(equals=['Отмена', 'Стартовое меню', '/start'],
                                       ignore_case=True),
                                  is_admin=True,
                                  state='*')
    disp.register_message_handler(setting_admin_handler,
                                  Text(equals='Настройка карточек',
                                       ignore_case=True),
                                  is_admin=True)
    disp.register_message_handler(price_admin_handler,
                                  Text(equals='Настройка прайса',
                                       ignore_case=True),
                                  is_admin=True)
    disp.register_message_handler(channel_link_admin_handler,
                                  Text(equals='Ссылки на канал',
                                       ignore_case=True),
                                  is_admin=True)
    disp.register_message_handler(logs_file,
                                  Text(equals='Логи', ignore_case=True),
                                  is_admin=True)
    admin_answer.register_handlers_admin_answer(disp)
    admin_edit_cover.register_handlers_admin_edit_cover(disp)
    admin_edit_price.register_handlers_admin_edit_price(disp)
    admin_link.register_handlers_admin_link(disp)
