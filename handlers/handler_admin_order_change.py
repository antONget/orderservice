from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.filters import StateFilter

import keyboards.keyboard_admin_order_change as kb
import database.requests as rq
from handlers.handler_admin_order_add import process_change_list_services

import logging

router = Router()


class Order(StatesGroup):
    title_services = State()
    cost_services = State()
    count_services = State()
    edit_title_service = State()
    edit_cost_service = State()


@router.callback_query(F.data == 'change_services')
async def process_change_services(callback: CallbackQuery) -> None:
    """
    Выбор услуги для ее редактирования
    :param callback:
    :return:
    """
    logging.info(f'process_change_services: {callback.message.chat.id}')
    list_services = [service for service in await rq.get_service()]
    back = 0
    forward = 2
    count_item = 6
    keyboard = kb.keyboards_edit_services(list_services=list_services, back=back, forward=forward, count=count_item)
    await callback.message.answer(text='Выберите услугу из базы',
                                  reply_markup=keyboard)


# >>>>
@router.callback_query(F.data.startswith('serviceseditforward'))
async def process_serviceseditforward(callback: CallbackQuery) -> None:
    """
    Пагинация вперед по списку услуг для их редактирования
    :param callback:
    :return:
    """
    logging.info(f'process_serviceseditforward: {callback.message.chat.id}')
    list_services = [service for service in await rq.get_service()]
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    count_item = 6
    keyboard = kb.keyboards_edit_services(list_services=list_services, back=back, forward=forward, count=count_item)
    try:
        await callback.message.edit_text(text='Выберите услугу из базы',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите услугу из базы.',
                                         reply_markup=keyboard)


# <<<<
@router.callback_query(F.data.startswith('serviceseditback'))
async def process_serviceseditback(callback: CallbackQuery) -> None:
    """
    Пагинация назад по списку услуг для его редактирования
    :param callback:
    :return:
    """
    logging.info(f'process_serviceseditback: {callback.message.chat.id}')
    list_services = [service for service in await rq.get_service()]
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    count_item = 6
    keyboard = kb.keyboards_edit_services(list_services=list_services, back=back, forward=forward, count=count_item)
    try:
        await callback.message.edit_text(text='Выберите услугу из базы',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите услугу из базы.',
                                         reply_markup=keyboard)


# удаление или модификация выбранной услуги
@router.callback_query(F.data.startswith('servicesedit'))
async def process_servicesedit(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Выбор действия с услугой - Удаление/Модификация
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_servicesedit: {callback.message.chat.id}')
    service_id = int(callback.data.split('_')[1])
    await state.update_data(service_id=service_id)
    service_info = await rq.get_service_id(service_id=service_id)
    await callback.message.answer(text=f'Что нужно сделать с услугой <b>{service_info.title_services}</b>',
                                  reply_markup=kb.keyboard_edit_list_services())


# УСЛУГА - удаление услуги
@router.callback_query(F.data == 'delete_services')
async def process_delete_services(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_delete_services: {callback.message.chat.id}')
    data = await state.get_data()
    service_id = data['service_id']
    await rq.delete_service(service_id=service_id)
    service_info = await rq.get_service_id(service_id=service_id)
    await callback.message.answer(text=f'Услуга <b>{service_info.title_services}</b>'
                                       f' успешно удалена')
    await process_change_list_services(callback.message)


# УСЛУГА - модификация услуги
@router.callback_query(F.data == 'modification_services')
async def process_modification_services(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Модификация услуги - ввод нового названия
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_modification_services: {callback.message.chat.id}')
    data = await state.get_data()
    service_id = data['service_id']
    service_info = await rq.get_service_id(service_id=service_id)
    await state.update_data(edit_title_service_new=service_info.title_services)
    await callback.message.answer(text=f'Введите новое название для услуги '
                                       f'<b>{service_info.title_services}</b>, '
                                       f'или переходите к изменению стоимости ее выполнения',
                                  reply_markup=kb.keyboard_pass_edit_title_services())
    await state.set_state(Order.edit_title_service)


@router.callback_query(F.data == 'pass_edit_service', StateFilter(Order.edit_title_service))
async def process_pass_edit_service(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Модификация услуги - пропустить изменение названия - ввод стоимости услуги
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_pass_edit_service: {callback.message.chat.id}')
    data = await state.get_data()
    service_id = data['service_id']
    service_info = await rq.get_service_id(service_id=service_id)
    await callback.message.answer(text=f'Укажите стоимость услуги:'
                                       f'<b>{service_info.title_services}</b>')
    await state.set_state(Order.edit_cost_service)


# Получаем наименование услуги
@router.message(F.text, StateFilter(Order.edit_title_service))
async def process_get_edittitle_services(message: Message, state: FSMContext) -> None:
    """
    Модификация услуги - Получаем название услуги - запрашиваем стоимость
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_get_edittitle_services: {message.chat.id}')
    await state.update_data(edit_title_service_new=message.text)
    data = await state.get_data()
    service_id = data['service_id']
    service_info = await rq.get_service_id(service_id=service_id)
    await message.answer(text=f'Укажите стоимость услуги:'
                              f'<b>{service_info.title_services}</b>')
    await state.set_state(Order.edit_cost_service)


@router.message(F.text, StateFilter(Order.edit_cost_service))
async def process_get_editcost_services(message: Message, state: FSMContext) -> None:
    """
    Модификация услуги - получаем стоимость - заносим модифицированную услугу в БД
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_get_editcost_services: {message.chat.id}')
    data = await state.get_data()
    service_id = data['service_id']
    await rq.update_service_id(service_id=service_id,
                               title_service=data["edit_title_service_new"],
                               cost_service=int(message.text))
    await message.answer(text=f'Вы внесли изменения в услугу <b>{data["edit_title_service_new"]}</b>\n'
                              f'Cтоимость: {message.text}',
                         reply_markup=kb.keyboard_finish_edit_service())
    await state.set_state(default_state)


# возвращение к списку услуг для редактирования
@router.callback_query(F.data == 'continue_edit_service')
async def process_continue_edit_service(callback: CallbackQuery) -> None:
    """
    Возвращаемся в диалог модификации услуги
    :param callback:
    :return:
    """
    logging.info(f'process_continue_edit_service: {callback.message.chat.id}')
    await process_change_services(callback)


# выход из редактирования
@router.callback_query(F.data == 'finish_edit_services')
async def process_finish_edit_services(callback: CallbackQuery) -> None:
    """
    Возвращаемся к диалогу редактирования услуги
    :param callback:
    :return:
    """
    logging.info(f'process_finish_edit_services: {callback.message.chat.id}')
    await process_change_list_services(callback.message)
