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
async def process_select_services(callback: CallbackQuery) -> None:
    logging.info(f'process_select_services: {callback.message.chat.id}')
    list_services = [service for service in await rq.get_service()]
    back = 0
    forward = 2
    count_item = 6
    keyboard = kb.keyboards_select_services(list_services=list_services, back=back, forward=forward,
                                            count=count_item)
    await callback.message.answer(text='Выберите услугу для создания заказа:',
                                  reply_markup=keyboard)


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


# добавление услуги в заказ
@router.callback_query(F.data.startswith('kserviceselect'))
async def process_serviceselect(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_serviceselect: {callback.message.chat.id}')
    service_id = int(callback.data.split('_')[1])
    await state.update_data(service_id=service_id)
    service_info = await rq.get_service_id(service_id=service_id)
    await state.update_data(select_cost_service=service_info.cost_services)
    await callback.message.answer(text=f'Услуга: <b>{service_info.title_services}</b>,\n'
                                       f'Оплата для одного исполнителя: <b>{service_info.cost_services}</b>',
                                  reply_markup=kb.keyboard_continue_orders())


@router.callback_query(F.data == 'back_odrers')
async def process_back_odrers(callback: CallbackQuery) -> None:
    """
    Возврат к выбору услуги для добавления в заказ
    :param callback:
    :return:
    """
    logging.info(f'process_back_odrers: {callback.message.chat.id}')
    await process_select_services(callback)


@router.callback_query(F.data == 'continue_orders')
async def process_continue_orders(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Продолжение добавления услуги в заказ - запрос ввода ID клиента
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_continue_orders: {callback.message.chat.id}')
    await callback.message.answer(text=f'Напишите ID клиента:')
    await state.set_state(OrderSelect.set_comment_service)


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
    # last_order = get_id_last_orders()
    # if last_order:
    #     number_orders = last_order[0] + 1
    # else:
    #     number_orders = last_order
    data = await state.get_data()
    service_id = data['service_id']
    service_info = await rq.get_service_id(service_id=service_id)
    picture = service_info.picture_services
    if picture == 'None':
        await message.answer(text=f'<b>Заказ №{service_info.id + 1}:</b>\n\n'
                                  f'Услуга: {service_info.title_services}.\n'
                                  f'Стоимость: {service_info.cost_services}\n'
                                  f'ID клиента: <code>{data["select_comment_service"]}</code>\n'
                                  f'Опубликовать?',
                             reply_markup=kb.keyboard_finish_orders(),
                             parse_mode='html')
    else:
        await message.answer_photo(photo=picture,
                                   caption=f'<b>Заказ №{service_info.id + 1}:</b>\n\n'
                                           f'Услуга: {service_info.title_services}.\n'
                                           f'Стоимость: {service_info.cost_services}\n'
                                           f'ID клиента: <code>{data["select_comment_service"]}</code>\n'
                                           f'Опубликовать?',
                                   reply_markup=kb.keyboard_finish_orders(),
                                   parse_mode='html')
    await state.set_state(default_state)


@router.callback_query(F.data == 'cancel_orders')
async def process_cancel_odrers(callback: CallbackQuery) -> None:
    """
    Отмена публикации заказа
    :param callback:
    :return:
    """
    logging.info(f'process_cancel_odrers: {callback.message.chat.id}')
    await process_select_services(callback)


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
    data = {"title_services": service_info.title_services,
            "cost_services": service_info.cost_services,
            "comment": data["select_comment_service"],
            "count_people": service_info.count_services}
    await rq.add_order(data=data)

    last_order = [order for order in await rq.get_orders()][-1]
    number_order = last_order.id
    # список для рассылки
    list_sandler = [user for user in await rq.get_all_users()]
    list_mailing = []
    for user in list_sandler:
        # супер администраторам не отправляем
        if not await check_super_admin(telegram_id=user.telegram_id):
            result = get_telegram_user(user_id=user.telegram_id, bot_token=config.tg_bot.token)
            if 'result' in result:
                if not service_info.picture_services == 'None':
                    msg = await bot.send_photo(photo=service_info.picture_services,
                                               chat_id=user.telegram_id,
                                               caption=f'Появился заказ № {number_order} на : {service_info.title_services}.\n'
                                                       f'Стоимость {service_info.cost_services}\n'
                                                       f'Комментарий <code>{data["select_comment_service"]}</code>\n'
                                                       f'Готовы выполнить?',
                                               reply_markup=kb.keyboard_ready_player_())
                else:
                    msg = await bot.send_message(chat_id=user.telegram_id,
                                                 text=f'Появился заказ № {number_order} на : {data["select_title_service"]}.\n'
                                                      f'Стоимость {service_info.cost_services}\n'
                                                      f'Комментарий <code>{data["select_comment_service"]}</code>\n'
                                                      f'Готовы выполнить?',
                                                 reply_markup=kb.keyboard_ready_player_())
            # формируем строку для записи в список рассылки
            iduser_idmessage = f'{user.telegram_id}_{msg.message_id}'
            list_mailing.append(iduser_idmessage)

    await callback.message.edit_reply_markup(reply_markup=kb.keyboard_finish_orders_one_press_del(number_order))
    await callback.message.answer(text=f'Заказ № {number_order} успешно отправлен!')
    # создаем строку списка рассылки
    list_mailing_str = ','.join(list_mailing)
    await rq.update_list_sandler(list_mailing_str=list_mailing_str, id_order=number_order)
    # изменяем клавиатуру у пользователей
    for row in list_mailing:
        result = get_telegram_user(user_id=row.split('_')[0], bot_token=config.tg_bot.token)
        if 'result' in result:
            await bot.edit_message_reply_markup(chat_id=int(row.split('_')[0]),
                                                message_id=int(row.split('_')[1]),
                                                reply_markup=kb.keyboard_ready_player(id_order=number_order))

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
    info_order = await rq.get_orders_id(order_id=id_order)

    list_player = info_order.players.split(',')
    list_sandler = info_order.sandler.split(',')
    # проходим по всем исполнителям, кто успел взять заказ
    for player in list_player:
        try:
            # удаляем у них сообщение с заказом
            await bot.delete_message(chat_id=int(player.split('.')[1]),
                                     message_id=int(player.split('.')[2]))
            # обнуляем занятость
            await rq.set_busy_id(telegram_id=int(player.split('.')[1]), busy=0)
        except:
            await callback.message.answer(text=f'При удалении p заказа № {id_order} у пользователя {player}'
                                               f' возникла ошибка')
    # проходим по списку рассылки, если он не пустой
    if list_sandler == '':
        for sandler in list_sandler:
            try:
                await bot.delete_message(chat_id=int(sandler.split('_')[0]),
                                         message_id=int(sandler.split('_')[1]))
            except:
                await callback.message.answer(text=f'При удалении заказа № {id_order} у пользователя {sandler}'
                                                   f' возникла ошибка')
    await rq.delete_order(order_id=int(id_order))
    await callback.message.answer(text=f'Заказ {id_order} удален!')