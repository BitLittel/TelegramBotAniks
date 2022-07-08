# -*- coding: utf-8 -*-

import asyncio
from main_bot import dp, bot
from check_answer import set_scheduled_jobs
from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def main():
    # инициализируем наш хендлер
    scheduler = AsyncIOScheduler()
    # забиваем задучу
    set_scheduled_jobs(scheduler, bot)
    # запуск бота
    try:
        # запускаем хендлер
        scheduler.start()
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")

# if __name__ == '__main__':
#     executor.start_polling(dp, skip_updates=True, on_startup=create_task_check_answer)
