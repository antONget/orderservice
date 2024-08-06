from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# УСЛУГА
def keyboard_edit_select_services() -> InlineKeyboardMarkup:
    """
    Клавиатура для редактирования списка пользователей
    :return:
    """
    button_1 = InlineKeyboardButton(text='Редактировать',
                                    callback_data='edit_services')
    button_2 = InlineKeyboardButton(text='Выбрать',
                                    callback_data='select_services')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]],)
    return keyboard


# УСЛУГА -> Редактировать
def keyboard_edit_services() -> InlineKeyboardMarkup:
    """
    Клавиатура для редактирования списка пользователей
    :return:
    """
    button_1 = InlineKeyboardButton(text='Добавить',
                                    callback_data='append_services')
    button_2 = InlineKeyboardButton(text='Изменить',
                                    callback_data='change_services')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]],)
    return keyboard


# УСЛУГА -> Добавить - изображение
def keyboard_add_picture() -> InlineKeyboardMarkup:
    """
    Клавиатура для редактирования списка пользователей
    :return:
    """
    button_1 = InlineKeyboardButton(text='Пропустить',
                                    callback_data='pass_picture')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard


# УСЛУГА -> Редактировать -> Добавить
def keyboard_confirmation_append_services() -> InlineKeyboardMarkup:
    """
    Клавиатура для редактирования списка пользователей
    :return:
    """
    button_1 = InlineKeyboardButton(text='Добавить ещё',
                                    callback_data='edit_services')
    button_2 = InlineKeyboardButton(text='Закончить',
                                    callback_data='finish_services')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]],)
    return keyboard
