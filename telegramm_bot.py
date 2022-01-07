from aiogram import Bot, Dispatcher, types
import logging
import requests
import asyncio

from project_secrets.tokens import TELEGRAMM_TOKEN
from utils.tests import factorial
from utils.talker import talker_answer

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAMM_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Обработчик команд /start и /help"""
    task = asyncio.create_task(factorial(name="telegramm", number=3))
    done, pending = await asyncio.wait({task})
    if task in done:
        result = task.result()
        await message.reply(str(result))


@dp.message_handler(regexp='(^cat[s]?$|puss)')
async def cats(message: types.Message):
    """Тест отправки картинки"""
    url = "https://github.com/aiogram/aiogram/raw/dev-2.x/examples/data/cats.jpg"
    response = requests.get(url)
    await message.reply_photo(response.content, caption='Cats are here 😺')


@dp.message_handler()
async def echo(message: types.Message):
    """Обработчик всех остальных ответов"""
    await message.answer(talker_answer(message.text))
