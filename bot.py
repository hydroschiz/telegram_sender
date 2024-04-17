import asyncio
import logging
import sys

from loader import dp, bot


async def main() -> None:
    dp.include_routers(
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
