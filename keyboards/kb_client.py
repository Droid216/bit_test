from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.callback_data import CallbackData
from loguru_bot.logs import logger

cb_label = CallbackData('ikb_label', 'label')
cb_pay = CallbackData('ikb_pay', 'label', 'payment')
cb_check_bill = CallbackData('ikb_check_bill', 'label', 'bill_id')
cb_check_quick = CallbackData('ikb_check_quick', 'label', 'quick_id')


@logger.catch()
def get_kb_start() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton(text='💸Тарифы')
    b2 = KeyboardButton(text='🔞Моя подписка')
    b3 = KeyboardButton(text='🤫Ссылка на канал "Eva Snow Preview"🤫')
    b4 = KeyboardButton(text='🌸О Еве')
    kb.add(b1, b2).add(b3).add(b4)
    return kb


@logger.catch()
def get_ikb_tariffs() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=1)
    ib1 = InlineKeyboardButton(text='💦Подписка на месяц', callback_data='sub')
    ib2 = InlineKeyboardButton(text="📞Cвязь со мной", callback_data='contact')
    ib3 = InlineKeyboardButton(text="🌷Подарочек", callback_data='present')
    ikb.add(ib1, ib2, ib3)
    return ikb


@logger.catch()
def get_ikb_pay(label) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=1)
    ib1 = InlineKeyboardButton(text='❤️Оплатить', callback_data=cb_label.new(label))
    ib2 = InlineKeyboardButton(text='🔙Назад', callback_data='cancel')
    ikb.add(ib1, ib2)
    return ikb


@logger.catch()
def get_ikb_present() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=1)
    ib1 = InlineKeyboardButton(text='☕️Подарить кофе', callback_data=cb_label.new('present1'))
    ib2 = InlineKeyboardButton(text='👙Подарить новые трусики', callback_data=cb_label.new('present2'))
    ib3 = InlineKeyboardButton(text='💐Подарить цветы', callback_data=cb_label.new('present3'))
    ib4 = InlineKeyboardButton(text='🍆Подарить новую игрушку', callback_data=cb_label.new('present4'))
    ib5 = InlineKeyboardButton(text='🔙Назад', callback_data='cancel')
    ikb.add(ib1, ib2, ib3, ib4, ib5)
    return ikb


@logger.catch()
def ikb_bill(url, label, bill_id) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=1)
    ib1 = InlineKeyboardButton(text="Оплатить", url=url)
    ib2 = InlineKeyboardButton(text="Проверить оплату", callback_data=cb_check_bill.new(label, bill_id))
    ikb.add(ib1, ib2)
    return ikb


@logger.catch()
def ikb_quick(url, label, quick_id) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=1)
    ib1 = InlineKeyboardButton(text="Оплатить", url=url)
    ib2 = InlineKeyboardButton(text="Проверить оплату", callback_data=cb_check_quick.new(label, quick_id))
    ikb.add(ib1, ib2)
    return ikb


@logger.catch()
def ikb_payment(label) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=1)
    ib1 = InlineKeyboardButton(text='ЮKassa', callback_data=cb_pay.new(label, 'kassa'))
    ib2 = InlineKeyboardButton(text='QiWi', callback_data=cb_pay.new(label, 'qiwi'))
    ib3 = InlineKeyboardButton(text='🔙Назад', callback_data='cancel')
    ikb.add(ib1, ib2, ib3)
    return ikb


@logger.catch()
def get_link(link) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    ib1 = InlineKeyboardButton(text='🫶🏻Жмякай🫶🏻', url=link)
    ikb.add(ib1)
    return ikb
