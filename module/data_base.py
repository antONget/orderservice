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
    print("table_users")
    sql.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        token_auth TEXT,
        telegram_id INTEGER,
        username TEXT,
        is_admin INTEGER,
        is_busy INTEGER
    )""")
    db.commit()


def table_channel() -> None:
    print("table_channel")
    sql.execute("""CREATE TABLE IF NOT EXISTS channel(
        id INTEGER PRIMARY KEY,
        channel_id INTEGER,
        type TEXT
    )""")
    db.commit()


def table_services() -> None:
    print("table_services")
    sql.execute("""CREATE TABLE IF NOT EXISTS services(
        id INTEGER PRIMARY KEY,
        title_services TEXT,
        cost_services INTEGER,
        count_services INTEGER,
        picture_services TEXT
    )""")
    db.commit()


def table_orders() -> None:
    print("table_orders")
    sql.execute("""CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY,
        title_services TEXT,
        cost_services INTEGER,
        comment TEXT,
        count_people INTEGER,
        players TEXT,
        sendler TEXT,
        change TEXT,
        report TEXT
    )""")
    db.commit()


def table_statistic() -> None:
    print("table_orders")
    sql.execute("""CREATE TABLE IF NOT EXISTS statistic(
        id INTEGER PRIMARY KEY,
        cost_services INTEGER,
        count_people INTEGER,
        players TEXT
    )""")
    db.commit()


# УСЛУГИ - добавление услуги
def add_services(title_services, cost_services, count_services, picture_services) -> None:
    print("add_services")
    sql.execute(f'INSERT INTO services (title_services, cost_services, count_services, picture_services) '
                f'VALUES ("{title_services}", "{cost_services}", "{count_services}", "{picture_services}")')
    db.commit()


# УСЛУГИ - получение списка названий услуг
def get_list_services() -> list:
    print("get_list_services")
    sql.execute('SELECT title_services FROM services')
    list_username = [row for row in sql.fetchall()]
    return list_username


# УСЛУГИ - получение услуги по ее названию
def get_row_services(title_services) -> list:
    print("get_row_services")
    sql.execute('SELECT * FROM services WHERE title_services = ?', (title_services,))
    row_services = [row for row in sql.fetchall()]
    return row_services


# УСЛУГИ - удалить услугу
def delete_services(title_services):
    print("delete_services")
    sql.execute('DELETE FROM services WHERE title_services = ?', (title_services,))
    db.commit()


# УСЛУГИ - обновление названия и стоимости услуги
def update_service(title_services, title_services_new, cost):
    print("update_service")
    sql.execute('UPDATE services SET title_services = ?, cost_services = ? WHERE title_services = ?',
                (title_services_new, cost, title_services))
    db.commit()


# УСЛУГИ - получение стоимости услуги
def get_cost_service(title_services) -> int:
    print("get_cost_service")
    return sql.execute('SELECT cost_services FROM services WHERE title_services = ?', (title_services,)).fetchone()[0]


# ПОЛЬЗОВАТЕЛЬ - проверка на админа
def check_command_for_admins(message: Message) -> bool:
    print("check_command_for_admins")
    # Выполнение запроса для получения всех telegram_id из таблицы admins
    sql.execute('SELECT telegram_id FROM users WHERE is_admin = ?', (1,))
    # Извлечение результатов запроса и сохранение их в список
    telegram_ids = [row[0] for row in sql.fetchall()]
    # print('check_command_for_admins', telegram_ids)
    # Закрытие соединения
    return message.chat.id in telegram_ids or str(message.chat.id) == str(config.tg_bot.admin_ids)


# ПОЛЬЗОВАТЕЛЬ - проверка на авторизоанного пользователя
def check_command_for_user(message: Message) -> bool:
    print("check_command_for_user")
    # Выполнение запроса для получения всех telegram_id из таблицы admins
    sql.execute('SELECT telegram_id FROM users')
    # Извлечение результатов запроса и сохранение их в список
    telegram_ids = [row[0] for row in sql.fetchall()]
    # Закрытие соединения
    print('check_command_for_user', telegram_ids, message.chat.id in telegram_ids)
    return message.chat.id in telegram_ids


# ПОЛЬЗОВАТЕЛЬ - верификация токена
def check_token(message: Message) -> bool:
    print("check_token")
    # Выполнение запроса для получения token_auth
    sql.execute('SELECT token_auth, telegram_id  FROM users')
    list_token = [row for row in sql.fetchall()]
    # Извлечение результатов запроса и сохранение их в список
    print('check_token', list_token)
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
    sql.execute(f'INSERT INTO users (token_auth, telegram_id, username, is_admin, is_busy) '
                f'VALUES ("{token_new}", "telegram_id", "username", 0, 0)')
    db.commit()


# ПОЛЬЗОВАТЕЛЬ - добавления сгенерированного токена
def add_super_admin(id_admin, user) -> None:
    logging.info(f'add_super_admin')
    sql.execute('SELECT telegram_id FROM users')
    super_admin = [row[0] for row in sql.fetchall()]

    if int(id_admin) not in super_admin:
        sql.execute(f'INSERT INTO users (token_auth, telegram_id, username, is_admin, is_busy) '
                    f'VALUES ("SUPERADMIN", {id_admin}, "{user}", 1, 0)')
        db.commit()


# ПРИВЯЗАТЬ - правка канала
def add_channel(channel) -> None:
    logging.info(f'add_channel')
    sql.execute('SELECT channel_id FROM channel WHERE type = ?', ('channel',))
    list_channel = [row[0] for row in sql.fetchall()]
    if list_channel:
        print('1.channel', channel)
        sql.execute(f"UPDATE channel SET channel_id = ? WHERE type = ?",
                    (channel, 'channel',))
    else:
        print('0.channel', channel)
        sql.execute(f'INSERT INTO channel (channel_id, type)'
                    f'VALUES ("{channel}", "channel")')
    db.commit()


# ПРИВЯЗАТЬ - правка беседы
def add_group(group) -> None:
    logging.info(f'add_group')
    sql.execute('SELECT channel_id FROM channel WHERE type = ?', ('group',))
    list_channel = [row[0] for row in sql.fetchall()]
    if list_channel:
        print('1.group:', group)
        sql.execute(f"UPDATE channel SET channel_id = ? WHERE type = ?",
                    (group, 'group',))
    else:
        print('0.group', group)
        sql.execute(f'INSERT INTO channel (channel_id, type)'
                    f'VALUES ("{group}", "group")')
    db.commit()


def get_channel() -> list:
    logging.info(f'get_channel')
    sql.execute('SELECT * FROM channel')
    channel_id = [row[1] for row in sql.fetchall()]
    return channel_id


# ПОЛЬЗОВАТЕЛЬ - список пользователей верифицированных в боте
def get_list_users() -> list:
    logging.info(f'get_list_users')
    sql.execute('SELECT telegram_id, username FROM users WHERE NOT username = ?', ('username',))
    list_username = [row for row in sql.fetchall()]
    return list_username
def get_list_users_notadmin() -> list:
    logging.info(f'get_list_users_notadmin')
    sql.execute('SELECT telegram_id, username FROM users WHERE NOT username = ? AND is_admin = ?', ('username', 0))
    list_username = [row for row in sql.fetchall()]
    return list_username

# ПОЛЬЗОВАТЕЛЬ - список админов
def get_list_admin() -> list:
    logging.info(f'get_list_admin')
    sql.execute('SELECT telegram_id FROM users WHERE is_admin = ?', (1,))
    list_admin = [row for row in sql.fetchall()]
    return list_admin


# ПОЛЬЗОВАТЕЛЬ - имя пользователя по его id
def get_user(telegram_id):
    logging.info(f'get_user')
    return sql.execute('SELECT username FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()


# ПОЛЬЗОВАТЕЛЬ - получить занятость
def get_busy_id(telegram_id):
    logging.info(f'get_busy_id')
    return sql.execute('SELECT is_busy FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()[0]


# ПОЛЬЗОВАТЕЛЬ - удалить пользователя
def delete_user(telegram_id):
    logging.info(f'delete_user')
    sql.execute('DELETE FROM users WHERE telegram_id = ?', (telegram_id,))
    db.commit()


# ПОЛЬЗОВАТЕЛЬ - установить занятость
def set_busy_id(busy, telegram_id):
    logging.info(f'set_busy_id')
    sql.execute('UPDATE users SET is_busy = ? WHERE telegram_id = ?', (busy, telegram_id))
    db.commit()


# АДМИНИСТРАТОРЫ - список администраторов
def get_list_admins() -> list:
    logging.info(f'get_list_admins')
    sql.execute('SELECT telegram_id, username FROM users WHERE is_admin = ? AND NOT username = ?', (1, 'username'))
    list_admins = [row for row in sql.fetchall()]
    return list_admins


# АДМИНИСТРАТОРЫ - список пользователей не являющихся администраторами
def get_list_notadmins() -> list:
    logging.info(f'get_list_notadmins')
    sql.execute('SELECT telegram_id, username FROM users WHERE is_admin = ? AND NOT username = ?', (0, 'username'))
    list_notadmins = [row for row in sql.fetchall()]
    return list_notadmins

# АДМИНИСТРАТОРЫ - назначить пользователя администратором
def set_admins(telegram_id):
    logging.info(f'set_admins')
    sql.execute('UPDATE users SET is_admin = ? WHERE telegram_id = ?', (1, telegram_id))
    db.commit()


# АДМИНИСТРАТОРЫ - разжаловать пользователя из администраторов
def set_notadmins(telegram_id):
    logging.info(f'set_notadmins')
    sql.execute('UPDATE users SET is_admin = ? WHERE telegram_id = ?', (0, telegram_id))
    db.commit()


# ЗАКАЗ - создание нового заказа
def add_orders(title_services, cost_services, comment, count_people) -> None:
    logging.info(f'add_orders')
    sql.execute(f'INSERT INTO orders (title_services, cost_services, comment, count_people, players, sendler, change, report) '
                f'VALUES ("{title_services}", "{cost_services}", "{comment}", "{count_people}", "players", "sendler", "change", "report")')
    db.commit()


# ЗАКАЗЫ - получение заказа по ее id
def get_row_orders_id(id_order) -> list:
    logging.info(f'get_row_orders_id')
    sql.execute('SELECT * FROM orders WHERE id = ?', (id_order,))
    row_services = [row for row in sql.fetchall()]
    return row_services


# ЗАКАЗЫ - получение id последнего заказа
def get_id_last_orders() -> int:
    logging.info(f'get_id_last_orders')
    sql.execute('SELECT id FROM orders')
    row_id = [row for row in sql.fetchall()]
    print(row_id)
    if row_id:
        return row_id[-1]
    else:
        return 0


# ЗАКАЗЫ - обновление списка исполнителей
def update_list_players(players, id_orders):
    logging.info(f'update_list_players')
    sql.execute('UPDATE orders SET players = ? WHERE id = ?', (players, id_orders))
    db.commit()


# ЗАКАЗЫ - обновление списка рассылки
def update_list_sendlers(list_mailing_str, id_orders):
    logging.info(f'update_list_sendlers')
    sql.execute('UPDATE orders SET sendler = ? WHERE id = ?', (list_mailing_str, id_orders))
    db.commit()


# ЗАКАЗЫ - обновление списка отказавшихся
def update_list_refuses(list_refuses, id_orders):
    logging.info(f'update_list_refuses')
    sql.execute('UPDATE orders SET change = ? WHERE id = ?', (list_refuses, id_orders))
    db.commit()


# ЗАКАЗЫ - обновление отчета
def update_report(report, id_orders):
    logging.info(f'update_report')
    sql.execute('UPDATE orders SET report = ? WHERE id = ?', (report, id_orders))
    db.commit()


# СТАТИСТИКА - добавление данных
def add_statistic(cost_services, count_people, players) -> None:
    print("add_services")
    sql.execute(f'INSERT INTO statistic (cost_services, count_people, players) '
                f'VALUES ("{cost_services}", "{count_people}", "{players}")')
    db.commit()

# СТАТИСТИКА - добавление данных
def select_alldata_statistic() -> list:
    print("select_alldata_statistic")
    sql.execute(f'SELECT * FROM statistic')
    list_orders = [row for row in sql.fetchall()]
    return list_orders


def delete_statistic() -> None:
    print("delete_statistic")
    sql.execute(f'DELETE statistic')
    db.commit()


if __name__ == '__main__':
    # db = sqlite3.connect('/Users/antonponomarev/PycharmProjects/boiko/database.db', check_same_thread=False)
    # sql = db.cursor()
    # set_busy_id(0, 843554518) #5443784834
    print(get_list_users_notadmin())