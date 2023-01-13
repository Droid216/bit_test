from loguru_bot.logs import logger
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

from create_bot import bot
from keyboards import kb_admin
from data_base import data_base


class EditPrice(StatesGroup):
    price = State()
    title = State()
    description = State()
    finish = State()


# @dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('prc'))
@logger.catch()
async def price_admin_callback(callback: types.CallbackQuery, state: FSMContext):
    label = callback.data[4:]
    price = await data_base.price_list(label)
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f'Прайс \"{price["name"]}\"сейчас\nЦена: {price["price"]}\n'
                                f'Заголовок:\n{price["title"]}\nОписание:\n{price["description"]}',
                           disable_web_page_preview=True)
    await EditPrice.price.set()
    async with state.proxy() as data:
        data['label'] = label
        data['name'] = price['name']
    await bot.send_message(chat_id=callback.from_user.id,
                           text='Напишите цену',
                           reply_markup=kb_admin.get_kb_cancel())
    await callback.message.delete()


# @dp.message_handler(Text(equals='Пропустить', ignore_case=True), state=[EditPrice.price, EditPrice.title, EditPrice.description])
@logger.catch()
async def next_edit_price(message: types.Message, state: FSMContext):
    await message.delete()
    st = await state.get_state()
    async with state.proxy() as data:
        price = await data_base.price_list(data['label'])
        if st == 'EditPrice:price':
            data['price'] = price['price']
            await bot.send_message(chat_id=message.from_user.id,
                                   text='Введите новый заголовок')
            await EditPrice.title.set()
        elif st == 'EditPrice:title':
            data['title'] = price['title']
            await bot.send_message(chat_id=message.from_user.id,
                                   text='Введите новое описание')
            await EditPrice.description.set()
        elif st == 'EditPrice:description':
            data['description'] = price['description']
            await bot.send_message(chat_id=message.from_user.id,
                                   text=f'Текущий прайс:',
                                   reply_markup=kb_admin.get_kb_cancel(False))
            await bot.send_message(chat_id=message.from_user.id,
                                   text=f'Прайс \"{data["name"]}\" сейчас\nЦена: {data["price"]}\n'
                                        f'Заголовок:\n{data["title"]}\nОписание:\n{data["description"]}',
                                   disable_web_page_preview=True,
                                   reply_markup=kb_admin.get_ikb_finish())
            await EditPrice.finish.set()


# @dp.message_handler(content_types='text', state=EditPrice.price)
@logger.catch()
async def edit_price(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await bot.send_message(chat_id=message.from_user.id,
                               text='Введите число')
        return
    async with state.proxy() as data:
        data['price'] = int(message.text)
    await bot.send_message(chat_id=message.from_user.id,
                           text='Введите новый заголовок')
    await EditPrice.title.set()


# @dp.message_handler(content_types='text', state=EditPrice.title)
@logger.catch()
async def edit_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text
    await bot.send_message(chat_id=message.from_user.id,
                           text='Введите новое описание')
    await EditPrice.description.set()


# @dp.message_handler(content_types='text', state=EditPrice.description)
@logger.catch()
async def edit_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
        await bot.send_message(chat_id=message.from_user.id,
                               text=f'Текущий прайс:',
                               reply_markup=kb_admin.get_kb_cancel(False))
        await bot.send_message(chat_id=message.from_user.id,
                               text=f'Прайс \"{data["name"]}\" сейчас\nЦена: {data["price"]}\n'
                                    f'Заголовок:\n{data["title"]}\nОписание:\n{data["description"]}',
                               disable_web_page_preview=True,
                               reply_markup=kb_admin.get_ikb_finish())
    await EditPrice.finish.set()


# @dp.callback_query_handler(text='finish', state=EditPrice.finish)
@logger.catch()
async def edit_price_finish(callback: types.CallbackQuery, state: FSMContext):
    await data_base.edit_price(state)
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f'Прайс обновлен',
                           reply_markup=kb_admin.get_kb_start())
    async with state.proxy() as data:
        logger.info(f"Edit price Admin: {callback.from_user.id}\nNew price:\n"
                    f'Прайс \"{data["name"]}\" сейчас\nЦена: {data["price"]}\n'
                    f'Заголовок:\n{data["title"]}\nОписание:\n{data["description"]}')
    await state.finish()


@logger.catch()
def register_handlers_admin_edit_price(disp: Dispatcher) -> None:
    disp.register_callback_query_handler(price_admin_callback,
                                         lambda callback_query: callback_query.data.startswith('prc'))
    disp.register_message_handler(next_edit_price,
                                  Text(equals='Пропустить',
                                       ignore_case=True),
                                  state=[EditPrice.price, EditPrice.title, EditPrice.description],
                                  is_admin=True)
    disp.register_message_handler(edit_price,
                                  content_types='text',
                                  state=EditPrice.price,
                                  is_admin=True)
    disp.register_message_handler(edit_title,
                                  content_types='text',
                                  state=EditPrice.title,
                                  is_admin=True)
    disp.register_message_handler(edit_description,
                                  content_types='text',
                                  state=EditPrice.description,
                                  is_admin=True)
    disp.register_callback_query_handler(edit_price_finish,
                                         text='finish',
                                         state=EditPrice.finish)
