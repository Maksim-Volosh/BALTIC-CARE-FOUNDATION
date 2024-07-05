import sqlite3
import bcrypt
from datetime import datetime

class Database():
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_db()

    def create_db(self):
        try:
            # Создаем таблицу пользователей
            query_users = ("CREATE TABLE IF NOT EXISTS users("
                           "id INTEGER PRIMARY KEY, "
                           "user_fullname TEXT, "
                           "user_phonenumber TEXT, "
                           "user_date TEXT, "
                           "user_tgid TEXT);")
            self.cursor.execute(query_users)
            
            # Создаем таблицу для записи рабочей информации
            query_work = ("CREATE TABLE IF NOT EXISTS work_records("
                          "id INTEGER PRIMARY KEY, "
                          "username TEXT, "
                          "start_time TEXT, "
                          "end_time TEXT, "
                          "total_time REAL, "
                          "collection REAL, "
                          "earnings REAL);")
            self.cursor.execute(query_work)

            self.connection.commit()
        except sqlite3.Error as error:
            print("Error while creating a sqlite table", error)

    def add_user(self, user_fullname, user_phonenumber, user_date, user_tgid):
        self.cursor.execute("INSERT INTO users(user_fullname, user_phonenumber, user_date, user_tgid) VALUES(?, ?, ?, ?)", 
                            (user_fullname, user_phonenumber, user_date, user_tgid))
        self.connection.commit()

    def get_user(self, user_tgid):
        users = self.cursor.execute("SELECT * FROM users WHERE user_tgid = ?", (user_tgid,))
        return users.fetchone()

    def add_work_record(self, username, start_time, end_time, total_time, collection, earnings):
        self.cursor.execute("INSERT INTO work_records(username, start_time, end_time, total_time, collection, earnings) VALUES(?, ?, ?, ?, ?, ?)",
                            (username, start_time, end_time, total_time, collection, earnings))
        self.connection.commit()

    def get_work_records(self, username):
        records = self.cursor.execute("SELECT * FROM work_records WHERE username = ?", (username,))
        return records.fetchall()

    def __del__(self):
        self.cursor.close()
        self.connection.close()

