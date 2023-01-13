from loguru_bot.logs import logger
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from config import ID_PRIVATE_CHANNEL, ID_PREVIEW_CHANNEL


cb_channel_link = CallbackData('ikb_channel_link', 'name_channel', 'id_channel')
cb_link = CallbackData('ikb_link', 'action', 'id_channel', 'id_link')


@logger.catch()
def get_kb_start() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    b1 = KeyboardButton(text='Настройка карточек')
    b2 = KeyboardButton(text='Настройка прайса')
    b3 = KeyboardButton(text='Ссылки на канал')
    b4 = KeyboardButton(text='Логи')
    kb.add(b1, b2, b3, b4)
    return kb


@logger.catch()
def get_kb_cancel(next_btn=True) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton(text='Отмена')
    if next_btn:
        b2 = KeyboardButton(text='Пропустить')
        kb.add(b2)
    kb.add(b1)
    return kb


@logger.catch()
def get_ikb_setting_cover() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    ib1 = InlineKeyboardButton(text="Изменить текст 'Приветствия'", callback_data='stg_start')
    ib2 = InlineKeyboardButton(text="Изменить текст 'Обо мне'", callback_data='stg_about')
    ib3 = InlineKeyboardButton(text="Изменить карточку 'Тарифы'", callback_data='stg_tariffs')
    ib4 = InlineKeyboardButton(text="Изменить карточку 'Подписки'", callback_data='stg_sub')
    ib5 = InlineKeyboardButton(text="Изменить карточку 'Контакта'", callback_data='stg_contact')
    ib6 = InlineKeyboardButton(text="Изменить карточку 'Подарков'", callback_data='stg_present')
    ikb.add(ib1, ib2, ib3, ib4, ib5, ib6)
    return ikb


@logger.catch()
def get_ikb_setting_price() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    ib1 = InlineKeyboardButton(text="Изменить прайс 'Подписки'", callback_data='prc_sub')
    ib2 = InlineKeyboardButton(text="Изменить прайс 'Контакта'", callback_data='prc_contact')
    ib3 = InlineKeyboardButton(text="Изменить прайс 'Кофе'", callback_data='prc_present1')
    ib4 = InlineKeyboardButton(text="Изменить прайс 'Трусики'", callback_data='prc_present2')
    ib5 = InlineKeyboardButton(text="Изменить прайс 'Цветочков'", callback_data='prc_present3')
    ib6 = InlineKeyboardButton(text="Изменить прайс 'Игрушки'", callback_data='prc_present4')
    ikb.add(ib1, ib2, ib3, ib4, ib5, ib6)
    return ikb


@logger.catch()
def get_ikb_channel_link() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=1)
    ib1 = InlineKeyboardButton(text='Eva Snow 18+',
                               callback_data=cb_channel_link.new('Eva Snow 18+', ID_PRIVATE_CHANNEL))
    ib2 = InlineKeyboardButton(text='Eva Snow Preview',
                               callback_data=cb_channel_link.new('Eva Snow Preview', ID_PREVIEW_CHANNEL))
    ikb.add(ib1, ib2)
    return ikb


@logger.catch()
def get_ikb_link(channel_id) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=1)
    ib1 = InlineKeyboardButton(text='Создать ссылку', callback_data=cb_link.new('create', channel_id, ''))
    ib2 = InlineKeyboardButton(text='Посмотреть ссылки', callback_data=cb_link.new('view', channel_id, ''))
    ikb.add(ib1, ib2)
    return ikb


@logger.catch()
def get_ikb_set_link(channel_id, id_link) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=1)
    ib1 = InlineKeyboardButton(text='Удалить', callback_data=cb_link.new('delete', channel_id, id_link))
    ib2 = InlineKeyboardButton(text='Скрыть', callback_data=cb_link.new('ignore', '', ''))
    ikb.add(ib1, ib2)
    return ikb


@logger.catch()
def get_ikb_present_answer(user_id) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    ib1 = InlineKeyboardButton(text='Ответить', callback_data=f'prst_{user_id}')
    ib2 = InlineKeyboardButton(text='Игнорировать', callback_data='prst_ignor')
    ikb.add(ib1, ib2)
    return ikb


@logger.catch()
def get_ikb_finish() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    ib1 = InlineKeyboardButton(text='Подтвердить', callback_data='finish')
    ikb.add(ib1)
    return ikb


@logger.catch()
def get_link(link) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    ib1 = InlineKeyboardButton(text='🫶🏻Жмякай🫶🏻', url=link)
    ikb.add(ib1)
    return ikb
