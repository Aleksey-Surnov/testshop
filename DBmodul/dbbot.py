import sqlite3
import os


def command(func):
    def wrapper(self, *args, **kwargs):
        cursor = self._get_connection().cursor()              # открываем курсор
        res = func(self, *args, cursor = cursor, **kwargs)    # выполняем функцию
        self._get_connection().commit()                       # коммит при необходимости
        cursor.close()                                        # Закрываем курсор
        return res
    return wrapper


class DbHelper():
    def __init__(self, db_name: str):
        self.db_name = db_name
        self._connection = None  # connection object


    def _get_connection(self):
        if not self._connection: # ленивая инициализация соединения
            self._connection = sqlite3.connect(self.db_name, check_same_thread=False)
        return self._connection


    def __del__(self):
        if self._connection:      # закрытие соединения при удалении объекта как пример безопасной работы
            self._connection.close()


    @command
    def init_db(self, cursor, force: bool = False):
        if force:
            cursor.execute('DROP TABLE IF EXISTS catalog')
            cursor.execute('DROP TABLE IF EXISTS purchase')
            self._connection.commit()

        cursor.execute('''
                CREATE TABLE IF NOT EXISTS catalog (
                       id              INTEGER PRIMARY KEY,
                       name            VARCHAR(100),
                       description     VARCHAR(500),
                       price           INTEGER NOT NULL, 
                       teg             VARCHAR(20)
                       )''')

        cursor.execute('''
                CREATE TABLE IF NOT EXISTS purchase (
                        id             INTEGER PRIMARY KEY,
                        user_id        INTEGER NOT NULL,
                        name           VARCHAR(100),
                        price          INTEGER NOT NULL,
                        countofitems   INTEGER)''')


    @command
    def add_goods_id(self, cursor, name, description, price, teg):
        cursor.execute('INSERT INTO catalog (name, description, price, teg) VALUES (?,?,?,?)',
                       (name, description, price, teg))


    @command
    def get_all_catalog(self, cursor):
        res = cursor.execute('SELECT * FROM catalog').fetchall()
        return res


    @command
    def get_category_catalog(self, cursor, teg):
        res = cursor.execute('SELECT name, description, price FROM catalog WHERE teg=?', (teg,)).fetchall()
        return res


    @command
    def verify_user(self, cursor, user_id):
        res = cursor.execute('SELECT name, price, countofitems FROM purchase WHERE user_id=?',(user_id,))
        if res.fetchall() == []: return True
        return False


    @command
    def get_basket(self, cursor, user_id):
        res = cursor.execute(
            'SELECT name, SUM(price), SUM(countofitems) FROM purchase WHERE user_id=? GROUP BY name', (user_id,)).fetchall()
        return res


    @command
    def add_basket(self, cursor, user_id, name, price):
        cursor.execute('INSERT INTO purchase (user_id, name, price, countofitems) VALUES (?,?,?,1)',
                       (user_id, name, price))


    @command
    def delete_basket(self, cursor, user_id):
        cursor.execute('DELETE FROM purchase WHERE user_id=?', (user_id,))




