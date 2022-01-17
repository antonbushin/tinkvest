from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import DEFAULT_RATE_LIMIT, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import ParseMode
from aiogram.utils import markdown as md
from aiogram.utils.exceptions import Throttled
import logging
import requests
import asyncio

from tinkvest.project_secrets.tokens import TELEGRAMM_TOKEN
from tinkvest.utils.talker import talker_answer
from tinkvest.tinkoff_broker_api import session_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAMM_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.inline_handler()
async def inline_echo(inline_query: types.InlineQuery):
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
    res = chosen_result
    logging.info(f"{res.result_id} ({res.query}), u: {res.from_user.id}")


# States
class Form(StatesGroup):
    name = State()
    age = State()
    gender = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await Form.name.set()
    await message.reply("Привет! Как тебя зовут?")


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """Allow user to cancel any action"""
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.reply('Закончили', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    """Process user name"""
    async with state.proxy() as data:
        data['name'] = message.text

    await Form.next()
    await message.reply("Сколько тебе лет?")


@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.age)
async def process_age_invalid(message: types.Message):
    """If age is invalid"""
    return await message.reply("Возраст должен быть числом.\nСколько тебе лет? (Только цифры)")


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    # Update state and data
    await Form.next()
    await state.update_data(age=int(message.text))

    # Configure ReplyKeyboardMarkup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Мужской", "Женский")
    markup.add("Другой")

    await message.reply("Какоой у тебя пол?", reply_markup=markup)


@dp.message_handler(lambda message: message.text not in ["Мужской", "Женский", "Другой"], state=Form.gender)
async def process_gender_invalid(message: types.Message):
    return await message.reply("Неподходящий под мои стандарты пол. Выбери пол с клавиатуры")


@dp.message_handler(state=Form.gender)
async def process_gender(message: types.Message, state: FSMContext):
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


def rate_limit(limit: int, key=None):
    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func

    return decorator


class ThrottlingMiddleware(BaseMiddleware):
    """https://github.com/aiogram/aiogram/blob/dev-2.x/examples/middleware_and_antiflood.py"""

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        """This handler is called when dispatcher receives a message"""
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            await self.message_throttled(message, t)

            raise CancelHandler()

    async def message_throttled(self, message: types.Message, throttled: Throttled):
        """Notify user only on first exceed and notify about unlocking only on last exceed"""
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            key = f"{self.prefix}_message"

        delta = throttled.rate - throttled.delta

        if throttled.exceeded_count <= 2:
            await message.reply('Too many requests! ')

        await asyncio.sleep(delta)

        thr = await dispatcher.check_key(key)

        if thr.exceeded_count == throttled.exceeded_count:
            await message.reply('Unlocked.')


@dp.message_handler(commands=['start'])
@rate_limit(5, 'start')
async def cmd_test(message: types.Message):
    await message.reply('Test passed! You can use this command every 5 seconds.')


@dp.message_handler(regexp='(^cat[s]?$|puss)')
async def cats(message: types.Message):
    """Тест отправки картинки"""
    url = "https://github.com/aiogram/aiogram/raw/dev-2.x/examples/data/cats.jpg"
    response = requests.get(url)
    await message.reply_photo(response.content, caption='Cats are here 😺')


async def send_message_by_user_id(chat_id: int = 173585407, caption: str = "qwe", filename: str = None):
    # await bot.send_message(chat_id=chat_id, text=text)
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
