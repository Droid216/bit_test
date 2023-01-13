from pyqiwip2p import QiwiP2P
from yookassa import Configuration, Payment
from loguru_bot.logs import logger
from aiogram import types, Dispatcher
import json

from .anti_flood import anti_flood
from create_bot import bot, dp
from config import ID_EVA_SUPPORT, P2P, API, SHOP_API
from data_base import data_base
from keyboards import kb_client, kb_admin


p2p = QiwiP2P(auth_key=P2P)
Configuration.account_id = SHOP_API
Configuration.secret_key = API


# @dp.callback_query_handler(kb_client.cb_label.filter())
@dp.throttled(anti_flood, rate=3)
@logger.catch()
async def label_callback(callback: types.CallbackQuery, callback_data: dict):
    await bot.edit_message_reply_markup(chat_id=callback.from_user.id,
                                        message_id=callback.message.message_id,
                                        reply_markup=kb_client.ikb_payment(callback_data['label']))


# @dp.callback_query_handler(kb_client.cb_pay.filter(payment='qiwi'))
@dp.throttled(anti_flood, rate=3)
@logger.catch()
async def pay_callback(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    label = callback_data['label']
    name_user = callback.from_user.username
    if label == "contact" and not name_user:
        await bot.send_message(chat_id=callback.from_user.id,
                               text='Для покупки данной услуги тебе надо указать "Имя пользователя" в профиле\n'
                                    'Настройки->Изменить профиль->Имя пользователя',
                               protect_content=True)
    else:
        await bot.send_message(chat_id=callback.from_user.id,
                               text='Секундочку... формируется счёт🥰',
                               protect_content=True)
        price_list = await data_base.price_list(label)
        bill = p2p.bill(amount=price_list['price'],
                        lifetime=15,
                        comment=f'{callback.from_user.id}_{label}')
        await data_base.add_bill(callback.from_user.id, bill.bill_id)
        await bot.send_message(chat_id=callback.from_user.id,
                               text=f"<b>{price_list['title']}</b>\n{price_list['description']}\n\n"
                                    f"<em>После оплаты нажми на кнопочку</em>\n👇🏻<b>Проверить оплату</b>👇🏻",
                               parse_mode='HTML',
                               disable_web_page_preview=True,
                               protect_content=True,
                               reply_markup=kb_client.ikb_bill(bill.pay_url, label, bill.bill_id))


# @dp.callback_query_handler(kb_client.cb_check_bill.filter())
@dp.throttled(anti_flood, rate=3)
@logger.catch()
async def check_callback_bill(callback: types.CallbackQuery, callback_data: dict):
    label = callback_data['label']
    bill_id = callback_data['bill_id']
    info = await data_base.check_bill(bill_id)
    if info:
        if p2p.check(bill_id=bill_id).status == 'PAID':
            logger.info(f"Buy {label} User: {callback.from_user.first_name} Id: {callback.from_user.id}")
            if label == 'sub':
                link = await data_base.select_link(1)
                await bot.send_message(chat_id=callback.from_user.id,
                                       text='🫦Жду тебя🫦',
                                       reply_markup=kb_admin.get_link(link),
                                       disable_web_page_preview=True,
                                       protect_content=True)
                await data_base.del_bill(bill=bill_id)
                await data_base.buy_sub(callback.from_user.id)
            elif label == 'contact':
                await data_base.del_bill(bill=bill_id)
                await bot.send_message(chat_id=callback.from_user.id,
                                       text='Я с тобой свяжусь как можно скорей, до связи🤙🏻👄',
                                       protect_content=True)
                await bot.send_message(chat_id=ID_EVA_SUPPORT,
                                       text=f'{callback.from_user.first_name} хочет пообщаться\n'
                                            f'Его контак @{callback.from_user.username}',
                                       disable_web_page_preview=True,
                                       protect_content=True)
                await data_base.buy_contact(callback.from_user.id)
            elif label[:-1] == 'present':
                await data_base.del_bill(bill=bill_id)
                present = await data_base.price_list(label)
                await bot.send_sticker(chat_id=callback.from_user.id,
                                       sticker='CAACAgIAAxkBAAEGOxpjW420O42YgbKjwS_WwLG1Vt4q4AAC1gcAAkb7rARW8D_bUpMSUyoE',
                                       protect_content=True)
                await bot.send_message(chat_id=callback.from_user.id,
                                       text=f'Спасибо за {present["name"]}, ты лучший😘',
                                       protect_content=True)
                await bot.send_message(chat_id=ID_EVA_SUPPORT,
                                       text=f'{callback.from_user.first_name} прислал в подарок {present["name"]}',
                                       reply_markup=kb_admin.get_ikb_present_answer(callback.from_user.id),
                                       disable_web_page_preview=True)
        else:
            await callback.answer(text='Не оплачено')
    else:
        await callback.message.delete()


# @dp.callback_query_handler(kb_client.cb_pay.filter(payment='kassa'))
@dp.throttled(anti_flood, rate=3)
async def pay_kassa_callback(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    label = callback_data['label']
    name_user = callback.from_user.username
    if label == "contact" and not name_user:
        await bot.send_message(chat_id=callback.from_user.id,
                               text='Для покупки данной услуги тебе надо указать "Имя пользователя" в профиле\n'
                                    'Настройки->Изменить профиль->Имя пользователя',
                               protect_content=True)
    else:
        price_list = await data_base.price_list(label)
        await bot.send_message(chat_id=callback.from_user.id,
                               text='Секундочку... формируется счёт🥰',
                               protect_content=True)
        quickpay = Payment.create({"amount": {"value": f'{price_list["price"]}',
                                              "currency": "RUB"},
                                   "payment_method_data": {"type": "bank_card"},
                                   "confirmation": {"type": "redirect",
                                                    "return_url": "ссылка"},
                                   "capture": True, "description": f'{callback.from_user.id}_{label}'})
        data = json.loads(quickpay.json())
        url = (data['confirmation'])['confirmation_url']
        await data_base.add_quick(callback.from_user.id, quickpay.id)
        await bot.send_message(chat_id=callback.from_user.id,
                               text=f"<b>{price_list['title']}</b>\n{price_list['description']}\n\n"
                                    f"<em>После оплаты нажми на кнопочку</em>\n👇🏻<b>Проверить оплату</b>👇🏻",
                               parse_mode='HTML',
                               disable_web_page_preview=True,
                               protect_content=True,
                               reply_markup=kb_client.ikb_quick(url, label, quickpay.id))


# @dp.callback_query_handler(kb_client.cb_check_quick.filter())
@dp.throttled(anti_flood, rate=3)
@logger.catch()
async def check_callback_quick(callback: types.CallbackQuery, callback_data: dict):
    label = callback_data['label']
    quick_id = callback_data['quick_id']
    info = await data_base.check_quick(quick_id)
    if info:
        if Payment.find_one(quick_id).status == 'succeeded':
            logger.info(f"Buy {label} User: {callback.from_user.first_name} Id: {callback.from_user.id}")
            if label == 'sub':
                link = await data_base.select_link(1)
                await bot.send_message(chat_id=callback.from_user.id,
                                       text='🫦Жду тебя🫦',
                                       reply_markup=kb_admin.get_link(link),
                                       disable_web_page_preview=True,
                                       protect_content=True)
                await data_base.del_quick(quick_id)
                await data_base.buy_sub(callback.from_user.id)
            elif label == 'contact':
                await data_base.del_quick(quick_id)
                await bot.send_message(chat_id=callback.from_user.id,
                                       text='Я с тобой свяжусь как можно скорей, до связи🤙🏻👄',
                                       protect_content=True)
                await bot.send_message(chat_id=ID_EVA_SUPPORT,
                                       text=f'{callback.from_user.first_name} хочет пообщаться\n'
                                            f'Его контак @{callback.from_user.username}',
                                       disable_web_page_preview=True,
                                       protect_content=True)
                await data_base.buy_contact(callback.from_user.id)
            elif label[:-1] == 'present':
                await data_base.del_quick(quick_id)
                present = await data_base.price_list(label)
                await bot.send_sticker(chat_id=callback.from_user.id,
                                       sticker='CAACAgIAAxkBAAEGOxpjW420O42YgbKjwS_WwLG1Vt4q4AAC1gcAAkb7rARW8D_bUpMSUyoE',
                                       protect_content=True)
                await bot.send_message(chat_id=callback.from_user.id,
                                       text=f'Спасибо за {present["name"]}, ты лучший😘',
                                       protect_content=True)
                await bot.send_message(chat_id=ID_EVA_SUPPORT,
                                       text=f'{callback.from_user.first_name} прислал в подарок {present["name"]}',
                                       reply_markup=kb_admin.get_ikb_present_answer(callback.from_user.id),
                                       disable_web_page_preview=True)
        else:
            await callback.answer(text='Не оплачено')
    else:
        await callback.message.delete()


@logger.catch()
def register_handlers_client_pay(disp: Dispatcher) -> None:
    disp.register_callback_query_handler(label_callback,
                                         kb_client.cb_label.filter())
    disp.register_callback_query_handler(pay_callback,
                                         kb_client.cb_pay.filter(payment='qiwi'))
    disp.register_callback_query_handler(check_callback_bill,
                                         kb_client.cb_check_bill.filter())
    disp.register_callback_query_handler(pay_kassa_callback,
                                         kb_client.cb_pay.filter(payment='kassa'))
    disp.register_callback_query_handler(check_callback_quick,
                                         kb_client.cb_check_quick.filter())
