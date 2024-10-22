import secrets
import sqlite3
import string
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
            
            # Создаем таблицу для записи рабочих точек
            query_work_place = (
                "CREATE TABLE IF NOT EXISTS place ("
                "id INTEGER PRIMARY KEY, "
                "name TEXT, "
                "adress TEXT, "
                "url_map TEXT)"
            )
            self.cursor.execute(query_work_place)

            # Создаем таблицу для записи рабочей информации
            query_work = ("CREATE TABLE IF NOT EXISTS work_records("
                        "id INTEGER PRIMARY KEY, "
                        "username TEXT, "
                        "start_time TEXT, "
                        "end_time TEXT, "
                        "total_time REAL, "
                        "collection REAL, "
                        "earnings REAL, "
                        "collection_term REAL,"
                        "earnings_term REAL);")
            self.cursor.execute(query_work)
            
            # Создаем таблицу для записи токена регистрации
            query_token = ("CREATE TABLE IF NOT EXISTS tokens("
                        "id INTEGER PRIMARY KEY, "
                        "token TEXT UNIQUE);")
            self.cursor.execute(query_token)

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
    
    def delete_user(self, user_tgid):
        self.cursor.execute("DELETE FROM users WHERE user_tgid = ?", (user_tgid,))
        self.connection.commit()
    
    def delete_user_stats(self, user_tgid):
        self.cursor.execute("DELETE FROM work_records WHERE username = ?", (user_tgid,))
        self.connection.commit()
        
    def best_day_collection(self, username):
        self.cursor.execute(
            "SELECT * FROM work_records WHERE username = ? ORDER BY collection DESC LIMIT 1",
            (username,)
        )
        return self.cursor.fetchone()
    
    def worse_day_collection(self, username):
        self.cursor.execute(
            "SELECT * FROM work_records WHERE username = ? ORDER BY collection ASC LIMIT 1",
            (username,)
        )
        return self.cursor.fetchone()
    
    def total_collection_current_month(self):
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        self.cursor.execute(
            "SELECT SUM(collection) FROM work_records WHERE strftime('%Y', start_time) = ? AND strftime('%m', start_time) = ?",
            (str(current_year), f'{current_month:02}')
        )
        result = self.cursor.fetchone()
        return result[0] if result[0] is not None else 0
    
    def total_terminal_collection_current_month(self):
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        self.cursor.execute(
            "SELECT SUM(collection_term) FROM work_records WHERE strftime('%Y', start_time) = ? AND strftime('%m', start_time) = ?",
            (str(current_year), f'{current_month:02}')
        )
        result = self.cursor.fetchone()
        return result[0] if result[0] is not None else 0
    
    def count_work_records_current_month(self):
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        self.cursor.execute(
            "SELECT COUNT(*) FROM work_records WHERE strftime('%Y', start_time) = ? AND strftime('%m', start_time) = ?",
            (str(current_year), f'{current_month:02}')
        )
        result = self.cursor.fetchone()
        return result[0] if result[0] is not None else 0
    
    def count_work_hours_current_month(self):
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        self.cursor.execute(
            "SELECT total_time FROM work_records WHERE strftime('%Y', start_time) = ? AND strftime('%m', start_time) = ?",
            (str(current_year), f'{current_month:02}')
        )
        records = self.cursor.fetchall()
        
        total_minutes = 0
        for record in records:
            try:
                time_parts = record[0].split(':')
                hours = int(time_parts[0])
                minutes = int(time_parts[1])
                seconds = int(time_parts[2])
                total_minutes += hours * 60 + minutes + seconds / 60  # Преобразуем в минуты и суммируем
            except ValueError:
                continue  # Пропускаем записи, которые не могут быть преобразованы

        total_hours = int(total_minutes // 60)
        remaining_minutes = int(total_minutes % 60)
        
        return f"{total_hours} часов {remaining_minutes} минут"

    def best_user_hours_current_month(self):
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        self.cursor.execute(
            "SELECT username, total_time FROM work_records WHERE strftime('%Y', start_time) = ? AND strftime('%m', start_time) = ? ORDER BY total_time DESC LIMIT 1 ",
            (str(current_year), f'{current_month:02}')
        )
        return self.cursor.fetchone()
        
    def best_user_collection_current_month(self):
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        self.cursor.execute(    
            "SELECT username, start_time, total_time, collection FROM work_records WHERE strftime('%Y', start_time) = ? AND strftime('%m', start_time) = ?  ORDER BY collection DESC LIMIT 1",
            (str(current_year), f'{current_month:02}')
        )
        return self.cursor.fetchone()
        
    
    def best_user_by_collection_current_month(self):
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        self.cursor.execute(
            "SELECT username, SUM(collection) as collection FROM work_records "
            "WHERE strftime('%Y', start_time) = ? AND strftime('%m', start_time) = ? "
            "GROUP BY username ORDER BY collection DESC LIMIT 1",
            (str(current_year), f'{current_month:02}')
        )
        return self.cursor.fetchone()
    
    def all_users(self):
        users = self.cursor.execute("SELECT * FROM users")
        return users.fetchall()

    def add_work_record(self, username, start_time, end_time, total_time, collection, earnings, collection_term=0, earnings_term=0):
        self.cursor.execute("INSERT INTO work_records(username, start_time, end_time, total_time, collection, earnings, collection_term, earnings_term) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                            (username, start_time, end_time, total_time, collection, earnings, collection_term, earnings_term))
        self.connection.commit()

    def get_work_records(self, username):
        records = self.cursor.execute("SELECT * FROM work_records WHERE username = ?", (username,))
        return records.fetchall()
    
    def get_place(self, id):
        self.cursor.execute("SELECT * FROM place WHERE id = ?", (id,))
        return self.cursor.fetchone()
    
    def all_places(self):
        self.cursor.execute("SELECT * FROM place")
        return self.cursor.fetchall()
    
    def delete_place(self, id):
        self.cursor.execute("DELETE FROM place WHERE id = ?", (id,))
        self.connection.commit()

    def add_place(self, name, adress, url_map):
        self.cursor.execute("INSERT INTO place(name, adress, url_map) VALUES(?, ?, ?)", 
        (name, adress, url_map))
        self.connection.commit()
        
    def get_token(self, token):
        self.cursor.execute("SELECT * FROM tokens WHERE token = ?", (token,))
        return self.cursor.fetchone()
    
    def all_tokens(self):
        self.cursor.execute("SELECT * FROM tokens")
        return self.cursor.fetchall()
    
    def add_token(self):
        token = generate_secure_token()
        self.cursor.execute("INSERT INTO tokens(token) VALUES(?)", (token,))
        self.connection.commit()
    
    def delete_token(self, token):
        self.cursor.execute("DELETE FROM tokens WHERE token = ?", (token,))
        self.connection.commit()
    
    def __del__(self):
        self.cursor.close()
        self.connection.close()


def generate_secure_token(length=20):
    characters = string.ascii_letters + string.digits + string.punctuation
    token = ''.join(secrets.choice(characters) for _ in range(length))
    return token

