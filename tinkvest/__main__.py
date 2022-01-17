"""
Provides some arithmetic functions
"""

import asyncio
from aiogram import executor

from tinkvest import tinkoff_broker_api
from .telegramm_bot import dp
from .utils.logger import logger
from .settings import HERE

logger = logger(module_name=__name__)
logger.info(f"HERE: {HERE}")


async def scheduler():
    """Планировщик"""
    pass
    # aioschedule.every(15).minutes.do(get_plot)
    # while True:
    #     await aioschedule.run_pending()
    #     await asyncio.sleep(1)


async def on_startup(_):
    """Функция, запускаемая вместе с start_polling"""
    await tinkoff_broker_api.ti_get_instruments()
    asyncio.create_task(scheduler())


def main():
    """main"""
    try:
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")


if __name__ == '__main__':
    main()
