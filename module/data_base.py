import sqlite3
from aiogram.types import Message
from config_data.config import Config, load_config
import logging


# Загружаем конфиг в переменную config
config: Config = load_config()
# можно использовать memory: вместо названия файла, чтобы хранить данные в оперативной памяти
db = sqlite3.connect('database.db', check_same_thread=False)
sql = db.cursor()


# СОЗДАНИЕ ТАБЛИЦ
def table_users() -> None:
    """
    Создание таблицы администраторов
    :return: None
    """
    sql.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        token_auth TEXT,
        telegram_id INTEGER,
        username TEXT,
        is_admin INTEGER
    )""")
    db.commit()


def table_channel() -> None:
    """
    Создание таблицы каналов
    :return: None
    """
    sql.execute("""CREATE TABLE IF NOT EXISTS channel(
        id INTEGER PRIMARY KEY,
        channel_id INTEGER,
        is_send INTEGER
    )""")
    db.commit()


def table_services() -> None:
    """
    Создание таблицы администраторов
    :return: None
    """
    sql.execute("""CREATE TABLE IF NOT EXISTS services(
        id INTEGER PRIMARY KEY,
        title_services TEXT,
        cost_services INTEGER,
        count_services INTEGER
    )""")
    db.commit()


def table_orders() -> None:
    """
    Создание таблицы администраторов
    :return: None
    """
    sql.execute("""CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY,
        title_services TEXT,
        cost_services INTEGER,
        comment TEXT,
        count_people INTEGER,
        players TEXT,
        sendler TEXT
    )""")
    db.commit()


# УСЛУГИ - добавление услуги
def add_services(title_services, cost_services, count_services) -> None:
    sql.execute(f'INSERT INTO services (title_services, cost_services, count_services) '
                f'VALUES ("{title_services}", "{cost_services}", "{count_services}")')
    db.commit()


# УСЛУГИ - получение списка названий услуг
def get_list_services() -> list:
    """
    Функция формирует список пользователей прошедших верефикацию
    :return:
    """
    sql.execute('SELECT title_services FROM services')
    list_username = [row for row in sql.fetchall()]
    return list_username


# УСЛУГИ - получение услуги по ее названию
def get_row_services(title_services) -> list:
    """
    Функция формирует список пользователей прошедших верефикацию
    :return:
    """
    sql.execute('SELECT * FROM services WHERE title_services = ?', (title_services,))
    row_services = [row for row in sql.fetchall()]
    return row_services


# УСЛУГИ - удалить услугу
def delete_services(title_services):
    """
    Функция выдает информацию о запрашиваемом пользователе
    :param telegram_id:
    :return:
    """
    sql.execute('DELETE FROM services WHERE title_services = ?', (title_services,))
    db.commit()


# УСЛУГИ - обновление названия и стоимости услуги
def update_service(title_services, title_services_new, cost):
    sql.execute('UPDATE services SET title_services = ?, cost_services = ? WHERE title_services = ?',
                (title_services_new, cost, title_services))
    db.commit()


# УСЛУГИ - получение стоимости услуги
def get_cost_service(title_services) -> int:
    """
    Функция формирует список пользователей прошедших верефикацию
    :return:
    """
    return sql.execute('SELECT cost_services FROM services WHERE title_services = ?', (title_services,)).fetchone()[0]


# ПОЛЬЗОВАТЕЛЬ - проверка на админа
def check_command_for_admins(message: Message) -> bool:
    """
    Функция проводит верификацию пользователя
    :param message:
    :return:
    """
    # Выполнение запроса для получения всех telegram_id из таблицы admins
    sql.execute('SELECT telegram_id FROM users WHERE is_admin = ?', (1,))
    # Извлечение результатов запроса и сохранение их в список
    telegram_ids = [row[0] for row in sql.fetchall()]
    print(telegram_ids)
    # Закрытие соединения
    return message.chat.id in telegram_ids or str(message.chat.id) == str(config.tg_bot.admin_ids)


# ПОЛЬЗОВАТЕЛЬ - проверка на авторизоанного пользователя
def check_command_for_user(message: Message) -> bool:
    """
    Функция проводит верификацию пользователя
    :param message:
    :return:
    """
    # Выполнение запроса для получения всех telegram_id из таблицы admins
    sql.execute('SELECT telegram_id FROM users')
    # Извлечение результатов запроса и сохранение их в список
    telegram_ids = [row[0] for row in sql.fetchall()]
    # Закрытие соединения
    print(telegram_ids, message.chat.id in telegram_ids)
    return message.chat.id in telegram_ids


# ПОЛЬЗОВАТЕЛЬ - верификация токена
def check_token(message: Message) -> bool:
    """
    Функция проводит верификацию пользователя по введенному TOKEN
    :param message:
    :return:
    """
    # Выполнение запроса для получения token_auth
    sql.execute('SELECT token_auth, telegram_id  FROM users')
    list_token = [row for row in sql.fetchall()]
    # Извлечение результатов запроса и сохранение их в список
    print(list_token)
    for row in list_token:
        token = row[0]
        telegram_id = row[1]
        if token == message.text and telegram_id == 'telegram_id':
            sql.execute('UPDATE users SET telegram_id = ?, username = ? WHERE token_auth = ?',
                        (message.chat.id, message.from_user.username, message.text))
            db.commit()
            return True
    db.commit()
    return False


# ПОЛЬЗОВАТЕЛЬ - добавления сгенерированного токена
def add_token(token_new) -> None:
    logging.info(f'add_token: {token_new}')
    sql.execute(f'INSERT INTO users (token_auth, telegram_id, username, is_admin) '
                f'VALUES ("{token_new}", "telegram_id", "username", 0)')
    db.commit()


# КАНАЛ - правка канала
def add_channel(channel) -> None:
    """
    Функция производит добавления пользователя в таблицу users
    :param token_new:
    :return: None
    """
    sql.execute('SELECT channel_id FROM channel')
    list_channel = [row[0] for row in sql.fetchall()]


    if int(channel) in list_channel:
        print('такая группа есть в списке')
        # for ch in list_channel:
        #     sql.execute(f"UPDATE channel SET is_send = ? WHERE channel_id = ?",
        #                 (0, ch))
        sql.execute(f"UPDATE channel SET is_send = ? WHERE channel_id = ?",
                    (1, channel))
    else:
        print('группы нет в списке')
        sql.execute(f'INSERT INTO channel (channel_id, is_send)'
                    f'VALUES ("{channel}", 1)')
        # for ch in list_channel:
        #     sql.execute(f"UPDATE channel SET is_send = ? WHERE channel_id = ?",
        #                 (0, ch))

    db.commit()


def get_channel() -> int:

    sql.execute('SELECT channel_id FROM channel')
    channel_id = [row for row in sql.fetchall()]
    return channel_id


# ПОЛЬЗОВАТЕЛЬ - список пользователей верифицированных в боте
def get_list_users() -> list:
    """
    Функция формирует список пользователей прошедших верефикацию
    :return:
    """
    sql.execute('SELECT telegram_id, username FROM users WHERE NOT username = ?', ('username',))
    list_username = [row for row in sql.fetchall()]
    return list_username


# ПОЛЬЗОВАТЕЛЬ - список админов
def get_list_admin() -> list:
    """
    Функция формирует список пользователей прошедших верефикацию
    :return:
    """
    sql.execute('SELECT telegram_id FROM users WHERE is_admin = ?', (1,))
    list_admin = [row for row in sql.fetchall()]
    return list_admin


# ПОЛЬЗОВАТЕЛЬ - имя пользователя по его id
def get_user(telegram_id):
    """
    Функция выдает информацию о запрашиваемом пользователе
    :param telegram_id:
    :return:
    """
    return sql.execute('SELECT username FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()


# ПОЛЬЗОВАТЕЛЬ - удалить пользователя
def delete_user(telegram_id):
    """
    Функция выдает информацию о запрашиваемом пользователе
    :param telegram_id:
    :return:
    """
    sql.execute('DELETE FROM users WHERE telegram_id = ?', (telegram_id,))
    db.commit()


# АДМИНИСТРАТОРЫ - список администраторов
def get_list_admins() -> list:
    """
    Функция формирует список пользователей прошедших верефикацию
    :return:
    """
    sql.execute('SELECT telegram_id, username FROM users WHERE is_admin = ? AND NOT username = ?', (1, 'username'))
    list_admins = [row for row in sql.fetchall()]
    return list_admins


# АДМИНИСТРАТОРЫ - список пользователей не являющихся администраторами
def get_list_notadmins() -> list:
    """
    Функция формирует список пользователей прошедших верефикацию
    :return:
    """
    sql.execute('SELECT telegram_id, username FROM users WHERE is_admin = ? AND NOT username = ?', (0, 'username'))
    list_notadmins = [row for row in sql.fetchall()]
    return list_notadmins

# АДМИНИСТРАТОРЫ - назначить пользователя администратором
def set_admins(telegram_id):
    """
    Функция формирует список пользователей прошедших верефикацию
    :return:
    """
    sql.execute('UPDATE users SET is_admin = ? WHERE telegram_id = ?', (1, telegram_id))
    db.commit()


# АДМИНИСТРАТОРЫ - разжаловать пользователя из администраторов
def set_notadmins(telegram_id):
    """
    Функция формирует список пользователей прошедших верефикацию
    :return:
    """
    sql.execute('UPDATE users SET is_admin = ? WHERE telegram_id = ?', (0, telegram_id))
    db.commit()


# ЗАКАЗ - создание нового заказа
def add_orders(title_services, cost_services, comment, count_people) -> None:
    sql.execute(f'INSERT INTO orders (title_services, cost_services, comment, count_people, players, sendler) '
                f'VALUES ("{title_services}", "{cost_services}", "{comment}", "{count_people}", "players", "sendler")')
    db.commit()


# ЗАКАЗЫ - получение заказа по ее id
def get_row_orders_id(id_services) -> list:
    """
    Функция формирует список пользователей прошедших верефикацию
    :return:
    """
    sql.execute('SELECT * FROM orders WHERE id = ?', (id_services,))
    row_services = [row for row in sql.fetchall()]
    return row_services


# ЗАКАЗЫ - получение id последнего заказа
def get_id_last_orders() -> list:
    """
    Функция формирует список пользователей прошедших верефикацию
    :return:
    """
    sql.execute('SELECT id FROM orders')
    row_id = [row for row in sql.fetchall()]
    print(row_id)
    return row_id[-1]


# ЗАКАЗЫ - обновление списка исполнителей
def update_list_players(players, id_orders):
    """
    Функция формирует список пользователей прошедших верефикацию
    :return:
    """
    sql.execute('UPDATE orders SET players = ? WHERE id = ?', (players, id_orders))
    db.commit()


# ЗАКАЗЫ - обновление списка рассылки
def update_list_sendlers(list_mailing_str, id_orders):
    """
    Функция формирует список пользователей прошедших верефикацию
    :return:
    """
    sql.execute('UPDATE orders SET sendler = ? WHERE id = ?', (list_mailing_str, id_orders))
    db.commit()


if __name__ == '__main__':
    db = sqlite3.connect('/Users/antonponomarev/PycharmProjects/boiko/database.db', check_same_thread=False)
    sql = db.cursor()
    sql.execute('DROP TABLE IF EXISTS orders')
    # table_users()
    # sql.execute('SELECT telegram_id FROM users WHERE is_admin = 1')