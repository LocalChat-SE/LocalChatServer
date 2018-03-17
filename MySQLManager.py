from DBManager import DBManager
import pymysql

import warnings
import json
from datetime import datetime

# Ignore warnings for attempting to create the database when the database has already been created
warnings.filterwarnings('ignore', '.*1050.*')
warnings.filterwarnings('ignore', '.*1007.*')

config = json.load(open('./config.json', 'r'))


class MySQLManager(DBManager):
    def __init__(self):
        print(config)

        self.connection = pymysql.connect(
            host=config['hostname'],
            user=config['username'],
            passwd=config['password'])

        self.initialize_database()

    def initialize_database(self):
        with self.connection.cursor() as cursor:

            # cursor.execute("DROP DATABASE " + database)
            cursor.execute("CREATE DATABASE IF NOT EXISTS " + config['database'])
            cursor.execute("USE " + config['database'])

            cursor.execute('''
                        CREATE TABLE IF NOT EXISTS users(
                            user_id VARCHAR(36),
                            username VARCHAR(255),
                            join_date DATETIME,
                            pass_hash VARCHAR(255),
                            PRIMARY KEY (user_id)
                        )''')

            cursor.execute('''
                        CREATE TABLE IF NOT EXISTS chats (
                            chat_id VARCHAR(36),
                            start_date DATETIME,
                            title VARCHAR(255),
                            location POINT NOT NULL,
                            description VARCHAR(255),
                            SPATIAL INDEX (location),
                            PRIMARY KEY (chat_id)
                        )''')

            cursor.execute('''
                        CREATE TABLE IF NOT EXISTS messages (
                            message_id VARCHAR(36),
                            user_id VARCHAR(255),
                            chat_id VARCHAR(255),
                            send_date DATETIME,
                            value VARCHAR(255),
                            PRIMARY KEY (message_id),
                            FOREIGN KEY (user_id) REFERENCES users(user_id),
                            FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
                        )''')

            cursor.execute('''
                        CREATE TABLE IF NOT EXISTS chat_members (
                            chat_id VARCHAR(36),
                            user_id VARCHAR(36),
                            moderator BIT,
                            PRIMARY KEY (chat_id, user_id),
                            FOREIGN KEY (chat_id) REFERENCES chats(chat_id),
                            FOREIGN KEY (user_id) REFERENCES users(user_id)
                        )''')

            self.connection.commit()

    # for debugging
    def get_all(self):
        with self.connection.cursor() as cursor:
            cursor.execute('SELECT * FROM users')
            users = cursor.fetchall()

            cursor.execute('SELECT * FROM chats')
            chats = cursor.fetchall()

            cursor.execute('SELECT * FROM messages')
            messages = cursor.fetchall()

            cursor.execute('SELECT * FROM chat_members')
            enrolls = cursor.fetchall()

            return users, chats, messages, enrolls

    def reset_all(self):
        with self.connection.cursor() as cursor:
            cursor.execute('DROP DATABASE ' + config['database'])
            self.connection.commit()


    # for login
    def get_user(self, user, password):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE username=%s AND pass_hash=%s", (user, password))
            if cursor.fetchone():
                return True, 'credentials match'
            return False, 'credentials do not match'

    # for new user
    def set_user(self, user, password):
        with self.connection.cursor() as cursor:

            cursor.execute("SELECT 1 FROM users WHERE user_id=%s", [user])
            if cursor.fetchone() is not None:
                return False, 'user already exists'

            else:
                data = (user, datetime.now(), password)
                cursor.execute("INSERT INTO users VALUES (UUID(), %s, %s, %s)", data)
                self.connection.commit()
                return True, 'user added to database'

    def delete_user(self, user, password):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM users WHERE username=%s AND pass_hash=%s", (user, password))
            if cursor.fetchone() is None:
                return False, 'user does not exist'

            else:
                cursor.execute("DELETE FROM users WHERE username=%s AND pass_hash=%s", (user, password))
                self.connection.commit()
                return True, 'user removed from database'

    def get_chats(self, location):

        with self.connection.cursor() as cursor:
            cursor.execute("""SELECT chat_id, title, 
                ST_X(location) AS "latitude",
                ST_Y(location) AS "longitude",
                (ST_Length(ST_GeometryFromWKB(ST_asWKB(LineString(location, ST_GeomFromText(%s)))))) AS distance
                FROM chats 
                ORDER BY distance ASC;""", [location])

            return True, 'chats fetched', cursor.fetchall()

    # returns chat info, enrolls, last n messages
    def get_chat(self, chatID, history=50):
        raise NotImplementedError

    # for new/edit chat
    def set_chat(self, chatID=None, name=None, location=None, description=None):
        with self.connection.cursor() as cursor:
            # new chat
            if not chatID:
                cursor.execute("SELECT UUID()")
                uuid = cursor.fetchone()[0]

                data = (uuid, datetime.now(), name, location, description)

                cursor.execute("INSERT INTO chats VALUES (%s, %s, %s, ST_GeomFromText(%s), %s)", data)

                self.connection.commit()
                return True, 'new chat added', uuid
            else:
                # TODO: implement edit chat
                pass

    def new_message(self, username, chatID, message):

        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO messages VALUES (UUID(), %s, %s, %s, %s)",
                           (username, chatID, datetime.now(), message))
            self.connection.commit()

            return True, 'message added to database'

    def set_enrollment(self, userID, chatID, isModerator=None, isBanned=None):
        with self.connection.cursor() as cursor:
            data = (userID, chatID)

            cursor.execute("SELECT 1 from chat_members WHERE (chat_id, user_id)=(%s, %s)", data)
            if cursor.fetchOne() is not None:
                return False, 'user already in chat room'

            cursor.execute("INSERT INTO chat_members VALUES (%s, %s)", data)
            self.connection.commit()

            return True, 'user added to chat'
