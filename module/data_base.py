import sqlite3
from aiogram.types import Message
from config_data.config import Config, load_config

# Загружаем конфиг в переменную config
config: Config = load_config()
# можно использовать memory: вместо названия файла, чтобы хранить данные в оперативной памяти
db = sqlite3.connect('database.db', check_same_thread=False)
sql = db.cursor()


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


def check_command_for_admins(message: Message) -> bool:
    """
    Функция проводит верификацию пользователя
    :param message:
    :return:
    """
    # Выполнение запроса для получения всех telegram_id из таблицы admins
    sql.execute('SELECT telegram_id FROM users WHERE is_admin = 1')
    # Извлечение результатов запроса и сохранение их в список
    telegram_ids = [row[0] for row in sql.fetchall()]
    # Закрытие соединения
    return message.chat.id in telegram_ids or str(message.chat.id) == str(config.tg_bot.admin_ids)


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


def add_token(token_new) -> None:
    """
    Функция производит добавления пользователя в таблицу users
    :param token_new:
    :return: None
    """
    sql.execute(f'INSERT INTO users (token_auth, telegram_id, username, is_admin) '
                f'VALUES ("{token_new}", "telegram_id", "username", 0)')
    db.commit()


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
        for ch in list_channel:
            sql.execute(f"UPDATE channel SET is_send = ? WHERE channel_id = ?",
                        (0, ch))
        sql.execute(f"UPDATE channel SET is_send = ? WHERE channel_id = ?",
                    (1, channel))
    else:
        print('группы нет в списке')
        sql.execute(f'INSERT INTO channel (channel_id, is_send)'
                    f'VALUES ("{channel}", 1)')
        for ch in list_channel:
            sql.execute(f"UPDATE channel SET is_send = ? WHERE channel_id = ?",
                        (0, ch))

    db.commit()


def get_list_users() -> list:
    """
    Функция формирует список пользователей прошедших верефикацию
    :return:
    """
    sql.execute('SELECT telegram_id, username FROM users WHERE NOT username = ?', ('username',))
    list_username = [row for row in sql.fetchall()]
    return list_username


def get_user(telegram_id):
    """
    Функция выдает информацию о запрашиваемом пользователе
    :param telegram_id:
    :return:
    """
    return sql.execute('SELECT username FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()


def delete_user(telegram_id):
    """
    Функция выдает информацию о запрашиваемом пользователе
    :param telegram_id:
    :return:
    """
    sql.execute('DELETE FROM users WHERE telegram_id = ?', (telegram_id,))
    db.commit()

def get_list_admins() -> list:
    """
    Функция формирует список пользователей прошедших верефикацию
    :return:
    """
    sql.execute('SELECT telegram_id, username FROM users WHERE is_admin = ? AND NOT username = ?', (1, 'username'))
    list_admins = [row for row in sql.fetchall()]
    return list_admins


def get_list_notadmins() -> list:
    """
    Функция формирует список пользователей прошедших верефикацию
    :return:
    """
    sql.execute('SELECT telegram_id, username FROM users WHERE is_admin = ? AND NOT username = ?', (0, 'username'))
    list_notadmins = [row for row in sql.fetchall()]
    return list_notadmins


def set_admins(telegram_id):
    """
    Функция формирует список пользователей прошедших верефикацию
    :return:
    """
    sql.execute('UPDATE users SET is_admin = ? WHERE telegram_id = ?', (1, telegram_id))
    db.commit()

def set_notadmins(telegram_id):
    """
    Функция формирует список пользователей прошедших верефикацию
    :return:
    """
    sql.execute('UPDATE users SET is_admin = ? WHERE telegram_id = ?', (0, telegram_id))
    db.commit()

