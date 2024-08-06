from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from filter.admin_filter import IsAdmin
import keyboards.keyboard_admin_user as kb
import database.requests as rq

from secrets import token_urlsafe
import logging
import asyncio

router = Router()


# ПОЛЬЗОВАТЕЛЬ
@router.message(F.text == 'Пользователь', IsAdmin())
async def process_change_list_users(message: Message) -> None:
    logging.info(f'process_change_list_users: {message.chat.id}')
    """
    Функция позволяет удалять/добавлять пользователей из бота
    :param message:
    :return:
    """
    await message.answer(text='Добавить или удалить пользователя',
                         reply_markup=kb.keyboard_edit_list_user())


# добавить пользователя
@router.callback_query(F.data == 'add_user')
async def process_add_user(callback: CallbackQuery) -> None:
    logging.info(f'process_add_user: {callback.message.chat.id}')
    token_new = str(token_urlsafe(8))
    data = {"token_auth": token_new}
    await rq.add_token(data)
    await callback.message.answer(text=f'Для добавления пользователя в бот отправьте ему этот TOKEN'
                                       f' <code>{token_new}</code>.'
                                       f' По этому TOKEN может быть добавлен только один пользователь,'
                                       f' не делитесь и не показывайте его никому, кроме тех лиц для кого'
                                       f' он предназначен')
    await callback.answer()


# удалить пользователя
@router.callback_query(F.data == 'delete_user')
async def process_description(callback: CallbackQuery) -> None:
    logging.info(f'process_description: {callback.message.chat.id}')
    list_users = [user for user in await rq.get_all_users()]
    keyboard = kb.keyboards_del_users(list_users=list_users, back=0, forward=2, count=6)
    await callback.message.answer(text='Выберите пользователя, которого вы хотите удалить',
                                  reply_markup=keyboard)
    await callback.answer()


# >>>>
@router.callback_query(F.data.startswith('forward'))
async def process_forward(callback: CallbackQuery) -> None:
    logging.info(f'process_forward: {callback.message.chat.id}')
    list_users = [user for user in await rq.get_all_users()]
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    keyboard = kb.keyboards_del_users(list_users=list_users, back=back, forward=forward, count=6)
    try:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите удалить',
                                         reply_markup=keyboard)
    except IndexError:
        await callback.message.edit_text(text='Выберите пользователя, которого нужно удалить',
                                         reply_markup=keyboard)
    await callback.answer()


# <<<<
@router.callback_query(F.data.startswith('back'))
async def process_back(callback: CallbackQuery) -> None:
    logging.info(f'process_back: {callback.message.chat.id}')
    list_users = [user for user in await rq.get_all_users()]
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = kb.keyboards_del_users(list_users=list_users, back=back, forward=forward, count=6)
    try:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите удалить',
                                         reply_markup=keyboard)
    except IndexError:
        await callback.message.edit_text(text='Выберите пользователя, которого нужно удалить',
                                         reply_markup=keyboard)
    await callback.answer()


# подтверждение удаления пользователя из базы
@router.callback_query(F.data.startswith('deleteuser'))
async def process_deleteuser(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_deleteuser: {callback.message.chat.id}')
    telegram_id = int(callback.data.split('_')[1])
    user_info = await rq.get_user_tg_id(tg_id=callback.message.chat.id)
    await state.update_data(del_telegram_id=telegram_id)
    await callback.message.answer(text=f'Удалить пользователя {user_info.username}',
                                  reply_markup=kb.keyboard_delete_user())


# отмена удаления пользователя
@router.callback_query(F.data == 'notdel_user')
async def process_notdel_user(callback: CallbackQuery) -> None:
    logging.info(f'process_notdel_user: {callback.message.chat.id}')
    await process_change_list_users(callback.message)
    await callback.answer()


# удаление после подтверждения
@router.callback_query(F.data == 'del_user')
async def process_descriptiondel_user(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_descriptiondel_user: {callback.message.chat.id}')
    data = await state.get_data()
    user_info = await rq.get_user_tg_id(data["del_telegram_id"])
    await rq.delete_user(data["del_telegram_id"])
    await callback.message.answer(text=f'Пользователь {user_info.username} успешно удален')
    await asyncio.sleep(3)
    await process_change_list_users(callback.message)
    await callback.answer()
