import logging
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup


def keyboards_start():
    logging.info("keyboards_superadmin")
    button_1 = KeyboardButton(text='Канал')
    button_2 = KeyboardButton(text='Консультация')
    button_3 = KeyboardButton(text='FAQ')
    button_4 = KeyboardButton(text='Каталог',
                              web_app=WebAppInfo(url='https://www.wildberries.ru/brands/sport-nahrung-pharma'))
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1, button_2], [button_3, button_4]],
        resize_keyboard=True
    )
    return keyboard


def keyboards_subscription():
    button_1 = InlineKeyboardButton(text='Я подписался', callback_data='subscription')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]], )
    return keyboard


def keyboards_get_phone():
    button_1 = KeyboardButton(text='Поделиться контактом ☎️', request_contact=True)
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1]], resize_keyboard=True)
    return keyboard


def keyboards_question():
    button_1 = InlineKeyboardButton(text='Вопрос 1', callback_data='question_1')
    button_2 = InlineKeyboardButton(text='Вопрос 2', callback_data='question_2')
    button_3 = InlineKeyboardButton(text='Вопрос 3', callback_data='question_3')
    button_4 = InlineKeyboardButton(text='Вопрос 4', callback_data='question_4')
    button_5 = InlineKeyboardButton(text='Вопрос 5', callback_data='question_5')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_4], [button_5]], )
    return keyboard