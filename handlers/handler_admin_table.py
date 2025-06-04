from aiogram import Router, F
from aiogram.types import Message

from filter.admin_filter import IsAdmin
import database.requests as rq

import logging

router = Router()


@router.message(F.text == 'Таблица')
async def process_get_table(message: Message) -> None:
    """
    Выводим статистику для проекта
    :param message:
    :return:
    """
    logging.info(f'process_get_balans_admin: {message.chat.id}')
    # получаем статистику за всех пользователей
    list_orders = await rq.select_all_data_statistic()
    # проходим по всем выполненным заказам
    if list_orders:
        statistika = 'Таблица статистики\n'
        flag = True
        for i, item in enumerate(list_orders, start=1):
            flag = True
            statistika += f'{item.cost_order} {item.order_id} {item.username}\n'
            if not i % 40:
                flag = False
                await message.answer(text=statistika)
                statistika = ''
        if flag:
            await message.answer(text=statistika)
    else:
        await message.answer(text='Данные для статистики отсутствуют')
