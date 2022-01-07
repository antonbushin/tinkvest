import asyncio
from telegramm_bot import dp


async def scheduled(wait_for):
    while True:
        await asyncio.sleep(wait_for)

        print('Время пришло!')


async def main():
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
