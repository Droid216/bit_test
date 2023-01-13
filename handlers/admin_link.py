from datetime import datetime
from loguru_bot.logs import logger
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

from create_bot import bot
from keyboards import kb_admin
from data_base import data_base


class Link(StatesGroup):
    name = State()
    time = State()


# @dp.callback_query_handler(kb_admin.cb_channel_link.filter())
@logger.catch()
async def create_and_view_link(callback: types.CallbackQuery, callback_data: dict):
    await bot.edit_message_text(chat_id=callback.from_user.id,
                                message_id=callback.message.message_id,
                                text=f"Управление ссылками на канале {callback_data['name_channel']}",
                                reply_markup=kb_admin.get_ikb_link(callback_data['id_channel']))


# @dp.callback_query_handler(kb_admin.cb_link.filter())
@logger.catch()
async def link_admin_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'create':
        await bot.send_message(chat_id=callback.from_user.id,
                               text=f"Введите название ссылки",
                               reply_markup=kb_admin.get_kb_cancel(False))
        await Link.name.set()
        async with state.proxy() as data:
            data['id_channel'] = callback_data['id_channel']
    elif callback_data['action'] == 'delete':
        link = await data_base.select_link(callback_data['id_link'])
        logger.info(f"Delete link Admin: {callback.from_user.id} Link: {link}")
        await bot.revoke_chat_invite_link(chat_id=callback_data['id_channel'],
                                          invite_link=link)
        await data_base.del_links(callback_data['id_link'])
        await callback.message.delete()
        await bot.send_message(chat_id=callback.from_user.id,
                               text=f"Ссылка удалена")
    elif callback_data['action'] == 'view':
        links = await data_base.select_links(callback_data['id_channel'])
        for link in links:
            if link[0] in [1, 2]:
                await bot.send_message(chat_id=callback.from_user.id,
                                       text=f"{link[1]}: {link[2]}\nПришло по ссылке: {link[4]}",
                                       disable_web_page_preview=True)
                continue
            await bot.send_message(chat_id=callback.from_user.id,
                                   text=f"{link[1]}: {link[2]}\nПришло по ссылке: {link[4]}\n"
                                        f"{f'Работает до: {link[5]}' if link[5] else ''}\n",
                                   reply_markup=kb_admin.get_ikb_set_link(link[3], link[0]),
                                   disable_web_page_preview=True)
    else:
        await callback.message.delete()


# @dp.message_handler(Text(equals='Пропустить', ignore_case=True), state=[Link.time, Link.count])
@logger.catch()
async def next_edit_handler(message: types.Message, state: FSMContext):
    await message.delete()
    st = await state.get_state()
    async with state.proxy() as data:
        if st == 'Link:time':
            data['time'] = ''
            link = await bot.create_chat_invite_link(chat_id=data['id_channel'],
                                                     name=f'{data["name"]}',
                                                     creates_join_request=True)
            await bot.send_message(chat_id=message.from_user.id,
                                   text=f'Ссылка создана\n{message.text}: {link.invite_link}',
                                   reply_markup=kb_admin.get_kb_start())
            await data_base.add_link(data['name'], link.invite_link, data['id_channel'], data['time'])
            logger.info(f"Create link Admin: {message.from_user.id} Link: {link.invite_link} Name: {data['name']} Channel: {data['id_channel']}")
            await state.finish()


# @dp.message_handler(content_types='text', state=Link.name)
@logger.catch()
async def name_link(message: types.Message, state: FSMContext):
    if len(message.text) > 30:
        await bot.send_message(chat_id=message.from_user.id,
                               text='Название не должно быть длинее 30 символов')
        return
    async with state.proxy() as data:
        data['name'] = message.text
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Введите дату и время действия ссылки в формате Y-m-d H:M\n'
                                f'Пример: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                           reply_markup=kb_admin.get_kb_cancel())
    await Link.time.set()


# @dp.message_handler(content_types='text', state=Link.time)
@logger.catch()
async def time_link(message: types.Message, state: FSMContext):
    try:
        time = datetime.strptime(message.text, '%Y-%m-%d %H:%M')
        if time < datetime.now():
            raise ValueError
        async with state.proxy() as data:
            data['time'] = message.text
            expire_date = datetime.strptime(data['time'], '%Y-%m-%d %H:%M')
            link = await bot.create_chat_invite_link(chat_id=data['id_channel'],
                                                     name=f'{data["name"]}',
                                                     expire_date=expire_date,
                                                     creates_join_request=True)
            await bot.send_message(chat_id=message.from_user.id,
                                   text=f'Ссылка создана\n{message.text}: {link.invite_link}',
                                   reply_markup=kb_admin.get_kb_start())
            await data_base.add_link(data['name'], link.invite_link, data['id_channel'], data['time'])
            logger.info(f"Create link Link: {link.invite_link} Name: {data['name']} Channel: {data['id_channel']} Time: {data['time']}")
            await state.finish()
    except ValueError:
        await bot.send_message(chat_id=message.from_user.id,
                               text='Неверный формат')
        await bot.send_message(chat_id=message.from_user.id,
                               text=f'Введите дату и время действия ссылки в формате Y-m-d H:M\n'
                                    f'Пример: {datetime.now().strftime("%Y-%m-%d %H:%M")}')


@logger.catch()
def register_handlers_admin_link(disp: Dispatcher) -> None:
    disp.register_callback_query_handler(create_and_view_link,
                                         kb_admin.cb_channel_link.filter())
    disp.register_callback_query_handler(link_admin_handler,
                                         kb_admin.cb_link.filter())
    disp.register_message_handler(next_edit_handler,
                                  Text(equals='Пропустить',
                                       ignore_case=True),
                                  state=[Link.time],
                                  is_admin=True)
    disp.register_message_handler(name_link,
                                  content_types='text',
                                  state=Link.name,
                                  is_admin=True)
    disp.register_message_handler(time_link,
                                  content_types='text',
                                  state=Link.time,
                                  is_admin=True)
