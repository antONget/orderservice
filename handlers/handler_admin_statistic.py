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

    # list_statistics: [id, tg_id, cost_order, order_id]
    if list_orders:
        total = {}
        for order in list_orders:
            if order.tg_id in total:
                total[order.tg_id] += order.cost_order
            else:
                total[order.tg_id] = order.cost_order
        statistika = ''
        balance = 0
        for key, value in total.items():
            user = await rq.get_user_tg_id(tg_id=key)
            statistika += f'@{user.username}: {value} руб.\n'
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
