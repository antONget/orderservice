from aiogram import Router, F
from aiogram.types import Message

from filter.admin_filter import IsAdmin
import database.requests as rq

router = Router()


@router.message(F.text == 'Скинуть занятость', IsAdmin())
async def process_change_channel(message: Message) -> None:
    """
    Очистить занятость
    :param message:
    :return:
    """
    await rq.clear_stat()
    await message.answer(text='Занятость всех пользователей обновлена')
