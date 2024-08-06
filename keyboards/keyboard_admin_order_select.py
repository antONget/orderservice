from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


# УСЛУГА -> Выбрать
def keyboards_select_services(list_services: list, back: int, forward: int, count: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для вывода списка услуг для из выбора и добавления в заказ
    :param list_services:
    :param back:
    :param forward:
    :param count:
    :return:
    """
    logging.info(f'keyboards_select_services')
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
        button = f'kserviceselect_{service.id}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'serviceselectback_{str(back)}')
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'serviceselectforward_{str(forward)}')

    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)

    return kb_builder.as_markup()


def keyboard_continue_orders() -> InlineKeyboardMarkup:
    """
    Клавиатура добавления услуги в заказ
    :return:
    """
    logging.info(f'keyboard_continue_orders')
    button_1 = InlineKeyboardButton(text='Далее',
                                    callback_data='continue_orders')
    button_2 = InlineKeyboardButton(text='Назад',
                                    callback_data='back_odrers')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]],)
    return keyboard


def keyboard_count_people() -> InlineKeyboardMarkup:
    """
    Клавиатура для указания количества исполнителей заказ по умолчанию
    :return:
    """
    logging.info(f'keyboard_count_people')
    button_1 = InlineKeyboardButton(text='Продолжить',
                                    callback_data='pass_people')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard


def keyboard_finish_orders() -> InlineKeyboardMarkup:
    """
    Клавиатура для возвращения после редактирования
    :return:
    """
    logging.info(f'keyboard_finish_orders')
    button_1 = InlineKeyboardButton(text='Отправить',
                                    callback_data='send_orders')
    button_2 = InlineKeyboardButton(text='Отмена',
                                    callback_data='cancel_orders')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]],)
    return keyboard


def keyboard_finish_orders_one_press() -> None:
    """
    Клавиатура для замены (обеспечивает однократное нажатие на кнопку "Отправить" - подменяет колбеки)
    :return:
    """
    button_1 = InlineKeyboardButton(text='Отпрaвить',
                                    callback_data=' ')
    button_2 = InlineKeyboardButton(text='Отмeна',
                                    callback_data=' ')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


def keyboard_ready_player_() -> InlineKeyboardMarkup:
    """
    Клавиатура выводится пользователям до момента окончания рассылки
    :return:
    """
    button_1 = InlineKeyboardButton(text='Подождите...',
                                    callback_data='---')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard


def keyboard_finish_orders_one_press_del(id_order) -> InlineKeyboardMarkup:
    """
    Клавиатура добавляет кнопку удалить
    :return:
    """
    button_1 = InlineKeyboardButton(text='Отпрaвить',
                                    callback_data=' ')
    button_2 = InlineKeyboardButton(text='Отмeна',
                                    callback_data=' ')
    button_3 = InlineKeyboardButton(text='Удалить',
                                    callback_data=f'deleteorder_{id_order}')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2], [button_3]],
    )
    return keyboard


# клавиатура подтверждения готовности участия в заказе с id = id_services
def keyboard_ready_player(id_order) -> InlineKeyboardMarkup:
    """
    Устанавливаем клавиатуру для пользователей после окончания рассылки
    :param id_order:
    :return:
    """
    button_1 = InlineKeyboardButton(text='Да',
                                    callback_data=f'ready_yes_{id_order}')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard
