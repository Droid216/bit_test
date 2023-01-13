import asyncio
from loguru_bot.logs import logger
from aiogram import types, Dispatcher

from create_bot import bot
from config import ID_PRIVATE_CHANNEL, ID_PREVIEW_CHANNEL
from data_base import data_base


# @dp.chat_join_request_handlers(lambda link: link.chat.id == ID_PRIVATE_CHANNEL)
@logger.catch()
async def join_private_channel(chat_member: types.ChatJoinRequest):
    user = await data_base.bd_user(chat_member.from_user.id)
    if not user:
        await bot.decline_chat_join_request(chat_id=chat_member.chat.id,
                                            user_id=chat_member.from_user.id)
    if user['status']:
        link = chat_member.invite_link.invite_link
        logger.info(f"Invite Eva Snow 18+ Link: {link} User: {chat_member.from_user.first_name} Id: {chat_member.from_user.id}")
        await data_base.count_link(link)
        await bot.approve_chat_join_request(chat_id=chat_member.chat.id,
                                            user_id=chat_member.from_user.id)
        await bot.send_message(chat_id=chat_member.from_user.id,
                               text=f'Теперь вы подписаны на канал.'
                                    f'\nДля перехода в канал нажмите: {chat_member.invite_link.invite_link}',
                               disable_web_page_preview=True,
                               protect_content=True)
    else:
        await bot.decline_chat_join_request(chat_id=chat_member.chat.id,
                                            user_id=chat_member.from_user.id)
        try:
            await bot.send_message(chat_id=chat_member.from_user.id,
                                   text='Вы не являетесь подписчиком')
        except Exception as error:
            print(error)


# @dp.chat_join_request_handlers(lambda link: link.chat.id == ID_PREVIEW_CHANNEL)
@logger.catch()
async def join_preview_channel(chat_member: types.ChatJoinRequest):
    link = chat_member.invite_link.invite_link
    logger.info(f"Invite Eva Snow Preview Link: {link} User: {chat_member.from_user.first_name} Id: {chat_member.from_user.id}")
    await data_base.count_link(link)
    await asyncio.sleep(5)
    await bot.approve_chat_join_request(chat_id=chat_member.chat.id,
                                        user_id=chat_member.from_user.id)


@logger.catch()
def register_handlers_client_chat_link(disp: Dispatcher) -> None:
    disp.register_chat_join_request_handler(join_private_channel,
                                            lambda link: link.chat.id == ID_PRIVATE_CHANNEL)
    disp.register_chat_join_request_handler(join_preview_channel,
                                            lambda link: link.chat.id == ID_PREVIEW_CHANNEL)
