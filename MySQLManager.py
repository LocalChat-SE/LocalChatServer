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
                        CREATE TABLE IF NOT EXISTS users (
                            username VARCHAR(255),
                            password VARCHAR(255),
                            join_date DATETIME,
                            PRIMARY KEY (username)
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
                            chat_id VARCHAR(255),
                            username VARCHAR(255),
                            send_date DATETIME,
                            value VARCHAR(255),
                            PRIMARY KEY (message_id),
                            FOREIGN KEY (username) REFERENCES users(username),
                            FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
                        )''')

            cursor.execute('''
                        CREATE TABLE IF NOT EXISTS enrollments (
                            chat_id VARCHAR(36),
                            username VARCHAR(255),
                            moderator BIT,
                            banned BIT,
                            PRIMARY KEY (chat_id, username),
                            FOREIGN KEY (chat_id) REFERENCES chats(chat_id),
                            FOREIGN KEY (username) REFERENCES users(username)
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

            cursor.execute('SELECT * FROM enrollments')
            enrolls = cursor.fetchall()

            return users, chats, messages, enrolls

    def reset_all(self):
        with self.connection.cursor() as cursor:
            cursor.execute('DROP DATABASE ' + config['database'])
            self.connection.commit()
        self.initialize_database()


    # for login
    def get_user(self, username, password):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT username FROM users WHERE username=%s AND password=%s", (username, password))
            if cursor.fetchone():
                return True, 'logged in'
            return False, 'credentials do not match'

    # for new user
    def set_user(self, username, password):
        with self.connection.cursor() as cursor:

            cursor.execute("SELECT 1 FROM users WHERE username=%s", [username])
            if cursor.fetchone() is not None:
                return False, 'user already exists'

            else:
                data = (username, password, datetime.now())
                cursor.execute("INSERT INTO users VALUES (%s, %s, %s)", data)
                self.connection.commit()
                return True, 'user added to database'

    def delete_user(self, username, password):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM users WHERE username=%s AND password=%s", (username, password))
            if cursor.fetchone() is None:
                return False, 'user does not exist'

            else:
                cursor.execute("DELETE FROM users WHERE username=%s AND password=%s", (username, password))
                self.connection.commit()
                return True, 'user removed from database'

    def get_nearby_chats(self, location):

        with self.connection.cursor() as cursor:
            cursor.execute("""SELECT chat_id, title, description, 
                ST_X(location) AS "latitude",
                ST_Y(location) AS "longitude",
                (ST_Length(ST_GeometryFromWKB(ST_asWKB(LineString(location, ST_GeomFromText(%s)))))) AS distance
                FROM chats 
                ORDER BY distance ASC;""", [location])

            return True, 'chats fetched', cursor.fetchall()

    def get_user_chats(self, username):
        with self.connection.cursor() as cursor:
            cursor.execute("""SELECT chat_id, title, description, 
                ST_X(location) AS "latitude",
                ST_Y(location) AS "longitude"
                FROM chats
                WHERE chat_id IN (
                    SELECT chat_id 
                    FROM enrollments
                    WHERE username=%s)
                """, [username])
            return True, 'chats fetched', cursor.fetchall()

    # returns chat info, enrolls, last n messages
    def get_chat(self, chatID, history=50):
        raise NotImplementedError

    # for new/edit chat
    def set_chat(self, chatID=None, username=None, location=None, description=None):
        with self.connection.cursor() as cursor:
            # new chat
            if not chatID:
                cursor.execute("SELECT UUID()")
                uuid = cursor.fetchone()[0]

                data = (uuid, datetime.now(), username, location, description)

                cursor.execute("INSERT INTO chats VALUES (%s, %s, %s, ST_GeomFromText(%s), %s)", data)

                self.connection.commit()
                return True, 'new chat added', uuid
            else:
                # TODO: implement edit chat
                pass

    def new_message(self, chatID, username, message):

        with self.connection.cursor() as cursor:

            cursor.execute("SELECT banned FROM enrollments WHERE (chat_id, username)=(%s, %s)", (chatID, username))
            record = cursor.fetchone()
            if record is None:
                return False, 'user is not a member of the chatroom'

            if record[0][0]:
                return False, 'user is banned'

            cursor.execute("INSERT INTO messages VALUES (UUID(), %s, %s, %s, %s)",
                           (chatID, username, datetime.now(), message))
            self.connection.commit()

            return True, 'message added to database'

    def set_enrollment(self, chatID, username, moderator=None, banned=None):

        if moderator is True and banned is True:
            return False, 'a user may not be a banned moderator'

        with self.connection.cursor() as cursor:

            cursor.execute("SELECT chat_id, username, moderator, banned FROM enrollments WHERE (chat_id, username)=(%s, %s)", (chatID, username))
            record = cursor.fetchOne()
            if record is not None:
                _, _, currently_moderator, currently_banned = record[0]

                if currently_moderator is True and moderator is False:
                    return False, 'a moderator may not be demoted'

                if currently_banned is True and moderator is True:
                    return False, 'a banned user may not be a moderator'

                if moderator is not None:
                    cursor.execute("UPDATE enrollments SET moderator=%s WHERE (username, chat_id)=(%s, %s)",
                                   (moderator, username, chatID))

                if banned is not None:
                    cursor.execute("UPDATE enrollments SET banned=%s WHERE (username, chat_id)=(%s, %s)",
                                   (banned, username, chatID))

                self.connection.commit()
                return True, 'user enrollment updated'

            if moderator is None:
                moderator = False

            if banned is None:
                banned = False

            cursor.execute("INSERT INTO enrollments VALUES (%s, %s, %s, %s)", (chatID, username, moderator, banned))
            self.connection.commit()

            return True, 'user added to chat'
