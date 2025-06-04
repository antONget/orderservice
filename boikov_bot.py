from aiogram import Bot, Dispatcher
from aiogram.types import FSInputFile
from aiogram.types import ErrorEvent
from aiogram.client.default import DefaultBotProperties
from handlers import handler_admin_main, handler_user_main, handler_admin_user, handler_admin_admins, \
    handler_admin_clear_busy, handler_admin_statistic, handler_admin_resource, \
    handler_admin_order_add, handler_admin_order_select, handler_admin_order_change, handler_admin_table
from handlers import other_handlers
from database.models import async_main
from config_data.config import Config, load_config

import traceback
import asyncio
import logging
# Инициализируем logger
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    await async_main()
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        filename="py_log.log",
        filemode='w',
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()

    # Регистрируем router в диспетчере
    dp.include_router(handler_admin_main.router)
    dp.include_router(handler_admin_user.router)
    dp.include_router(handler_admin_admins.router)
    dp.include_router(handler_admin_clear_busy.router)
    dp.include_router(handler_admin_statistic.router)
    dp.include_router(handler_admin_resource.router)
    dp.include_router(handler_admin_order_add.router)
    dp.include_router(handler_admin_order_change.router)
    dp.include_router(handler_admin_order_select.router)
    dp.include_router(handler_admin_table.router)
    dp.include_router(handler_user_main.router)
    dp.include_router(other_handlers.router)

    @dp.error()
    async def error_handler(event: ErrorEvent):
        logger.critical("Критическая ошибка: %s", event.exception, exc_info=True)
        await bot.send_message(chat_id=config.tg_bot.support_id,
                               text=f'{event.exception}')
        formatted_lines = traceback.format_exc()
        text_file = open('error.txt', 'w')
        text_file.write(str(formatted_lines))
        text_file.close()
        await bot.send_document(chat_id=config.tg_bot.support_id,
                                document=FSInputFile('error.txt'))

    # Пропускаем накопившиеся update и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
