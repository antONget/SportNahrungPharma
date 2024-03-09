import logging
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

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
    button_6 = InlineKeyboardButton(text='Вопрос 6', callback_data='question_6')
    button_7 = InlineKeyboardButton(text='Вопрос 7', callback_data='question_7')
    button_8 = InlineKeyboardButton(text='Вопрос 8', callback_data='question_8')
    button_9 = InlineKeyboardButton(text='Вопрос 9', callback_data='question_9')
    button_10 = InlineKeyboardButton(text='Вопрос 10', callback_data='question_10')
    button_11 = InlineKeyboardButton(text='Вопрос 11', callback_data='question_11')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_4], [button_5],
                                                     [button_6], [button_7], [button_8], [button_9], [button_10],
                                                     [button_11]], )
    return keyboard


def keyboards_select_question(dict_question: dict):
    logging.info(f'keyboards_select_question')

    kb_builder = InlineKeyboardBuilder()
    buttons = []
    i = 0
    for question in dict_question.keys():
        i += 1
        button = f'question_{i}'
        buttons.append(InlineKeyboardButton(
            text=question,
            callback_data=button))
    # button_back = InlineKeyboardButton(text='<<<<',
    #                                    callback_data=f'serviceselectback_{str(back)}')
    # button_count = InlineKeyboardButton(text=f'{back+1}',
    #                                     callback_data='none')
    # button_next = InlineKeyboardButton(text='>>>>',
    #                                    callback_data=f'serviceselectforward_{str(forward)}')

    kb_builder.row(*buttons, width=1)
    # kb_builder.row(button_back, button_count, button_next)

    return kb_builder.as_markup()