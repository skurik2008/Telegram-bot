"""Модуль содержит функции для создания и работы с базой данных,
необходимой для реализации команды /history"""

import sqlite3

def connect():
    """
    Функция создает подключение к базе данных db.db
    :return: объект подключения
    """
    conn = sqlite3.connect('db.db')
    return conn

def init_table():
    """
    Функция создает в базе данных таблицу history со столбцами:
    id_пользователя, название команды бота, дата и время ввода команды,
    город для поиска отелей, результат выполнения команды в виде списка отелей
    """
    con = connect()
    cursorObj = con.cursor()
    cursorObj.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, "
                      "user_id INTEGER, "
                      "command text, "
                      "date text, "
                      "city text, "
                      "result text)")
    con.commit()

def add_value(id_user, command, date, city, value):
    """
    Функция заполняет таблицу данными
    :param id_user: id_пользователя
    :param command: название команды бота
    :param date: дата и время ввода команды
    :param city: город для поиска отелей
    :param value: результат выполнения команды в виде списка отелей
    """
    con = connect()
    cursorObj = con.cursor()
    cursorObj.execute("INSERT INTO history (user_id, command, date, city, result) VALUES(?, ?, ?, ?, ?)",
                  (id_user, command, date, city, value))
    con.commit()

def select_data(user, date):
    """
    Функция формирует новую таблицу, отсортированную по пользователю и дате
    :param user: крайний message из чата
    :param date: дата, запрашиваемая пользователем для вывода истории
    :return: список строк отсортированной таблицы
    """
    con = connect()
    cursorObj = con.cursor()
    date_for_select = date + '%'
    cursorObj.execute("SELECT command, date, city, result FROM history WHERE user_id = ? AND date LIKE ?",
                      (user.from_user.id, date_for_select))
    result = cursorObj.fetchall()
    return result
