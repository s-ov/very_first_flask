import math
import time
import sqlite3
from flask import url_for
import re


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cursor = db.cursor()

    def get_menu(self):
        sql = """SELECT * FROM mainmenu"""
        try:
            self.__cursor.execute(sql)
            result = self.__cursor.fetchall()
            if result:
                return result
        except:
            print("Error while reading from database.")
        return []

    def add_post(self, title, text, url):
        try:
            query = f"SELECT COUNT() as 'count' FROM posts WHERE url LIKE '{url}'"
            self.__cursor.execute(query)
            result = self.__cursor.fetchone()
            if result['count'] > 0:
                print("There is an article with such an url.")
                return False
            base = url_for('static', filename='images')
            text = re.sub(r"(?P<tag><img\s+[^>]*src)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",
                          "\\g<tag>" + base + "/\\g<url>",
                          text)
            tm = math.floor(time.time())
            query_2 = "INSERT INTO posts VALUES(NULL, ?, ?, ?, ?)", (title, text, url, tm)
            self.__cursor.execute(query_2)
            self.__db.commit()
        except sqlite3.Error as e:
            print(f"Article adding into db failed: {e}")
            return False
        return True

    def get_post(self, alias):
        try:
            query = f"SELECT title, text FROM posts WHERE url LIKE '{alias}' LIMIT 1"
            self.__cursor.execute(query)
            result = self.__cursor.fetchone()
            if result:
                return result
        except sqlite3.Error as e:
            print(f"Error while getting article from bd: {e}")
        return False, False

    def get_posts_announce(self):
        try:
            query = f"SELECT id, title, text, url FROM posts ORDER BY time DESC"
            self.__cursor.execute(query)
            result = self.__cursor.fetchall()
            if result:
                return result
        except sqlite3.Error as e:
            print(f"Error while getting article from bd: {e}")
        return []

    def add_user(self, name, email, hash_psw):
        try:
            query = f"SELECT COUNT() as 'count' FROM users WHERE email LIKE '{email}'"
            self.__cursor.execute(query)
            result = self.__cursor.fetchone()
            if result['count'] > 0:
                print('There is an user with a such email.')
                return False
            tm = math.floor(time.time())
            query_2 = "INSERT INTO users VALUES(NULL, ?, ?, ?, NULL, ?)", (name, email, hash_psw, tm)
            self.__cursor.execute(query_2)
            self.__db.commit()
        except sqlite3.Error as e:
            print(f"Error while adding an user into db: {e}.")
            return False
        return True

    def get_user(self, user_id):
        try:
            query = f"SELECT * FROM users WHERE id = {user_id} LIMIT 1"
            self.__cursor.execute(query)
            result = self.__cursor.fetchone()
            if not result:
                print("No such user.")
                return False
            return result
        except sqlite3.Error as e:
            print(f"Data error while getting from db: {e}.")
        return False

    def get_user_by_email(self, email):
        try:
            query = f"SELECT * FROM users WHERE email = '{email}' LIMIT 1"
            self.__cursor.execute(query)
            result = self.__cursor.fetchone()
            if not result:
                print("No such user.")
                return False
            return result
        except sqlite3.Error as e:
            print(f"Data error while getting from db: {e}.")
        return False

    def update_user_avatar(self, avatar, user_id):
        if not avatar:
            return False
        try:
            binary = sqlite3.Binary(avatar)
            query = "UPDATE users SET avatar = ? WHERE id = ?", (binary, user_id)
            self.__cursor.execute(query)
            self.__db.commit()
        except sqlite3.Error as e:
            print(f"Avatar update error in db: {e}")
            return False
        return True
