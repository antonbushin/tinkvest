"""Реализация поведения Телеграм-бота с aiogram"""

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import markdown as md
import requests

from tinkvest.project_secrets.tokens import TELEGRAMM_TOKEN
from tinkvest.utils.talker import talker_answer
from tinkvest.tinkoff_broker_api import session_data
from tinkvest.utils.logger import logger
from tinkvest import constants

logger = logger(__name__)

bot = Bot(token=TELEGRAMM_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.inline_handler()
async def inline_echo(inline_query: types.InlineQuery):
    """Обработка запросов inline_query"""
    text = inline_query.query or "A"
    print("text:", text)
    items = []
    for i in session_data.instruments:
        if text.lower() in i.ticker.lower() or text.lower() in i.name.lower():
            items.append(types.InlineQueryResultArticle(
                id=i.figi,
                title=f"{i.ticker} ({i.type})",
                description=i.name,
                url=f"https://www.tinkoff.ru/invest/stocks/{i.ticker}/",
                input_message_content=types.InputTextMessageContent(
                    message_text=f"[{i.ticker}](https://www.tinkoff.ru/invest/stocks/{i.ticker})",
                    parse_mode=ParseMode.MARKDOWN
                )
            ))
    await bot.answer_inline_query(inline_query.id,
                                  results=items[:50],
                                  cache_time=1,
                                  switch_pm_text="❔ Помощь",
                                  switch_pm_parameter="ticker",
                                  )


@dp.chosen_inline_handler()
async def chosen_handler(chosen_result: types.ChosenInlineResult):
    """Обработка результатов выбора inline_query"""
    res = chosen_result
    logger.info("result_id: %s, query: %s, user.id: %s", res.result_id, res.query, res.from_user.id)


# States
class WelcomeForm(StatesGroup):
    """Приветственная форма"""
    name = State()
    age = State()
    gender = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    """Обработка команды start"""
    await WelcomeForm.name.set()
    await message.reply("Привет! Как тебя зовут?")


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals=constants.STOP_WORDS, ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """Позволяет выйти из сценария"""
    current_state = await state.get_state()
    if current_state is None:
        return

    logger.info('Cancelling state %r', current_state)
    await state.finish()
    await message.reply('Ок, закончили', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=WelcomeForm.name)
async def process_name(message: types.Message, state: FSMContext):
    """Сохранение имени пользователя"""
    async with state.proxy() as data:
        data['name'] = message.text

    await WelcomeForm.next()
    await message.reply("Сколько тебе лет?")


@dp.message_handler(lambda message: not message.text.isdigit(), state=WelcomeForm.age)
async def process_age_invalid(message: types.Message):
    """Валидация возраста пользователя"""
    return await message.reply("Возраст должен быть числом.\nСколько тебе лет? (Только цифры)")


@dp.message_handler(lambda message: message.text.isdigit(), state=WelcomeForm.age)
async def process_age(message: types.Message, state: FSMContext):
    """Сохранение возраста пользователя"""
    await WelcomeForm.next()
    await state.update_data(age=int(message.text))

    # Configure ReplyKeyboardMarkup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Мужской", "Женский")
    markup.add("Другой")

    await message.reply("Какоой у тебя пол?", reply_markup=markup)


@dp.message_handler(lambda message: message.text not in constants.GENDERS, state=WelcomeForm.gender)
async def process_gender_invalid(message: types.Message):
    """Валидация пола пользователя"""
    return await message.reply("Неподходящий под мои стандарты пол. Выбери пол с клавиатуры")


@dp.message_handler(state=WelcomeForm.gender)
async def process_gender(message: types.Message, state: FSMContext):
    """Сохранение пола пользователя и вывод приветствия"""
    async with state.proxy() as data:
        data['gender'] = message.text
        markup = types.ReplyKeyboardRemove()

        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('Ок, рад знакомству,', md.bold(data['name'])),
                md.text('Возраст:', md.code(data['age'])),
                md.text('Пол:', data['gender']),
                sep='\n',
            ),
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )

    # Finish conversation
    await state.finish()


@dp.message_handler(regexp='(^cat[s]?$|puss)')
async def cats(message: types.Message):
    """Тест отправки картинки"""
    url = "https://github.com/aiogram/aiogram/raw/dev-2.x/examples/data/cats.jpg"
    response = requests.get(url)
    await message.reply_photo(response.content, caption='Cats are here 😺')


async def send_message_by_user_id(chat_id: int = None, caption: str = "qwe", filename: str = None):
    """Отправка сообщения в конкретный чат (173585407)"""
    if not chat_id:
        return
    print("send_message_by_user_id start")
    if filename:
        print("in filename")
        with open(filename, 'rb') as photo:
            print("in with")
            response = await bot.send_photo(chat_id=chat_id, photo=photo, caption=caption)
            print("response:", response)


@dp.message_handler()
async def echo(message: types.Message):
    """Обработчик всех остальных ответов"""
    await message.answer(talker_answer(message.text))
