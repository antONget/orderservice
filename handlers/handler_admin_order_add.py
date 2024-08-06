from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.filters import StateFilter

from filter.admin_filter import IsAdmin
import keyboards.keyboard_admin_order_add as kb
import database.requests as rq

import logging

router = Router()


class Order(StatesGroup):
    title_services = State()
    cost_services = State()
    count_services = State()
    picture = State()


# УСЛУГА
@router.message(F.text == 'Услуга', IsAdmin())
async def process_change_list_services(message: Message) -> None:
    """
    Действие с услугой - Редактировать/Выбрать
    :param message:
    :return:
    """
    logging.info(f'process_change_list_services: {message.chat.id}')
    await message.answer(text='Вы можете добавить услугу в базу или изменить уже созданные!',
                         reply_markup=kb.keyboard_edit_select_services())


# УСЛУГА -> Редактировать -> [Добавить][Изменить]
@router.callback_query(F.data == 'edit_services')
async def process_edit_list_services(callback: CallbackQuery) -> None:
    """
    Действие с услугой при ее Редактировании -> Добавить/Изменить
    :param callback:
    :return:
    """
    logging.info(f'process_edit_list_services: {callback.message.chat.id}')
    await callback.message.answer(text='Вы можете добавить услугу в базу или изменить уже созданные!',
                                  reply_markup=kb.keyboard_edit_services())


# УСЛУГА -> Редактировать -> Добавить - ввод названия услуги
@router.callback_query(F.data == 'append_services')
async def process_append_services(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Добавление услуги - ввод названия услуги
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_append_services: {callback.message.chat.id}')
    await callback.message.answer(text='Введите название услуги!')
    await state.set_state(Order.title_services)


# УСЛУГА -> Редактировать -> Добавить - Запрашиваем стоимость услуги
@router.message(IsAdmin(), StateFilter(Order.title_services))
async def process_get_title_services(message: Message, state: FSMContext) -> None:
    """
    Получаем название услуги -> Запрашиваем стоимость услуги
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_get_title_services: {message.chat.id}')
    await state.update_data(title_services=message.text)
    await message.answer(text=f'Укажите стоимость за услугу: <b>{message.text}</b>')
    await state.set_state(Order.cost_services)


# УСЛУГА -> Редактировать -> Добавить - Запрашиваем количество исполнителей
@router.message(IsAdmin(), StateFilter(Order.cost_services))
async def process_get_cost_services(message: Message, state: FSMContext) -> None:
    """
    Получаем стоимость услуги -> Запрашиваем количество исполнителей
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_get_cost_services: {message.chat.id}')
    try:
        cost_services = int(message.text)
    except:
        await message.answer(text='Некорректно введена стоимость! Повторите ввод стоимости услуги.')
        return
    await state.update_data(cost_services=cost_services)
    data = await state.get_data()
    await message.answer(text=f'Укажите количество исполнителей для услуги: '
                              f'<b>{data["title_services"]}</b>')
    await state.set_state(Order.count_services)


# УСЛУГА -> Редактировать -> Добавить - Запрос прислать изображение (Пропустить)
@router.message(IsAdmin(), StateFilter(Order.count_services))
async def process_get_count_services(message: Message, state: FSMContext) -> None:
    """
    Получаем стоимость услуги -> Запрос прислать изображение (Пропустить)
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_get_count_services: {message.chat.id}')
    try:
        count_services = int(message.text)
    except:
        await message.answer(text='Некорректно введено количество исполнителей! Повторите ввод.')
        return
    await state.update_data(count_services=count_services)
    await message.answer(text=f'Пришлите изображение для услуги',
                         reply_markup=kb.keyboard_add_picture())
    await state.set_state(Order.picture)


# УСЛУГА -> Редактировать -> Добавить - Получаем изображение
@router.message(F.photo, IsAdmin(), StateFilter(Order.picture))
async def process_get_picture_services(message: Message, state: FSMContext) -> None:
    """
    Получаем изображение для услуги и добавляем новую услугу в базу
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_get_picture_services: {message.chat.id}')
    id_photo = message.photo[-1].file_id
    await state.update_data(picture_services=id_photo)
    data = await state.get_data()
    order_data = {"title_services": data["title_services"],
                  "cost_services": data["cost_services"],
                  "count_services": data["count_services"],
                  "picture_services": data["picture_services"]}
    await rq.add_service(data=order_data)
    await message.answer_photo(photo=data["picture_services"],
                               caption=f'<b>Услуга добавлена в базу:</b>\n\n'
                                       f'<i>Название услуги:</i> {data["title_services"]}\n'
                                       f'<i>Стоимость услуги:</i> {data["cost_services"]}\n'
                                       f'<i>Количество исполнителей:</i> {data["count_services"]}\n',
                               reply_markup=kb.keyboard_confirmation_append_services())
    await state.set_state(default_state)


# УСЛУГА -> Редактировать -> Добавить - Пропустить добавления изображения
@router.callback_query(StateFilter(Order.picture))
async def process_pass_picture_services(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_pass_picture_services')
    await state.update_data(picture_services='None')
    data = await state.get_data()
    order_data = {"title_services": data["title_services"],
                  "cost_services": data["cost_services"],
                  "count_services": data["count_services"],
                  "picture_services": data["picture_services"]}
    await rq.add_service(data=order_data)
    await callback.message.answer(text=f'<b>Услуга добавлена в базу:</b>\n\n'
                                       f'<i>Название услуги:</i> {data["title_services"]}\n'
                                       f'<i>Стоимость услуги:</i> {data["cost_services"]}\n'
                                       f'<i>Количество исполнителей:</i> {data["count_services"]}\n',
                                  reply_markup=kb.keyboard_confirmation_append_services())
    await state.set_state(default_state)


# завершаем добавление услуг
@router.callback_query(F.data == 'finish_services')
async def process_finish_append_services(callback: CallbackQuery) -> None:
    logging.info(f'process_finish_append_services: {callback.message.chat.id}')
    await process_change_list_services(callback.message)
