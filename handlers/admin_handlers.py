from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
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
    get_list_users, get_user, delete_user, get_list_admins, get_list_notadmins, set_admins, set_notadmins,\
    table_services, add_services, get_list_services, delete_services, update_service, get_cost_service, table_orders,\
    add_orders, get_row_services, get_id_last_orders, update_list_sendlers

router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()
user_dict = {}
table_users()

class Stage(StatesGroup):
    channel = State()
    title_services = State()
    cost_services = State()
    count_services = State()
    edit_title_service = State()
    edit_cost_service = State()
    set_comment_service = State()
    select_count_people = State()


# запуск бота только администраторами /start
@router.message(CommandStart(), lambda message: check_command_for_admins(message))
async def process_start_command(message: Message) -> None:
    table_users()
    logging.info(f'process_start_command: {message.chat.id}')
    if str(message.chat.id) != str(config.tg_bot.admin_ids):
        await message.answer(text=MESSAGE_TEXT['admin'],
                             reply_markup=keyboards_admin())
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

# КАНАЛ - добавление канала
@router.message(lambda message: check_command_for_admins(message), StateFilter(Stage.channel))
async def process_change_list_users(message: Message, state: FSMContext) -> None:
    logging.info(f'process_change_list_users: {message.chat.id}')
    try:
        add_channel(message.text)
        await message.answer(text=f'Вы установили канал/чат id={message.text} для получения отчетов! '
                                  f'Убедитесь что бот имеет права администратора в этом канале')
    except:
        await message.answer(text=f'Канал/чат id={message.text} не корректен')
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
    table_services()
    await message.answer(text=MESSAGE_TEXT['services'],
                         reply_markup=keyboard_edit_select_services())


# УСЛУГА -> Редактировать -> [Добавить][Изменить]
@router.callback_query(F.data == 'edit_services')
async def process_edit_list_services(callback: CallbackQuery) -> None:
    logging.info(f'process_edit_list_services: {callback.message.chat.id}')
    await callback.message.answer(text='Вы можете добавить услугу в базу или изменить уже созданные!',
                                  reply_markup=keyboard_edit_services())


# УСЛУГА -> Редактировать -> Добавить
@router.callback_query(F.data == 'append_services')
async def process_append_services(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_append_services: {callback.message.chat.id}')
    await callback.message.answer(text='Введите название услуги!')
    await state.set_state(Stage.title_services)


# УСЛУГА -> Редактировать -> Добавить - Получаем название услуги
@router.message(lambda message: check_command_for_admins(message), StateFilter(Stage.title_services))
async def process_get_title_services(message: Message, state: FSMContext) -> None:
    logging.info(f'process_append_services: {message.chat.id}')
    await state.update_data(title_services=message.text)
    await message.answer(text=f'Укажите стоимость выполнения услуги <b>{message.text}</b> для одного исполнителя')
    await state.set_state(Stage.cost_services)


# УСЛУГА -> Редактировать -> Добавить - Получаем стоимость выполнения услуги одним человеком и заносим в БД
@router.message(lambda message: check_command_for_admins(message), StateFilter(Stage.cost_services))
async def process_get_cost_services(message: Message, state: FSMContext) -> None:
    logging.info(f'process_get_cost_services: {message.chat.id}')
    await state.update_data(cost_services=message.text)
    user_dict[message.chat.id] = await state.get_data()
    await message.answer(text=f'Укажите количество исполнителей для услуги '
                              f'<b>{user_dict[message.chat.id]["title_services"]}</b> для одного исполнителя')
    await state.set_state(Stage.count_services)


# УСЛУГА -> Редактировать -> Добавить - Получаем количество исполнителей для услуги и заносим в базу
@router.message(lambda message: check_command_for_admins(message), StateFilter(Stage.count_services))
async def process_get_count_services(message: Message, state: FSMContext) -> None:
    logging.info(f'process_get_count_services: {message.chat.id}')
    await state.update_data(count_services=message.text)
    user_dict[message.chat.id] = await state.get_data()
    add_services(user_dict[message.chat.id]["title_services"],
                 int(user_dict[message.chat.id]["cost_services"]),
                 int(user_dict[message.chat.id]["count_services"]))
    await message.answer(text=f'<b>Услуга добавлена в базу:</b>\n\n'
                              f'<i>Название услуги:</i> {user_dict[message.chat.id]["title_services"]}\n'
                              f'<i>Стоимость услуги:</i> {user_dict[message.chat.id]["cost_services"]}\n'
                              f'<i>Количество исполнителей:</i> {user_dict[message.chat.id]["count_services"]}\n',
                         reply_markup=keyboard_confirmation_append_services())
    await state.set_state(default_state)


# завершаем добавление услуг
@router.callback_query(F.data == 'finish_services')
async def process_finish_append_services(callback: CallbackQuery) -> None:
    logging.info(f'process_finish_append_services: {callback.message.chat.id}')
    await process_change_list_services(callback.message)


@router.callback_query(F.data == 'change_services')
async def process_change_services(callback: CallbackQuery) -> None:
    logging.info(f'process_change_services: {callback.message.chat.id}')
    list_services = get_list_services()
    back = 0
    forward = 2
    count_item = 6
    keyboard = keyboards_edit_services(list_services, back, forward, count_item)
    await callback.message.answer(text='Выберите услугу из базы',
                                  reply_markup=keyboard)


# >>>>
@router.callback_query(F.data.startswith('serviceseditforward'))
async def process_serviceseditforward(callback: CallbackQuery) -> None:
    logging.info(f'process_serviceseditforward: {callback.message.chat.id}')
    list_services = get_list_services()
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    count_item = 6
    keyboard = keyboards_edit_services(list_services, back, forward, count_item)
    try:
        await callback.message.edit_text(text='Выберите услугу из базы',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите услугу из базы.',
                                         reply_markup=keyboard)


# <<<<
@router.callback_query(F.data.startswith('serviceseditback'))
async def process_serviceseditback(callback: CallbackQuery) -> None:
    logging.info(f'process_serviceseditback: {callback.message.chat.id}')
    list_services = get_list_services()
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    count_item = 6
    keyboard = keyboards_edit_services(list_services, back, forward, count_item)
    try:
        await callback.message.edit_text(text='Выберите услугу из базы',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите услугу из базы.',
                                         reply_markup=keyboard)


# удаление или модификация выбранной услуги
@router.callback_query(F.data.startswith('servicesedit'))
async def process_servicesedit(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_servicesedit: {callback.message.chat.id}')
    title_service = callback.data.split('_')[1]
    await state.update_data(edit_title_service=title_service)
    await state.update_data(edit_title_service_new=title_service)
    await callback.message.answer(text=f'Что нужно сделать с услугой <b>{title_service}</b>',
                                  reply_markup=keyboard_edit_list_services())


# УСЛУГА - удаление услуги
@router.callback_query(F.data == 'delete_services')
async def process_delete_services(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_delete_services: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    delete_services(user_dict[callback.message.chat.id]['edit_title_service'])
    await callback.message.answer(text=f'Услуга <b>{user_dict[callback.message.chat.id]["edit_title_service"]}</b>'
                                       f' успешно удалена')
    await process_change_list_services(callback.message)


# УСЛУГА - модификация услуги
@router.callback_query(F.data == 'modification_services')
async def process_modification_services(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_modification_services: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    await callback.message.answer(text=f'Введите новое название для услуги '
                                       f'<b>{user_dict[callback.message.chat.id]["edit_title_service"]}</b>, '
                                       f'или переходите к изменению стоимости ее выполнения',
                                  reply_markup=keyboard_pass_edit_title_services())
    await state.set_state(Stage.edit_title_service)


@router.callback_query(F.data == 'pass_edit_service', StateFilter(Stage.edit_title_service))
async def process_pass_edit_service(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_pass_edit_service: {callback.message.chat.id}')
    await state.set_state(default_state)
    await callback.message.answer(text=f'Укажите стоимость выполнения услуги '
                                       f'<b>{user_dict[callback.message.chat.id]["edit_title_service"]}</b>')
    await state.set_state(Stage.edit_cost_service)


# Получаем наименование услуги
@router.message(F.text, StateFilter(Stage.edit_title_service))
async def process_get_edittitle_services(message: Message, state: FSMContext) -> None:
    logging.info(f'process_get_edittitle_services: {message.chat.id}')
    await state.update_data(edit_title_service_new=message.text)
    user_dict[message.chat.id] = await state.get_data()
    await message.answer(text=f'Укажите стоимость выполнения услуги '
                              f'<b>{user_dict[message.chat.id]["edit_title_service_new"]}</b> для одного исполнителя')
    await state.set_state(Stage.edit_cost_service)


@router.message(F.text, StateFilter(Stage.edit_cost_service))
async def process_get_editcost_services(message: Message, state: FSMContext) -> None:
    logging.info(f'process_get_editcost_services: {message.chat.id}')
    update_service(title_services=user_dict[message.chat.id]["edit_title_service"],
                   title_services_new=user_dict[message.chat.id]["edit_title_service_new"],
                   cost=int(message.text))
    await message.answer(text=f'Вы внесли изменения в услугу <b>{user_dict[message.chat.id]["edit_title_service_new"]}</b> '
                              f'стоимость выполнения для одного исполнителя - {message.text}',
                         reply_markup=keyboard_finish_edit_service())
    await state.set_state(default_state)


# возвращение к списку услуг для редактирования
@router.callback_query(F.data == 'continue_edit_service')
async def process_continue_edit_service(callback: CallbackQuery) -> None:
    logging.info(f'process_continue_edit_service: {callback.message.chat.id}')
    await process_change_services(callback)


# выход из редактирования
@router.callback_query(F.data == 'finish_edit_services')
async def process_finish_edit_services(callback: CallbackQuery) -> None:
    logging.info(f'process_finish_edit_services: {callback.message.chat.id}')
    # await process_start_command(callback.message)
    await process_change_list_services(callback.message)


# УСЛУГА -> Выбрать
@router.callback_query(F.data == 'select_services')
async def process_select_services(callback: CallbackQuery) -> None:
    logging.info(f'process_select_services: {callback.message.chat.id}')
    table_orders()
    list_services = get_list_services()
    back = 0
    forward = 2
    count_item = 6
    keyboard = keyboards_select_services(list_services, back, forward, count_item)
    await callback.message.answer(text='Выберите услугу из базы для добавления в заказ',
                                  reply_markup=keyboard)


# >>>>
@router.callback_query(F.data.startswith('serviceselectforward'))
async def process_serviceselectforward(callback: CallbackQuery) -> None:
    logging.info(f'process_serviceselectforward: {callback.message.chat.id}')
    list_services = get_list_services()
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    count_item = 6
    keyboard = keyboards_edit_services(list_services, back, forward, count_item)
    try:
        await callback.message.edit_text(text='Выберите услугу из базы для добавления в заказ',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите услугу из базы для добавления в заказ.',
                                         reply_markup=keyboard)


# <<<<
@router.callback_query(F.data.startswith('serviceselectback'))
async def process_serviceselectback(callback: CallbackQuery) -> None:
    logging.info(f'process_serviceselectback: {callback.message.chat.id}')
    list_services = get_list_services()
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    count_item = 6
    keyboard = keyboards_edit_services(list_services, back, forward, count_item)
    try:
        await callback.message.edit_text(text='Выберите услугу из базы для добавления в заказ',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите услугу из базы для добавления в заказ.',
                                         reply_markup=keyboard)


# добавление услуги в заказ
@router.callback_query(F.data.startswith('serviceselect'))
async def process_serviceselect(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_serviceselect: {callback.message.chat.id}')
    title_service = callback.data.split('_')[1]
    await state.update_data(select_title_service=title_service)
    cost = get_cost_service(title_service)
    await state.update_data(select_cost_service=cost)
    await callback.message.answer(text=f'Выбрана услуга <b>{title_service}</b>,\n стоимость выполнения для одного'
                                       f' исполнителя <b>{cost}</b>',
                                  reply_markup=keyboard_continue_orders())


@router.callback_query(F.data == 'back_odrers')
async def process_back_odrers(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_back_odrers: {callback.message.chat.id}')
    await process_select_services(callback)


@router.callback_query(F.data == 'continue_orders')
async def process_continue_orders(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_continue_orders: {callback.message.chat.id}')
    await callback.message.answer(text=f'Добавьте комментарий к заказу')
    await state.set_state(Stage.set_comment_service)


# @router.message(F.text, StateFilter(Stage.set_comment_service))
# async def process_get_comment(message: Message, state: FSMContext) -> None:
#     logging.info(f'process_get_comment: {message.chat.id}')
#     await state.update_data(select_comment_service=message.text)
#     await message.answer(text=f'Сколько исполнителей требуется для выполнения заказа? Количество по умолчанию 1',
#                          reply_markup=keyboard_count_people())
#     await state.update_data(select_countpeople_service=1)
#     await state.set_state(Stage.select_count_people)
#
#
# @router.callback_query(F.data == 'pass_people')
# async def process_send_orders(callback: CallbackQuery, state: FSMContext) -> None:
#     logging.info(f'process_send_orders: {callback.message.chat.id}')
#     user_dict[callback.message.chat.id] = await state.get_data()
#     await callback.message.answer(text=f'Заказа на услугу <b>{user_dict[callback.message.chat.id]["select_title_service"]}</b>\n'
#                                        f'стоимостью <b>{user_dict[callback.message.chat.id]["select_cost_service"]}</b>\n'
#                                        f'для {user_dict[callback.message.chat.id]["select_countpeople_service"]} исполнителей сформирован.\n'
#                                        f'Комментарий: {user_dict[callback.message.chat.id]["select_comment_service"]}',
#                                   reply_markup=keyboard_finish_orders())


@router.message(F.text, StateFilter(Stage.set_comment_service))
async def process_get_count_people(message: Message, state: FSMContext) -> None:
    logging.info(f'process_get_count_people: {message.chat.id}')
    await state.update_data(select_comment_service=message.text)

    user_dict[message.chat.id] = await state.get_data()
    await message.answer(text=f'<b>Заказ</b>:\n\n'
                              f'Услуга: {user_dict[message.chat.id]["select_title_service"]}.\n'
                              f'Стоимость {user_dict[message.chat.id]["select_cost_service"]}\n'
                              f'Комментарий <code>{user_dict[message.chat.id]["select_comment_service"]}</code>\n'
                              f'Опубликовать',
                         reply_markup=keyboard_finish_orders(),
                         parse_mode='html')


@router.callback_query(F.data == 'cancel_orders')
async def process_cancel_odrers(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_cancel_odrers: {callback.message.chat.id}')
    await process_select_services(callback)


@router.callback_query(F.data == 'send_orders')
async def process_send_orders_all(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_send_orders_all: {callback.message.chat.id}')
    row_services = get_row_services(user_dict[callback.message.chat.id]["select_title_service"])
    print(row_services)  # [(id, title_services, cost_services,count_people)]
    add_orders(title_services=user_dict[callback.message.chat.id]["select_title_service"],
               cost_services=row_services[0][2],
               comment=user_dict[callback.message.chat.id]["select_comment_service"],
               count_people=row_services[0][3])
    id_orders = get_id_last_orders()

    list_sendler = get_list_users()
    list_mailing = []
    for row in list_sendler:
        msg = await bot.send_message(chat_id=row[0],
                                     text=f'Появился заказ на : {user_dict[callback.message.chat.id]["select_title_service"]}.\n'
                                          f'Стоимость {user_dict[callback.message.chat.id]["select_cost_service"]}\n'
                                          f'Комментарий <code>{user_dict[callback.message.chat.id]["select_comment_service"]}</code>\n'
                                          f'Готовы выполнить?',
                                     reply_markup=keyboard_ready_player(id_order=id_orders[0]))
        iduser_idmessage = f'{row[0]}_{msg.message_id}'
        list_mailing.append(iduser_idmessage)
    msg = await bot.send_message(chat_id=config.tg_bot.admin_ids,
                           text=f'Появился заказ на : {user_dict[callback.message.chat.id]["select_title_service"]}.\n'
                                f'Стоимость {user_dict[callback.message.chat.id]["select_cost_service"]}\n'
                                f'Комментарий <code>{user_dict[callback.message.chat.id]["select_comment_service"]}</code>\n'
                                f'Готовы выполнить?',
                           reply_markup=keyboard_ready_player(id_order=id_orders[0]))
    iduser_idmessage = f'{config.tg_bot.admin_ids}_{msg.message_id}'
    list_mailing.append(iduser_idmessage)
    await callback.message.answer(text=f'Заказ № {id_orders[0]} успешно отправлен')
    list_mailing_str = ','.join(list_mailing)
    update_list_sendlers(list_mailing_str=list_mailing_str, id_orders=id_orders[0])
    await state.set_state(default_state)


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
async def process_add_user(callback: CallbackQuery) -> None:
    logging.info(f'process_add_user: {callback.message.chat.id}')
    token_new = str(token_urlsafe(8))
    add_token(token_new)
    await callback.message.answer(text=f'Для добавления пользователя в бот отправьте ему этот TOKEN <code>{token_new}</code>.'
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
    try:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите удалить',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите пользователя, которого нужно удалить',
                                         reply_markup=keyboard)


# <<<<
@router.callback_query(F.data.startswith('back'))
async def process_description(callback: CallbackQuery) -> None:
    list_user = get_list_users()
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = keyboards_del_users(list_user, back, forward, 2)
    try:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите удалить',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите пользователя, которого нужно удалить',
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
    try:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите сделать администратором',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите пользователя, которого нужно сделать администратором',
                                         reply_markup=keyboard)


# <<<<
@router.callback_query(F.data.startswith('adminback'))
async def process_backadmin(callback: CallbackQuery) -> None:
    logging.info(f'process_backadmin: {callback.message.chat.id}')
    list_admin = get_list_notadmins()
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = keyboards_add_admin(list_admin, back, forward, 2)
    try:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите сделать администратором',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите пользователя, которого нужно сделать администратором',
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
    try:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите разжаловать',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите пользователя, которого нужно разжаловать',
                                         reply_markup=keyboard)


# <<<<
@router.callback_query(F.data.startswith('admindelback'))
async def process_backdeladmin(callback: CallbackQuery) -> None:
    logging.info(f'process_backdeladmin: {callback.message.chat.id}')
    list_admin = get_list_admins()
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = keyboards_del_admin(list_admin, back, forward, 2)
    try:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите разжаловать',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите пользователя, которого нужно разжаловать',
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