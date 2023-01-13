import typing
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import BoundFilter

from config import ADMINS
from loguru_bot.logs import logger


class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin: typing.Optional[bool] = None):
        self.is_admin = is_admin

    async def check(self, obj):
        if self.is_admin is None:
            return False
        return (obj.from_user.id in ADMINS) == self.is_admin


@logger.catch()
def register_filter(dp: Dispatcher) -> None:
    dp.filters_factory.bind(AdminFilter)
