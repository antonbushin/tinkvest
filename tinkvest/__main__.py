"""main"""

import asyncio
import aioschedule
from aiogram import executor

from tinkvest import tinkoff_broker_api
from tinkvest.telegramm_bot import dp
from tinkvest.utils.logger import logger
from tinkvest.constants import HERE
from tinkvest.algotraiding import get_plot

logger = logger(__name__)
logger.info("HERE: %s", HERE)


async def scheduler():
    """Планировщик"""
    aioschedule.every(1).hours.do(get_plot)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    """Функция, запускаемая вместе с start_polling"""
    await tinkoff_broker_api.ti_get_instruments()
    asyncio.create_task(scheduler())


def main():
    """main"""
    try:
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    except (KeyboardInterrupt, SystemExit) as e:
        logger.error("Bot stopped!")
        raise e


if __name__ == '__main__':
    main()
