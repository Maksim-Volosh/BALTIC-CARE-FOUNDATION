import sqlite3
import bcrypt

class Database():
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_db()

    def create_db(self):
        try:
            query =  ("CREATE TABLE IF NOT EXISTS users("
                    "id INTEGER PRIMARY KEY, "
                    "user_fullname TEXT, "
                    "user_phonenumber TEXT, "
                    "user_date TEXT, "
                    "user_tgid TEXT);")
            self.cursor.execute(query)
            self.connection.commit()
        except sqlite3.Error as Error:
            print("Error while creating a sqlite table", Error)
    
    def add_user(self, user_fullname, user_phonenumber, user_date, user_tgid):
        self.cursor.execute("INSERT INTO users(user_fullname, user_phonenumber, user_date, user_tgid) VALUES(?, ?, ?, ?)", (user_fullname, user_phonenumber, user_date, user_tgid))
        self.connection.commit()
    
    def get_user(self, user_tgid):
        users = self.cursor.execute("SELECT * FROM users WHERE user_tgid = ?", (user_tgid,))
        return users.fetchone()
    
    def __del__(self):
        self.cursor.close()
        self.connection.close()
            

        