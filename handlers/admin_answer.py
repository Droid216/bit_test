from loguru_bot.logs import logger
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from create_bot import bot
from keyboards import kb_admin


class Answer(StatesGroup):
    answer = State()


# @dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('prst'))
@logger.catch()
async def answer_present(callback: types.CallbackQuery, state: FSMContext):
    if callback.data != 'prst_ignor':
        user_id = int(callback.data[5:])
        await bot.send_message(chat_id=callback.from_user.id,
                               text="Пришлите ответ",
                               reply_markup=kb_admin.get_kb_cancel(False))
        await Answer.answer.set()
        async with state.proxy() as data:
            data['user_id'] = user_id
            data['message_id'] = callback.message.message_id
    else:
        await callback.message.delete()


# @dp.message_handler(content_types=types.ContentType.ANY, state=Answer.answer)
@logger.catch()
async def answer_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            await bot.send_message(chat_id=data['user_id'],
                                   text='Ответ на подарок от Евы:',
                                   disable_web_page_preview=True,
                                   protect_content=True)
            await bot.copy_message(chat_id=data['user_id'],
                                   from_chat_id=message.chat.id,
                                   message_id=message.message_id,
                                   protect_content=True)
            await bot.delete_message(chat_id=message.from_user.id,
                                     message_id=data['message_id'])
        except Exception as error:
            print(error)
        await bot.send_message(chat_id=message.from_user.id,
                               text="Ответ отправлен",
                               reply_markup=kb_admin.get_kb_start())
        logger.info(f"Answer present Admin: {message.from_user.id} User: {data['user_id']}")
    await state.finish()


@logger.catch()
def register_handlers_admin_answer(disp: Dispatcher) -> None:
    disp.register_callback_query_handler(answer_present,
                                         lambda callback_query: callback_query.data.startswith('prst'))
    disp.register_message_handler(answer_message,
                                  content_types=types.ContentType.ANY,
                                  state=Answer.answer,
                                  is_admin=True)
