from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


# УСЛУГА -> Редактировать -> Изменить
def keyboards_edit_services(list_services, back, forward, count):
    logging.info(f'keyboards_edit_services')
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_services)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток, то увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward > max_forward:
        forward = max_forward
        back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for service in list_services[back*count:(forward-1)*count]:
        text = service.title_services
        button = f'servicesedit_{service.id}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'serviceseditback_{str(back)}')
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'serviceseditforward_{str(forward)}')

    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)

    return kb_builder.as_markup()


# УСЛУГА -> Редактировать -> Изменить -> выбрана услуга для удаления или модификации
def keyboard_edit_list_services() -> InlineKeyboardMarkup:
    """
    Клавиатура для редактирования списка администраторов
    :return:
    """
    button_1 = InlineKeyboardButton(text='Редактировать',
                                    callback_data='modification_services')
    button_2 = InlineKeyboardButton(text='Удалить',
                                    callback_data='delete_services')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]],)
    return keyboard


# УСЛУГА -> Редактировать -> Изменить -> выбрана услуга для удаления или модификации
def keyboard_pass_edit_title_services() -> InlineKeyboardMarkup:
    """
    Клавиатура для пропуска редактирования названия услуги
    :return:
    """
    button_1 = InlineKeyboardButton(text='Пропустить',
                                    callback_data='pass_edit_service')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard


# Завершение процедуры редактирование услуги
def keyboard_finish_edit_service() -> InlineKeyboardMarkup:
    """
    Клавиатура для вовращения после редактирования
    :return:
    """
    button_1 = InlineKeyboardButton(text='Продолжить',
                                    callback_data='continue_edit_service')
    button_2 = InlineKeyboardButton(text='Завершить',
                                    callback_data='finish_edit_services')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]],)
    return keyboard
