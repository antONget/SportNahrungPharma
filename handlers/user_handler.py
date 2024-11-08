from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state

import pytz
import datetime
import logging
from config_data.config import Config, load_config
from keyboards.user_keyboard import keyboards_start, keyboards_get_phone, keyboards_select_question
from services.googlesheets import append_user, append_client
import requests
import re

router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()


class User(StatesGroup):
    question_user = State()
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


def validate_russian_phone_number(phone_number):
    # Паттерн для российских номеров телефона
    # Российские номера могут начинаться с +7, 8, или без кода страны
    pattern = re.compile(r'^(\+7|8|7)?(\d{10})$')

    # Проверка соответствия паттерну
    match = pattern.match(phone_number)

    return bool(match)


@router.message(CommandStart())
async def process_start_command_user(message: Message) -> None:
    """
    Нажата команда СТАРТ - запуск бота
    :param message:
    :return:
    """
    logging.info(f'process_start_command_user: {message.chat.id}')
    tz_moscow = pytz.timezone("Europe/Moscow")
    dt_moscow = str(datetime.datetime.now(tz_moscow)).split()[0]
    append_user(message.chat.id, message.from_user.username, dt_moscow)
    await message.answer(text=f'Благодарим за обращение. Если Вы хотите задать вопрос нутрициологу, нажмите на кнопку'
                              f' "Консультация"',
                         reply_markup=keyboards_start())


@router.message(F.text == 'Канал')
async def process_press_chanel(message: Message) -> None:
    """
    Нажата кнопка "Канал" - предоставляем ссылку на канал
    :param message:
    :return:
    """
    logging.info(f'process_press_chanel: {message.chat.id}')
    await message.answer(text=f'Здравствуйте, подпишитесь на канал'
                              f' <a href="https://t.me/{config.tg_bot.channel}">{config.tg_bot.channel}</a>.'
                              f' На канале выкладываем всю актуальную информацию о здоровье, похудении,'
                              f' добавках и правильном питании!',
                         disable_web_page_preview=True,
                         parse_mode='HTML')


@router.message(F.text == 'Консультация')
async def process_press_consultation(message: Message, state: FSMContext) -> None:
    """
    Нажата кнопка "Консультация" - Просьба ввести вопрос
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_press_consultation: {message.chat.id}')
    await message.answer(text=f'Напишите Ваш вопрос. Продолжая, вы соглашаетесь с условиями:\n'
                              f'<a href="https://telegra.ph/POLZOVATELSKOE-SOGLASHENIE-OB-OBRABOTKE-PERSONALNYH-DANNYH'
                              f'-03-11">Пользовательского соглашения</a>',
                         disable_web_page_preview=True,
                         parse_mode='HTML')
    await state.set_state(User.question_user)


@router.message(F.text, StateFilter(User.question_user))
async def process_press_consultation(message: Message, state: FSMContext) -> None:
    """
    Получаем вопрос и запрашиваем имя
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_press_consultation: {message.chat.id}')
    await state.update_data(question=message.text)
    await message.answer(text=f'Напишите Ваше имя')
    await state.set_state(User.get_name)


@router.message(F.text, StateFilter(User.get_name))
async def get_name_user(message: Message, state: FSMContext) -> None:
    """
    Получаем имя и запрашиваем номер телефона
    :param message:
    :param state:
    :return:
    """
    logging.info(f'get_name_user: {message.chat.id}')
    await state.update_data(name_user=message.text)
    await message.answer(text=f'Напишите Ваш номер телефона',
                         reply_markup=keyboards_get_phone())
    await state.set_state(User.get_phone)


@router.message(StateFilter(User.get_phone))
async def get_phone_user(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем номер телефона (проверяем его) и отправляем данные в канал
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_phone_user: {message.chat.id}')
    if message.contact:
        phone = str(message.contact.phone_number)
    else:
        phone = message.text
        if not validate_russian_phone_number(phone):
            await message.answer(text="Неверный формат номера. Повторите ввод:")
            return
    await state.update_data(phone_user=phone)
    await message.answer(text=f'Мы приняли заявку, в течение дня с Вами свяжется нутрициолог. Благодарим за обращение!',
                         reply_markup=keyboards_start())
    await state.set_state(User.info_user)
    await state.update_data(info=message.text)
    user_dict[message.chat.id] = await state.get_data()
    append_client(id_telegram=message.chat.id,
                  user_name=message.from_user.username,
                  name=user_dict[message.chat.id]['name_user'],
                  phone=user_dict[message.chat.id]['phone_user'],
                  info=user_dict[message.chat.id]['question'])

    channel = get_telegram_user(user_id=config.tg_bot.group_id, bot_token=config.tg_bot.token)
    if 'result' in channel:
        await bot.send_message(chat_id=config.tg_bot.group_id,
                               text=f'Telegram_id: {message.chat.id}\n'
                                    f'username: @{message.from_user.username}\n'
                                    f'Имя: {user_dict[message.chat.id]["name_user"]}\n'
                                    f'Телефон: {user_dict[message.chat.id]["phone_user"]}\n'
                                    f'Вопрос: {user_dict[message.chat.id]["question"]}')

    # await message.answer(text=f'Благодарим! В ближайшее время с Вами свяжется нутрициолог и ответит на Ваш вопрос')
    await state.set_state(default_state)


question = {
    "1. Почему неприятно пахнет из банки L-Carnitine 750 SNP?":
        "Сам главный компонент L карнитин тартрат имеет сильно неприятный запах, напоминающий запах рыбы и в какой-то"
        " степени сырое мясо (с лат. carni - мясо). К тому же капсула нашего продукта L-Carnitine 750 SNP не содержит"
        " примесей и наполнителей, поэтому в составе чистый l карнитин тартрат.",
    "2. Как принимать L-Carnitine 750 SNP?":
        "Наш продукт следует принимать за 30 мин до тренировки, поскольку к этому времени карнитин попадает в кровь,"
        " а пик его достигает через 2 часа после применения.",
    "3. Можно ли принимать L-Carnitine 750 SNP в дни без тренировок?":
        "Л карнитин следует принимать в тренировочные дни. Без тренировок жиры не будут поступать в кровь и в мышцы,"
        " и л карнитину нечего будет переносить в митохондрии мышечных клеток. Ведь именно в мышцах  жиры сгорают,"
        " когда там требуется энергия, т.е существует дефецит. НО, если Вы активный человек и часто гуляете или"
        " передвигаетесь пешком по 40-60 мин, то наш продукт увеличит сжигание жиров, т.е в такие дни можно применять.",
    "4. Можно ли принимать L-Carnitine 750 SNP детям?":
        "Сам компонент нашего продукта л карнитин тартрат безопасен. Конкретно наш продукт не изучался в исследованиях"
        " при применении у детей. Но есть лекарственные препараты с таким же составом,  которые изучались."
        " Поскольку наш продукт является специализированным продуктом питания спортсменов, то лучше"
        " проконсультироваться со спортивным врачом и лечащим.",
    "5. Почему содержимое капсулы L-Carnitine 750 SNP имеет кислый вкус? Это что лимонная кислота?":
        "Сам компонент нашего продукта l карнитин тартрат - соль, состоящая из базы l карнитина и основания"
        " виноградная кислота. Виноградная кислота имеет кислый вкус, потому что это кислота. l карнитин тартрат имеет"
        " кислый вкус из-за виноградной кислоты",
    "6. Почему L-Carnitine 750 SNP не работает?":
        "Продукт работает, многие наши покупатели получили положительный эффект в виде похудения. Вы можете задать"
        " вопрос нутрициологу и он сможет выяснить из-за чего не получен нужный эффект",
    "7. Сколько нужно пить капсул L-Carnitine 750 SNP?":
        "Оптимально 1-2 капсулы в день перед тренировкой. Но все индивидуально, иногда нужно подобрать свою дозу.",
    "8. Смогу ли я похудеть принимая L-Carnitine 750 SNP?":
        "L-Carnitine 750 SNP работает и Вы сможете похудеть. Но нужно понимать, что сами жиры сгорают при дефеците"
        " калорий, т.е оптимально их можно создать занимаясь спортом и организуя свой рацион питания правильно, так,"
        " например, важно снизить потребление углеводной пищи",
    "9. Какие тренировки должны быть при применении L-Carnitine 750 SNP?":
        "Лучше использовать кардио нагрузки, т.к при таких тренировка происходит сгорание именно жиров.",
    "10. Можно ли L-Carnitine 750 SNP сочетат с другими добавками?":
        "L-Carnitine 750 SNP - безопасный продукт, нет данных о неготивном взаимодействии с другими веществами,"
        " поэтому можно принимать вместе с другими добавками.",
    "11. Разве L-Carnitine 750 SNP является жиросжигателем?":
        "L-Carnitine 750 SNP переносит жирные кислоты в мышечных клетках в митохондрии, где они сгорают с образованием"
        " энергии, воды и углекислого газа. Так это и есть настоящий жиросжигатель. Понятие 'жиросжигатель' это"
        " образное, такие компоненты лишь выгоняют жиры из жирового депо в кровь, и то опосредовано. И если нет"
        " тренировок, то жиры вернуться обратно в жир."
}


@router.message(F.text == 'FAQ')
async def process_press_faq(message: Message) -> None:
    logging.info(f'process_press_FAQ: {message.chat.id}')
    await message.answer(text=f'Список вопросов и ответов на них',
                         reply_markup=keyboards_select_question(question))


@router.callback_query(F.data.startswith('question_'))
async def process_press_question(callback: CallbackQuery):
    logging.info(f'process_press_question: {callback.message.chat.id}')
    num_question = callback.data.split('_')[1]
    for key, value in question.items():
        if num_question == key.split('.')[0]:
            await callback.message.answer(text=f'<b>{key}</b>\n\n'
                                               f'{value}',
                                          parse_mode='html')
