from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import pytz
import datetime
import logging
from config_data.config import Config, load_config
from keyboards.user_keyboard import keyboards_start, keyboards_subscription, keyboards_get_phone, keyboards_question
from services.googlesheets import append_user, append_client
import asyncio
import requests

router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()


class User(StatesGroup):
    get_name = State()
    get_phone = State()
    info_user = State()


user_dict = {}


def get_telegram_user(user_id, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    print(response.json())
    return response.json()


@router.message(CommandStart())
async def process_start_command_user(message: Message) -> None:
    logging.info(f'process_start_command_user: {message.chat.id}')
    tz_moscow = pytz.timezone("Europe/Moscow")
    dt_moscow = str(datetime.datetime.now(tz_moscow)).split()[0]
    append_user(message.chat.id, message.from_user.username, dt_moscow)
    await message.answer(text=f'Благодарим Вас за покупку нашего товара! Если у вас есть вопросы как его принимать'
                              f' или вы желаете узнать больше о спортивных добавках это бот поможет вам.',
                         reply_markup=keyboards_start())


@router.message(F.text == 'Канал')
async def process_press_chanel(message: Message) -> None:
    logging.info(f'process_press_chanel: {message.chat.id}')
    await message.answer(text=f'Сопроводительный текст с призывом подписаться на канал'
                              f' <a href="{config.tg_bot.channel}">канал для подписки</a>')


@router.message(F.text == 'Консультация')
async def process_press_consultation(message: Message, bot: Bot, state: FSMContext) -> None:
    logging.info(f'process_press_consultation: {message.chat.id}')
    await message.answer(text=f'Задайте свой вопрос квалифицированному нутрициологу, оставьте ваши контакты'
                              f' и подпишитесь на наш Телеграм-канал: '
                              f'<a href="{config.tg_bot.channel}">канал для подписки</a>',
                         disable_web_page_preview=True,
                         parse_mode='HTML')
    user_channel_status = await bot.get_chat_member(chat_id=config.tg_bot.channel, user_id=message.from_user.id)
    if user_channel_status.status != 'left':
        await asyncio.sleep(2)
        await message.answer(text=f'Введите ваше имя:')
        await state.set_state(User.get_name)
    else:
        await message.answer(text=f'Для получения консультации подпишись на канал: '
                                  f'<a href="{config.tg_bot.channel}">канал для подписки</a>',
                             reply_markup=keyboards_subscription(),
                             parse_mode='HTML')


@router.callback_query(F.data=='subscription')
async def process_press_subscription(callback: CallbackQuery, bot: Bot, state: FSMContext):
    logging.info(f'process_press_subscription: {callback.message.chat.id}')
    user_channel_status = await bot.get_chat_member(chat_id=config.tg_bot.channel, user_id=callback.message.from_user.id)
    if user_channel_status.status != 'left':
        await asyncio.sleep(2)
        await callback.message.answer(text=f'Введите ваше имя:')
        await state.set_state(User.get_name)
    else:
        await callback.message.answer(text=f'Для получения консультации подпишись на канал: '
                                           f'<a href="{config.tg_bot.channel}">канал для подписки</a>',
                                      reply_markup=keyboards_subscription(),
                                      parse_mode='HTML')


@router.message(F.text, StateFilter(User.get_name))
async def get_name_user(message: Message, state: FSMContext) -> None:
    logging.info(f'get_name_user: {message.chat.id}')
    await state.update_data(name_user=message.text)
    await message.answer(text=f'Введите ваш контактный телефон или нажмите «Поделиться контактом» ⤵️',
                         reply_markup=keyboards_get_phone())
    await state.set_state(User.get_phone)


@router.message(StateFilter(User.get_phone))
async def get_phone_user(message: Message, state: FSMContext) -> None:
    logging.info(f'get_phone_user: {message.chat.id}')
    if message.contact:
        phone = message.contact.phone_number
        print(phone)
    else:
        phone = message.text
    await state.update_data(phone_user=phone)
    await message.answer(text=f'Задайте ваш вопрос')
    await state.set_state(User.info_user)


@router.message(StateFilter(User.info_user))
async def get_info_user(message: Message, state: FSMContext, bot: Bot) -> None:
    logging.info(f'get_info_user: {message.chat.id}')
    await state.update_data(info=message.text)
    user_dict[message.chat.id] = await state.get_data()
    print('id_telegram=', message.chat.id,
          'user_name=', message.from_user.username,
          'name=', user_dict[message.chat.id]['name_user'],
          'phone=', user_dict[message.chat.id]['phone_user'],
          'info_user=', user_dict[message.chat.id]['info'])
    append_client(id_telegram=message.chat.id,
                  user_name=message.from_user.username,
                  name=user_dict[message.chat.id]['name_user'],
                  phone=user_dict[message.chat.id]['phone_user'],
                  info=user_dict[message.chat.id]['info'])

    channel = get_telegram_user(user_id=config.tg_bot.group_id, bot_token=config.tg_bot.token)
    if 'result' in channel:
        await bot.send_message(chat_id=config.tg_bot.group_id,
                               text=f'Telegram_id: {message.chat.id}\n'
                                    f'@username: {message.from_user.username}\n'
                                    f'Имя: {user_dict[message.chat.id]["name_user"]}\n'
                                    f'Телефон: {user_dict[message.chat.id]["phone_user"]}\n'
                                    f'Комментарий: {user_dict[message.chat.id]["info"]}')

    await message.answer(text=f'Благодарим!\n'
                              f'В ближайшее время с вами свяжется нутрициолог для согласования'
                              f' удобного времени и записи на диагностику.')


@router.message(F.text == 'FAQ')
async def process_press_FAQ(message: Message) -> None:
    logging.info(f'process_press_FAQ: {message.chat.id}')
    await message.answer(text=f'Список вопросов и ответов на них',
                         reply_markup=keyboards_question())

question = {
    "1 Вопрос_1?": "Ответ на вопрос 1",
    "2 Вопрос_2?": "Ответ на вопрос 2",
    "3 Вопрос_3?": "Ответ на вопрос 3",
    "4 Вопрос_4?": "Ответ на вопрос 4",
    "5 Вопрос_5?": "Ответ на вопрос 5",
}


@router.callback_query(F.data.startswith('question_'))
async def process_press_question(callback: CallbackQuery, bot: Bot, state: FSMContext):
    logging.info(f'process_press_question: {callback.message.chat.id}')
    num_question = callback.data.split('_')[1]
    for key, value in question.items():
        print('num_question', num_question, 'key', key, 'value', value, )
        if num_question == key.split()[0]:
            await callback.message.answer(text=f'<b>{key}</b>\n\n'
                                               f'{value}',
                                          parse_mode='html')




