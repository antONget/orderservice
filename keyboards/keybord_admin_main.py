from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboards_admin_one():
    button_1 = KeyboardButton(text='Услуга')
    button_2 = KeyboardButton(text='Статистика')
    button_0 = KeyboardButton(text='Скинуть занятость')
    button_3 = KeyboardButton(text='>>>')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1, button_2], [button_0], [button_3]],
                                   resize_keyboard=True)
    return keyboard


def keyboards_superadmin_one():
    button_1 = KeyboardButton(text='Услуга')
    button_2 = KeyboardButton(text='Статистика')
    button_0 = KeyboardButton(text='Скинуть занятость')
    button_3 = KeyboardButton(text='>>>')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1, button_2], [button_0], [button_3]],
                                   resize_keyboard=True)
    return keyboard


def keyboards_admin_two():
    button_2 = KeyboardButton(text='Пользователь')
    button_6 = KeyboardButton(text='Таблица')
    button_5 = KeyboardButton(text='<<<')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_2], [button_6], [button_5]],
                                   resize_keyboard=True)
    return keyboard


def keyboards_superadmin_two():
    button_1 = KeyboardButton(text='Администраторы')
    button_2 = KeyboardButton(text='Пользователь')
    button_3 = KeyboardButton(text='Прикрепить')
    button_4 = KeyboardButton(text='Сброс статистики')
    button_6 = KeyboardButton(text='Таблица')
    button_5 = KeyboardButton(text='<<<')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1, button_2], [button_3, button_4], [button_6], [button_5]],
                                   resize_keyboard=True)
    return keyboard
