from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from filter.admin_filter import IsAdmin
import database.requests as rq
import keyboards.keyboard_admin_clear_busy as kb
router = Router()


@router.message(F.text == 'Скинуть занятость', IsAdmin())
async def process_change_channel(message: Message) -> None:
    """
    Очистить занятость
    :param message:
    :return:
    """
    users = await rq.get_all_users()
    message_text = ''
    if users:
        for user in users:
            if user.is_busy:
                executor = await rq.get_executor_tg_id_status(tg_id=user.telegram_id, status=rq.ExecutorStatus.done)
                if executor:
                    message_text += f'@{user.username} выполняет заказ № {executor.id_order}\n'
    if message_text:
        await message.answer(text=message_text,
                             reply_markup=kb.keyboard_busy())
    else:
        await message.answer(text='Занятых пользователей не найдено.')


@router.callback_query(F.data == 'clear_busy')
async def process_clear_data(callback: CallbackQuery):

    await rq.clear_stat()
    await callback.answer(text='Занятость всех пользователей обновлена', show_alert=True)
