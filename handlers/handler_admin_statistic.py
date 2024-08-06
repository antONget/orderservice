from aiogram import Router, F
from aiogram.types import Message

from filter.admin_filter import IsAdmin
import database.requests as rq

import logging

router = Router()


@router.message(F.text == 'Статистика', IsAdmin())
async def process_get_balans_admin(message: Message) -> None:
    """
    Выводим статистику для проекта
    :param message:
    :return:
    """
    logging.info(f'process_get_balans_admin: {message.chat.id}')
    list_orders = await rq.select_all_data_statistic()

    # list_statistics: [id, cost, count, player[@username.telegram_id]]
    if list_orders:
        total = {}
        for order in list_orders:
            list_player = order.players.split(',')
            for player in list_player:
                if player.split('.')[0] in total:
                    total[player.split('.')[0]] += order.cost_services
                else:
                    total[player.split('.')[0]] = order.cost_services
        statistika = ''
        balance = 0
        for key, value in total.items():
            statistika += f'@{key}: {value} руб.\n'
            balance += value
        await message.answer(text=f'<b>Статистика</b>:\n\n'
                                  f'{statistika}'
                                  f'ИТОГО: {balance}')
    else:
        await message.answer(text='Данные для статистики отсутствуют')


@router.message(F.text == 'Сброс статистики', IsAdmin())
async def process_reset_balans_admin(message: Message) -> None:
    logging.info(f'process_reset_balans_admin: {message.chat.id}')
    if await rq.check_statistic():
        await rq.delete_statistic()
        await message.answer(text='Статистика очищена')
    else:
        await message.answer(text='Статистика уже пуста')
