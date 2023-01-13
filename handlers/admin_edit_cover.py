from loguru_bot.logs import logger
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

from create_bot import bot
from keyboards import kb_admin
from data_base import data_base


class EditCover(StatesGroup):
    text = State()
    caption = State()
    photo = State()
    finish = State()


# @dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('stg'))
@logger.catch()
async def setting_admin_callback(callback: types.CallbackQuery, state: FSMContext):
    label = callback.data[4:]
    cover = await data_base.cover(label)
    if label in ['about', 'start']:
        await bot.send_message(chat_id=callback.from_user.id,
                               text=f'Текст сейчас:\n{cover["caption"]}',
                               disable_web_page_preview=True)
        await EditCover.text.set()
    else:
        await bot.send_message(chat_id=callback.from_user.id,
                               text='Карточка сейчас:')
        await bot.send_photo(chat_id=callback.from_user.id,
                             photo=cover['photo'],
                             caption=cover['caption'],)
        await EditCover.caption.set()
    async with state.proxy() as data:
        data['label'] = label
    await bot.send_message(chat_id=callback.from_user.id,
                           text='Напишите текст который будет отображаться',
                           reply_markup=kb_admin.get_kb_cancel())
    await callback.message.delete()


# @dp.message_handler(Text(equals='Пропустить', ignore_case=True), state=[EditCover.text, EditCover.caption, EditCover.photo])
@logger.catch()
async def next_edit_handler(message: types.Message, state: FSMContext):
    await message.delete()
    st = await state.get_state()
    async with state.proxy() as data:
        cover = await data_base.cover(data['label'])
        if st == 'EditCover:text':
            data['text'] = cover['caption']
            await bot.send_message(chat_id=message.from_user.id,
                                   text='Новый текст сообщения:',
                                   reply_markup=kb_admin.get_kb_cancel(False))
            await bot.send_message(chat_id=message.from_user.id,
                                   text=f'{data["text"]}',
                                   disable_web_page_preview=True,
                                   reply_markup=kb_admin.get_ikb_finish())
            await EditCover.finish.set()
        elif st == 'EditCover:caption':
            data['caption'] = cover['caption']
            await bot.send_message(chat_id=message.from_user.id,
                                   text='Пришлите ссылку на фото')
            await EditCover.photo.set()
        elif st == 'EditCover:photo':
            data['photo'] = cover['photo']
            await bot.send_message(chat_id=message.from_user.id,
                                   text='Новый вид карточки:',
                                   reply_markup=kb_admin.get_kb_cancel(False))
            await bot.send_photo(chat_id=message.from_user.id,
                                 photo=data['photo'],
                                 caption=f'{data["caption"]}',
                                 reply_markup=kb_admin.get_ikb_finish())
            await EditCover.finish.set()


# @dp.message_handler(content_types='text', state=[EditCover.text, EditCover.caption])
@logger.catch()
async def edit_caption_cover(message: types.Message, state: FSMContext):
    st = await state.get_state()
    async with state.proxy() as data:
        if st == 'EditCover:text':
            data['text'] = message.text
            await bot.send_message(chat_id=message.from_user.id,
                                   text='Новый текст сообщения:',
                                   reply_markup=kb_admin.get_kb_cancel(False))
            await bot.send_message(chat_id=message.from_user.id,
                                   text=f'{data["text"]}',
                                   disable_web_page_preview=True,
                                   reply_markup=kb_admin.get_ikb_finish())
            await EditCover.finish.set()
        else:
            data['caption'] = message.text
            await bot.send_message(chat_id=message.from_user.id,
                                   text=f'Пришлите ссылку на фото')
            await EditCover.photo.set()


# @dp.message_handler(content_types='text', state=[EditCover.photo])
@logger.catch()
async def edit_photo_cover(message: types.Message, state: FSMContext):
    if message.entities:
        async with state.proxy() as data:
            data['photo'] = message.text
            await bot.send_message(chat_id=message.from_user.id,
                                   text='Новый вид карточки:',
                                   reply_markup=kb_admin.get_kb_cancel(False))
            await bot.send_photo(chat_id=message.from_user.id,
                                 photo=data['photo'],
                                 caption=f'{data["caption"]}',
                                 reply_markup=kb_admin.get_ikb_finish())
        await EditCover.finish.set()
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text=f'Пришлите ссылку на фото')


# @dp.callback_query_handler(text='finish', state=EditCover.finish)
@logger.catch()
async def edit_finish(callback: types.CallbackQuery, state: FSMContext):
    await data_base.edit_cover(state)
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f'Карточка отредактированна',
                           reply_markup=kb_admin.get_kb_start())
    async with state.proxy() as data:
        if data['label'] in ['about', 'start']:
            logger.info(f"Edit cover Admin: {callback.from_user.id}\nNew cover:\n"
                        f"{data['text']}")
        else:
            logger.info(f"Edit cover Admin: {callback.from_user.id}\nNew cover:\n"
                        f"{data['photo']}\n{data['caption']}")
    await state.finish()


@logger.catch()
def register_handlers_admin_edit_cover(disp: Dispatcher) -> None:
    disp.register_message_handler(next_edit_handler,
                                  Text(equals='Пропустить',
                                       ignore_case=True),
                                  state=[EditCover.text, EditCover.caption, EditCover.photo],
                                  is_admin=True)
    disp.register_callback_query_handler(setting_admin_callback,
                                         lambda callback_query: callback_query.data.startswith('stg'))
    disp.register_message_handler(edit_caption_cover,
                                  content_types='text',
                                  state=[EditCover.text, EditCover.caption],
                                  is_admin=True)
    disp.register_message_handler(edit_photo_cover,
                                  content_types='text',
                                  state=[EditCover.photo],
                                  is_admin=True)
    disp.register_callback_query_handler(edit_finish,
                                         text='finish',
                                         state=EditCover.finish)
