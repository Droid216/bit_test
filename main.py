from asyncio import get_event_loop
from aiogram import executor
from loguru_bot.logs import logger

from config import ID_EVA_SUPPORT
from create_bot import dp, bot
from handlers import admin, client
from data_base import data_base
from filter import admin_filter


@logger.catch()
async def on_startup(_) -> None:
    data_base.sql_start()
    loop = get_event_loop()
    loop.create_task(data_base.check_sub_time(3600))
    logger.info("Start bot")
    await bot.send_message(chat_id=ID_EVA_SUPPORT,
                           text="Start bot")


@logger.catch()
async def on_shutdown(_) -> None:
    logger.info("Shutdown bot")
    await bot.send_message(chat_id=ID_EVA_SUPPORT,
                           text="Shutdown bot")


if __name__ == '__main__':
    admin_filter.register_filter(dp)
    admin.register_handlers_admin(dp)
    client.register_handlers_client(dp)
    executor.start_polling(dispatcher=dp,
                           on_startup=on_startup, skip_updates=False, on_shutdown=on_shutdown)

