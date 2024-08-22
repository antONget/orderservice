from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.filters import StateFilter

import keyboards.keyboard_admin_order_select as kb
import database.requests as rq
from filter.admin_filter import check_super_admin
from config_data.config import Config, load_config

import logging
import requests

router = Router()
config: Config = load_config()


class OrderSelect(StatesGroup):
    set_comment_service = State()
    select_count_people = State()
    picture = State()


def get_telegram_user(user_id, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    return response.json()


# УСЛУГА -> Выбрать
@router.callback_query(F.data == 'select_services')
async def process_select_services(callback: CallbackQuery, bot: Bot) -> None:
    """
    Вывод списка услуг для добавления их в заказ
    :param callback:
    :param bot:
    :return:
    """
    logging.info(f'process_select_services: {callback.message.chat.id}')
    list_services = [service for service in await rq.get_service()]
    if not list_services:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        await callback.answer(text='Нет услуг для добавления в заказ', show_alert=True)
        return
    back = 0
    forward = 2
    count_item = 6
    keyboard = kb.keyboards_select_services(list_services=list_services, back=back, forward=forward,
                                            count=count_item)
    try:
        await callback.message.edit_text(text='Выберите услугу для создания заказа:',
                                         reply_markup=keyboard)
    except:
        await callback.message.answer(text='Выберите услугу для создания заказа:',
                                      reply_markup=keyboard)
    await callback.answer()


# >>>>
@router.callback_query(F.data.startswith('serviceselectforward'))
async def process_serviceselectforward(callback: CallbackQuery) -> None:
    """
    Пагинация вперед по списку услуг для добавления их в заказ
    :param callback:
    :return:
    """
    logging.info(f'process_serviceselectforward: {callback.message.chat.id}')
    list_services = [service for service in await rq.get_service()]
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    count_item = 6
    keyboard = kb.keyboards_select_services(list_services=list_services,
                                            back=back,
                                            forward=forward,
                                            count=count_item)
    try:
        await callback.message.edit_text(text='Выберите услугу для создания заказа:',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите услугу  для создания заказа:',
                                         reply_markup=keyboard)
    await callback.answer()


# <<<<
@router.callback_query(F.data.startswith('serviceselectback'))
async def process_serviceselectback(callback: CallbackQuery) -> None:
    """
    Пагинация назад по списку услуг для добавления их в заказ
    :param callback:
    :return:
    """
    logging.info(f'process_serviceselectback: {callback.message.chat.id}')
    list_services = [service for service in await rq.get_service()]
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    count_item = 6
    keyboard = kb.keyboards_select_services(list_services, back, forward, count_item)
    try:
        await callback.message.edit_text(text='Выберите услугу для создания заказа:',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите услугу для  создания заказа:',
                                         reply_markup=keyboard)
    await callback.answer()


# добавление услуги в заказ
@router.callback_query(F.data.startswith('kserviceselect'))
async def process_serviceselect(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_serviceselect: {callback.message.chat.id}')
    service_id = int(callback.data.split('_')[1])
    await state.update_data(service_id=service_id)
    service_info = await rq.get_service_id(service_id=service_id)
    await state.update_data(select_cost_service=service_info.cost_services)
    await callback.message.edit_text(text=f'Услуга: <b>{service_info.title_services}</b>,\n'
                                          f'Оплата для одного исполнителя: <b>{service_info.cost_services}</b>',
                                     reply_markup=kb.keyboard_continue_orders())
    await callback.answer()


@router.callback_query(F.data == 'order_back')
async def process_order_back(callback: CallbackQuery, bot: Bot) -> None:
    """
    Возврат к выбору услуги для добавления в заказ
    :param callback:
    :param bot:
    :return:
    """
    logging.info(f'process_order_back: {callback.message.chat.id}')
    await callback.answer()
    await process_select_services(callback=callback, bot=bot)


@router.callback_query(F.data == 'continue_orders')
async def process_continue_orders(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Продолжение добавления услуги в заказ - запрос ввода ID клиента
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_continue_orders: {callback.message.chat.id}')
    await callback.message.edit_text(text=f'Напишите ID клиента:', reply_markup=None)
    await state.set_state(OrderSelect.set_comment_service)
    await callback.answer()


# @router.message(StateFilter(OrderSelect.set_comment_service), F.text)
# async def process_get_comment(message: Message, state: FSMContext) -> None:
#     logging.info(f'process_get_comment: {message.chat.id}')
#     await state.update_data(select_comment_service=message.text)
#     await message.answer(text=f'Сколько исполнителей требуется для выполнения заказа? Количество по умолчанию 1',
#                          reply_markup=kb.keyboard_count_people())
#     await state.update_data(select_countpeople_service=1)
#     await state.set_state(OrderSelect.select_count_people)
#
#
# @router.callback_query(F.data == 'pass_people')
# async def process_send_orders(callback: CallbackQuery, state: FSMContext) -> None:
#     """
#     Пропускаем ввод количества исполнителей (указываем по умолчанию = 1)
#     :param callback:
#     :param state:
#     :return:
#     """
#     logging.info(f'process_send_orders: {callback.message.chat.id}')
#     data = await state.get_data()
#     await callback.message.answer(text=f'Заказ на услугу <b>{data["select_title_service"]}</b>\n'
#                                        f'стоимостью <b>{data["select_cost_service"]}</b>\n'
#                                        f'для {data["select_countpeople_service"]} исполнителей сформирован.\n'
#                                        f'ID клиента: {data["select_comment_service"]}',
#                                   reply_markup=kb.keyboard_finish_orders())
#     await state.set_state(default_state)


@router.message(lambda message: message.text not in ['Услуга', 'Статистика', 'Скинуть занятость', '>>>',
                                                     'Администраторы', 'Пользователь', 'Прикрепить', 'Сброс статистики',
                                                     '<<<'], StateFilter(OrderSelect.set_comment_service))
async def process_set_comment_service(message: Message, state: FSMContext) -> None:
    """
    Подтверждение опубликования заказа
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_set_comment_service: {message.chat.id}')
    await state.update_data(select_comment_service=message.text)
    data = await state.get_data()
    service_id = data['service_id']
    service_info = await rq.get_service_id(service_id=service_id)
    picture = service_info.picture_services
    last_order = [order for order in await rq.get_orders()]
    if not last_order:
        number_order = 1
    else:
        number_order = last_order[-1].id + 1
    if picture == 'None':
        await message.answer(text=f'<b>Заказ №{number_order}:</b>\n\n'
                                  f'Услуга: {service_info.title_services}.\n'
                                  f'Стоимость: {service_info.cost_services}\n'
                                  f'ID клиента: <code>{data["select_comment_service"]}</code>\n'
                                  f'Опубликовать?',
                             reply_markup=kb.keyboard_finish_orders(),
                             parse_mode='html')
    else:
        await message.answer_photo(photo=picture,
                                   caption=f'<b>Заказ №{number_order}:</b>\n\n'
                                           f'Услуга: {service_info.title_services}.\n'
                                           f'Стоимость: {service_info.cost_services}\n'
                                           f'ID клиента: <code>{data["select_comment_service"]}</code>\n'
                                           f'Опубликовать?',
                                   reply_markup=kb.keyboard_finish_orders(),
                                   parse_mode='html')
    await state.set_state(default_state)


@router.callback_query(F.data == 'cancel_orders')
async def process_cancel_odrers(callback: CallbackQuery, bot: Bot) -> None:
    """
    Отмена публикации заказа
    :param callback:
    :param bot:
    :return:
    """
    logging.info(f'process_cancel_odrers: {callback.message.chat.id}')
    await process_select_services(callback=callback, bot=bot)
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.answer()


@router.callback_query(F.data == 'send_orders')
async def process_send_orders_all(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Публикация заказа
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_send_orders_all: {callback.message.chat.id}')
    await callback.message.edit_reply_markup(reply_markup=kb.keyboard_finish_orders_one_press())
    data = await state.get_data()
    service_id = data['service_id']
    service_info = await rq.get_service_id(service_id=service_id)
    data_order = {"service_id": service_info.id,
                  "title_services": service_info.title_services,
                  "cost_services": service_info.cost_services,
                  "comment": data["select_comment_service"],
                  "count_people": service_info.count_services}
    await rq.add_order(data=data_order)

    last_order = [order for order in await rq.get_orders()][-1]
    number_order = last_order.id
    # список для рассылки всем пользователям
    list_sandler = [user for user in await rq.get_all_users()]
    for user in list_sandler:
        # супер-администраторам не отправляем
        if not await check_super_admin(telegram_id=user.telegram_id):
            # проверяем доступность ботом аккаунта
            result = get_telegram_user(user_id=user.telegram_id, bot_token=config.tg_bot.token)
            if 'result' in result:
                # есть ли в сообщении фотография
                if not service_info.picture_services == 'None':
                    msg = await bot.send_photo(photo=service_info.picture_services,
                                               chat_id=user.telegram_id,
                                               caption=f'Появился заказ № {number_order} на:'
                                                       f' {service_info.title_services}.\n'
                                                       f'Стоимость {service_info.cost_services}\n'
                                                       f'Комментарий <code>{data["select_comment_service"]}</code>\n'
                                                       f'Готовы выполнить?',
                                               reply_markup=kb.keyboard_ready_player_())
                else:
                    msg = await bot.send_message(chat_id=user.telegram_id,
                                                 text=f'Появился заказ № {number_order} на:'
                                                      f' {service_info.title_services}.\n'
                                                      f'Стоимость {service_info.cost_services}\n'
                                                      f'Комментарий <code>{data["select_comment_service"]}</code>\n'
                                                      f'Готовы выполнить?',
                                                 reply_markup=kb.keyboard_ready_player_())
                # добавляем пользователя в БД исполнителей заказа
                data_executor = {"tg_id": user.telegram_id,
                                 "id_order": last_order.id,
                                 "cost_order": last_order.cost_services,
                                 "status_executor": rq.ExecutorStatus.none,
                                 "message_id": msg.message_id}
                await rq.add_executor(data=data_executor)

    await callback.message.edit_reply_markup(reply_markup=kb.keyboard_finish_orders_one_press_del(number_order))
    await callback.message.answer(text=f'Заказ № {number_order} успешно отправлен!')

    # изменяем клавиатуру у пользователей
    list_mailing = [executor for executor in await rq.get_executors_order_id(order_id=last_order.id)]
    for executor in list_mailing:
        result = get_telegram_user(user_id=executor.tg_id, bot_token=config.tg_bot.token)
        if 'result' in result:
            try:
                await bot.edit_message_reply_markup(chat_id=executor.tg_id,
                                                    message_id=executor.message_id,
                                                    reply_markup=kb.keyboard_ready_player(id_order=number_order))
            except:
                await bot.send_message(chat_id=config.tg_bot.support_id,
                                       text=f'Заказ № {number_order} пользователь {executor.tg_id} '
                                            f'@{(await rq.get_user_tg_id(tg_id=executor.tg_id)).username} '
                                            f'не обновлена клавиатура')

    await state.set_state(default_state)


@router.callback_query(F.data.startswith('deleteorder_'))
async def process_delete_order(callback: CallbackQuery, bot: Bot) -> None:
    """
    Удаление заказа после его рассылки
    :param callback:
    :param bot:
    :return:
    """
    logging.info(f'process_delete_order: {callback.message.chat.id}')
    id_order = int(callback.data.split('_')[1])
    executors_done = await rq.get_executors_status_order_id(order_id=id_order, status=rq.ExecutorStatus.done)
    list_id_tg_done = [done.tg_id for done in executors_done]
    executors_all = await rq.get_executors_order_id(order_id=id_order)

    for executor in executors_all:
        try:
            # удаляем у них сообщение с заказом
            await bot.delete_message(chat_id=executor.tg_id,
                                     message_id=executor.message_id)
            await rq.delete_executor(tg_id=executor.tg_id, order_id=id_order)
            # проходим по всем исполнителям, кто успел взять заказ
            if executor.tg_id in list_id_tg_done:
                await rq.set_busy_id(telegram_id=executor.tg_id, busy=0)

        except:
            await callback.message.answer(text=f'При удалении заказа № {id_order} у пользователя'
                                               f' {(await rq.get_user_tg_id(executor.tg_id)).username} возникла ошибка')
            await bot.send_message(chat_id=config.tg_bot.support_id,
                                   text=f'При удалении заказа № {id_order} у пользователя'
                                        f' {(await rq.get_user_tg_id(executor.tg_id)).username} возникла ошибка')
    await rq.delete_order(order_id=int(id_order))
    await callback.message.answer(text=f'Заказ {id_order} удален!')
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.answer()
