from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message
from lexicon.lexicon_ru import MESSAGE_TEXT
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from keyboards.keyboards import *
from aiogram.types import CallbackQuery
from secrets import token_urlsafe
import asyncio
from aiogram import Bot
import logging
from config_data.config import Config, load_config
from module.data_base import check_command_for_admins, table_users, add_token, table_channel, add_channel,\
    get_list_users, get_user, delete_user, get_list_admins, get_list_notadmins, set_admins, set_notadmins

router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()
user_dict = {}

class Stage(StatesGroup):
    channel = State()


# запуск бота только администраторами /start
@router.message(CommandStart(), lambda message: check_command_for_admins(message))
async def process_start_command(message: Message) -> None:
    table_users()
    logging.info(f'process_start_command: {message.chat.id}')
    if str(message.chat.id) != str(config.tg_bot.admin_ids):
        await message.answer(text=MESSAGE_TEXT['start'])
    else:
        await message.answer(text=MESSAGE_TEXT['superadmin'],
                             reply_markup=keyboards_superadmin())


# КАНАЛ
@router.message(F.text == 'Канал', lambda message: check_command_for_admins(message))
async def process_change_channel(message: Message, state: FSMContext) -> None:
    """
    Функция получает id канала или чата для отправки отчета
    :param message:
    :return:
    """
    logging.info(f'process_change_channel: {message.chat.id}')
    await message.answer(text=MESSAGE_TEXT['channel'])
    table_channel()
    await state.set_state(Stage.channel)


@router.message(lambda message: check_command_for_admins(message), StateFilter(Stage.channel))
async def process_change_list_users(message: Message, state: FSMContext) -> None:
    logging.info(f'process_change_list_users: {message.chat.id}')
    await message.answer(text=f'Вы установили канал/чат id={message.text} для получения отчетов! '
                              f'Убедитесь что бот имеет права администратора в этом канале')
    add_channel(message.text)
    await state.set_state(default_state)


# УСЛУГА
@router.message(F.text == 'Услуга', lambda message: check_command_for_admins(message))
async def process_change_list_services(message: Message) -> None:
    """
    Функция позволяет удалять пользователей из бота
    :param message:
    :return:
    """
    logging.info(f'process_change_list_services: {message.chat.id}')
    await message.answer(text=MESSAGE_TEXT['user'],
                         reply_markup=keyboard_edit_list_user())


# ПОЛЬЗОВАТЕЛЬ
@router.message(F.text == 'Пользователь', lambda message: check_command_for_admins(message))
async def process_change_list_users(message: Message) -> None:
    """
    Функция позволяет удалять пользователей из бота
    :param message:
    :return:
    """
    logging.info(f'process_change_list_users: {message.chat.id}')
    await message.answer(text=MESSAGE_TEXT['user'],
                         reply_markup=keyboard_edit_list_user())


# добавить пользователя
@router.callback_query(F.data == 'add_user')
async def process_description(callback: CallbackQuery) -> None:
    token_new = str(token_urlsafe(8))
    add_token(token_new)
    await callback.message.answer(text=f'Для добавления пользователя в бот отправьте ему этот TOKEN <b>{token_new}</b>.'
                                       f' По этому TOKEN может быть добавлен только один пользователь,'
                                       f' не делитесь и не показывайте его никому, кроме тех лиц для кого он предназначен')


# удалить пользователя
@router.callback_query(F.data == 'delete_user')
async def process_description(callback: CallbackQuery) -> None:
    list_user = get_list_users()
    keyboard = keyboards_del_users(list_user, 0, 2, 2)
    await callback.message.answer(text='Выберите пользователя, которого вы хотите удалить',
                                  reply_markup=keyboard)


# >>>>
@router.callback_query(F.data.startswith('forward'))
async def process_description(callback: CallbackQuery) -> None:
    list_user = get_list_users()
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    keyboard = keyboards_del_users(list_user, back, forward, 2)
    await callback.message.answer(text='Выберите пользователя, которого вы хотите удалить',
                                  reply_markup=keyboard)


# <<<<
@router.callback_query(F.data.startswith('back'))
async def process_description(callback: CallbackQuery) -> None:
    list_user = get_list_users()
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = keyboards_del_users(list_user, back, forward, 2)
    await callback.message.answer(text='Выберите пользователя, которого вы хотите удалить',
                                  reply_markup=keyboard)


# подтверждение удаления пользователя из базы
@router.callback_query(F.data.startswith('deleteuser'))
async def process_deleteuser(callback: CallbackQuery, state: FSMContext) -> None:
    telegram_id = int(callback.data.split('_')[1])
    user_info = get_user(telegram_id)
    await state.update_data(del_telegram_id=telegram_id)
    await callback.message.answer(text=f'Удалить пользователя {user_info[0]}',
                                  reply_markup=keyboard_delete_user())


# отмена удаления пользователя
@router.callback_query(F.data == 'notdel_user')
async def process_deleteuser(callback: CallbackQuery) -> None:
    await process_change_list_users(callback.message)


# удаление после подтверждения
@router.callback_query(F.data == 'del_user')
async def process_description(callback: CallbackQuery, state: FSMContext) -> None:
    user_dict[callback.message.chat.id] = await state.get_data()
    user_info = get_user(user_dict[callback.message.chat.id]["del_telegram_id"])
    print(user_info, user_dict[callback.message.chat.id]["del_telegram_id"])
    delete_user(user_dict[callback.message.chat.id]["del_telegram_id"])
    await callback.message.answer(text=f'Пользователь успешно удален')
    await asyncio.sleep(3)
    await process_change_list_users(callback.message)


# АДМИНИСТРАТОРЫ
@router.message(F.text == 'Администраторы', lambda message: str(message.chat.id) == str(config.tg_bot.admin_ids))
async def process_change_list_admins(message: Message) -> None:
    """
    Функция позволяет удалять пользователей из бота
    :param message:
    :return:
    """
    logging.info(f'process_change_list_admins: {message.chat.id}')
    await message.answer(text=MESSAGE_TEXT['admins'],
                         reply_markup=keyboard_edit_list_admins())


# добавление администратора
@router.callback_query(F.data == 'add_admin')
async def process_add_admin(callback: CallbackQuery) -> None:
    logging.info(f'process_add_admin: {callback.message.chat.id}')
    list_admin = get_list_notadmins()
    keyboard = keyboards_add_admin(list_admin, 0, 2, 2)
    await callback.message.answer(text='Выберите пользователя, которого нужно назначить администратором',
                                  reply_markup=keyboard)


# >>>>
@router.callback_query(F.data.startswith('adminforward'))
async def process_forwardadmin(callback: CallbackQuery) -> None:
    logging.info(f'process_backadmin: {callback.message.chat.id}')
    list_admin = get_list_notadmins()
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    keyboard = keyboards_add_admin(list_admin, back, forward, 2)
    await callback.message.answer(text='Выберите пользователя, которого вы хотите сделать администратором',
                                  reply_markup=keyboard)


# <<<<
@router.callback_query(F.data.startswith('adminback'))
async def process_backadmin(callback: CallbackQuery) -> None:
    logging.info(f'process_backadmin: {callback.message.chat.id}')
    list_admin = get_list_notadmins()
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = keyboards_add_admin(list_admin, back, forward, 2)
    await callback.message.answer(text='Выберите пользователя, которого вы хотите сделать администратором',
                                  reply_markup=keyboard)


# подтверждение добавления админа в список админов
@router.callback_query(F.data.startswith('adminadd'))
async def process_deleteuser(callback: CallbackQuery, state: FSMContext) -> None:
    telegram_id = int(callback.data.split('_')[1])
    user_info = get_user(telegram_id)
    await state.update_data(add_admin_telegram_id=telegram_id)
    await callback.message.answer(text=f'Назначить пользователя {user_info[0]} администратором',
                                  reply_markup=keyboard_add_list_admins())


# отмена добавления пользователя в список администраторов
@router.callback_query(F.data == 'notadd_admin_list')
async def process_deleteuser(callback: CallbackQuery) -> None:
    await process_change_list_admins(callback.message)


# удаление после подтверждения
@router.callback_query(F.data == 'add_admin_list')
async def process_description(callback: CallbackQuery, state: FSMContext) -> None:
    user_dict[callback.message.chat.id] = await state.get_data()
    user_info = get_user(user_dict[callback.message.chat.id]["add_admin_telegram_id"])
    print(user_info, user_dict[callback.message.chat.id]["add_admin_telegram_id"])
    set_admins(int(user_dict[callback.message.chat.id]["add_admin_telegram_id"]))
    await callback.message.answer(text=f'Пользователь успешно назначен администратором')
    await asyncio.sleep(3)
    await process_change_list_admins(callback.message)


# разжалование администратора
@router.callback_query(F.data == 'delete_admin')
async def process_del_admin(callback: CallbackQuery) -> None:
    logging.info(f'process_del_admin: {callback.message.chat.id}')
    list_admin = get_list_admins()
    keyboard = keyboards_del_admin(list_admin, 0, 2, 2)
    await callback.message.answer(text='Выберите пользователя, которого нужно разжаловать',
                                  reply_markup=keyboard)


# >>>>
@router.callback_query(F.data.startswith('admindelforward'))
async def process_forwarddeladmin(callback: CallbackQuery) -> None:
    logging.info(f'process_forwarddeladmin: {callback.message.chat.id}')
    list_admin = get_list_admins()
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    keyboard = keyboards_del_admin(list_admin, back, forward, 2)
    await callback.message.answer(text='Выберите пользователя, которого вы хотите разжаловать',
                                  reply_markup=keyboard)


# <<<<
@router.callback_query(F.data.startswith('admindelback'))
async def process_backdeladmin(callback: CallbackQuery) -> None:
    logging.info(f'process_backdeladmin: {callback.message.chat.id}')
    list_admin = get_list_admins()
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = keyboards_del_admin(list_admin, back, forward, 2)
    await callback.message.answer(text='Выберите пользователя, которого вы хотите разжаловать',
                                  reply_markup=keyboard)


# подтверждение добавления админа в список админов
@router.callback_query(F.data.startswith('admindel'))
async def process_deleteuser(callback: CallbackQuery, state: FSMContext) -> None:
    telegram_id = int(callback.data.split('_')[1])
    user_info = get_user(telegram_id)
    await state.update_data(del_admin_telegram_id=telegram_id)
    await callback.message.answer(text=f'Разжаловать пользователя {user_info[0]} из администраторов',
                                  reply_markup=keyboard_del_list_admins())


# отмена добавления пользователя в список администраторов
@router.callback_query(F.data == 'notdel_admin_list')
async def process_deleteuser(callback: CallbackQuery) -> None:
    await process_change_list_admins(callback.message)


# удаление после подтверждения
@router.callback_query(F.data == 'del_admin_list')
async def process_description(callback: CallbackQuery, state: FSMContext) -> None:
    user_dict[callback.message.chat.id] = await state.get_data()
    user_info = get_user(user_dict[callback.message.chat.id]["del_admin_telegram_id"])
    print(user_info, user_dict[callback.message.chat.id]["del_admin_telegram_id"])
    set_notadmins(int(user_dict[callback.message.chat.id]["del_admin_telegram_id"]))
    await callback.message.answer(text=f'Пользователь успешно разжалован')
    await asyncio.sleep(3)
    await process_change_list_admins(callback.message)