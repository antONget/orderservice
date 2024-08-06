from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import keyboards.keyboard_admin_admins as kb
from filter.admin_filter import IsAdmin
import database.requests as rq

import logging
import asyncio

router = Router()


# АДМИНИСТРАТОРЫ
@router.message(F.text == 'Администраторы', IsAdmin())
async def process_change_list_admins(message: Message) -> None:
    """
    Действия с пользователями и администраторами
    :param message:
    :return:
    """
    logging.info(f'process_change_list_admins: {message.chat.id}')
    await message.answer(text='Назначить или разжаловать администратора?',
                         reply_markup=kb.keyboard_edit_list_admins())


# добавление администратора
@router.callback_query(F.data == 'add_admin')
async def process_add_admin(callback: CallbackQuery) -> None:
    """
    Список пользователей для назначения их администраторами
    :param callback:
    :return:
    """
    logging.info(f'process_add_admin: {callback.message.chat.id}')
    list_not_admin = [user for user in await rq.get_list_admins(is_admin=rq.UserRole.user)]
    keyboard = kb.keyboards_add_admin(list_not_admin=list_not_admin, back=0, forward=2, count=6)
    await callback.message.answer(text='Выберите пользователя, которого нужно назначить администратором',
                                  reply_markup=keyboard)
    await callback.answer()


# >>>>
@router.callback_query(F.data.startswith('adminforward'))
async def process_forwardadmin(callback: CallbackQuery) -> None:
    """
    Пагинация вперед по списку пользователей для назначения их администраторами
    :param callback:
    :return:
    """
    logging.info(f'process_forwardadmin: {callback.message.chat.id}')
    list_not_admin = [user for user in await rq.get_list_admins(is_admin=rq.UserRole.user)]
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    keyboard = kb.keyboards_add_admin(list_not_admin=list_not_admin, back=back, forward=forward, count=6)
    try:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите сделать администратором',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите пользователя, которого нужно сделать администратором',
                                         reply_markup=keyboard)
    await callback.answer()


# <<<<
@router.callback_query(F.data.startswith('adminback'))
async def process_backadmin(callback: CallbackQuery) -> None:
    """
    пагинация назад по списку пользователей для назначения их администраторами
    :param callback:
    :return:
    """
    logging.info(f'process_backadmin: {callback.message.chat.id}')
    list_not_admin = [user for user in await rq.get_list_admins(is_admin=rq.UserRole.user)]
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = kb.keyboards_add_admin(list_not_admin=list_not_admin, back=back, forward=forward, count=6)
    try:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите сделать администратором',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите пользователя, которого нужно сделать администратором',
                                         reply_markup=keyboard)
    await callback.answer()


# подтверждение добавления админа в список админов
@router.callback_query(F.data.startswith('adminadd'))
async def process_adminadd(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Подтверждение назначение пользователя администратором
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_adminadd: {callback.message.chat.id}')
    telegram_id = int(callback.data.split('_')[1])
    user_info = await rq.get_user_tg_id(tg_id=telegram_id)
    await state.update_data(add_admin_telegram_id=telegram_id)
    await callback.message.answer(text=f'Назначить пользователя {user_info.username} администратором',
                                  reply_markup=kb.keyboard_add_list_admins())
    await callback.answer()


# отмена добавления пользователя в список администраторов
@router.callback_query(F.data == 'notadd_admin_list')
async def process_notadd_admin_list(callback: CallbackQuery) -> None:
    """
    Отмена назначения пользователя администратором
    :param callback:
    :return:
    """
    logging.info(f'process_notadd_admin_list: {callback.message.chat.id}')
    await process_change_list_admins(callback.message)
    await callback.answer()


# удаление после подтверждения
@router.callback_query(F.data == 'add_admin_list')
async def process_add_admin_list(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Назначение пользователя администратором
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_add_admin_list: {callback.message.chat.id}')
    await callback.answer()
    data = await state.get_data()
    user_info = await rq.get_user_tg_id(data["add_admin_telegram_id"])
    await rq.set_role_user(int(data["add_admin_telegram_id"]), is_admin=1)
    await callback.message.answer(text=f'Пользователь {user_info.username} успешно назначен администратором')
    await asyncio.sleep(3)
    await process_change_list_admins(callback.message)


# разжалование администратора
@router.callback_query(F.data == 'delete_admin')
async def process_del_admin(callback: CallbackQuery) -> None:
    """
    Список пользователей для их разжалования
    :param callback:
    :return:
    """
    logging.info(f'process_del_admin: {callback.message.chat.id}')
    list_admin = [user for user in await rq.get_list_admins(is_admin=rq.UserRole.admin)]
    keyboard = kb.keyboards_del_admin(list_admin=list_admin, back=0, forward=2, count=6)
    await callback.message.answer(text='Выберите пользователя, которого нужно разжаловать',
                                  reply_markup=keyboard)
    await callback.answer()


# >>>>
@router.callback_query(F.data.startswith('admindelforward'))
async def process_forwarddeladmin(callback: CallbackQuery) -> None:
    """
    Пагинация вперед по списку администраторов для их разжалования
    :param callback:
    :return:
    """
    logging.info(f'process_forwarddeladmin: {callback.message.chat.id}')
    list_admin = [user for user in await rq.get_list_admins(is_admin=rq.UserRole.admin)]
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    keyboard = kb.keyboards_del_admin(list_admin=list_admin, back=back, forward=forward, count=6)
    try:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите разжаловать',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите пользователя, которого нужно разжаловать',
                                         reply_markup=keyboard)
    await callback.answer()


# <<<<
@router.callback_query(F.data.startswith('admindelback'))
async def process_backdeladmin(callback: CallbackQuery) -> None:
    """
    Пагинация назад по списку администраторов для их разжалования
    :param callback:
    :return:
    """
    logging.info(f'process_backdeladmin: {callback.message.chat.id}')
    list_admin = [user for user in await rq.get_list_admins(is_admin=rq.UserRole.admin)]
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = kb.keyboards_del_admin(list_admin=list_admin, back=back, forward=forward, count=6)
    try:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите разжаловать',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите пользователя, которого нужно разжаловать',
                                         reply_markup=keyboard)
    await callback.answer()


# подтверждение добавления админа в список админов
@router.callback_query(F.data.startswith('admindel'))
async def process_deleteuser(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Подтверждение разжалование администратора
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_deleteuser: {callback.message.chat.id}')
    telegram_id = int(callback.data.split('_')[1])
    user_info = await rq.get_user_tg_id(tg_id=telegram_id)
    await state.update_data(del_admin_telegram_id=telegram_id)
    await callback.message.answer(text=f'Разжаловать пользователя {user_info.username} из администраторов',
                                  reply_markup=kb.keyboard_del_list_admins())
    await callback.answer()


# отмена добавления пользователя в список администраторов
@router.callback_query(F.data == 'notdel_admin_list')
async def process_deleteuser(callback: CallbackQuery) -> None:
    """
    Отмена разжалования администратора
    :param callback:
    :return:
    """
    logging.info(f'process_deleteuser: {callback.message.chat.id}')
    await process_change_list_admins(callback.message)
    await callback.answer()


# удаление после подтверждения
@router.callback_query(F.data == 'del_admin_list')
async def process_description(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Меняем статус администратора на пользователя
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_description: {callback.message.chat.id}')
    await callback.answer()
    data = await state.get_data()
    user_info = await rq.get_user_tg_id(tg_id=data["del_admin_telegram_id"])
    await rq.set_role_user(telegram_id=int(data["del_admin_telegram_id"]), is_admin=rq.UserRole.user)
    await callback.message.answer(text=f'Пользователь {user_info.username} успешно разжалован')
    await asyncio.sleep(3)
    await process_change_list_admins(callback.message)
