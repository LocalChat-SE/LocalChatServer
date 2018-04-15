from DBManager import DBManager
import pymysql

import warnings
import json
from datetime import datetime

# Ignore warnings for attempting to create the database when the database has already been created
warnings.filterwarnings('ignore', '.*1050.*')
warnings.filterwarnings('ignore', '.*1007.*')

config = json.load(open('./config.json', 'r'))
del config['type']
del config['port']


class MySQLManager(DBManager):

    def __init__(self):
        MySQLManager.initialize_database()

    @staticmethod
    def initialize_database():
        config_copy = dict(config)
        del config_copy['db']
        with pymysql.connect(**config_copy) as cursor:

            # cursor.execute("DROP DATABASE " + database)
            cursor.execute("CREATE DATABASE IF NOT EXISTS " + config['db'])
            cursor.execute("USE " + config['db'])

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
                            name VARCHAR(255),
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

    # for debugging
    def get_all(self):
        with pymysql.connect(**config) as cursor:
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
        with pymysql.connect(**config) as cursor:
            cursor.execute('DROP DATABASE ' + config['db'])
        self.initialize_database()

    # for login
    def get_user(self, username, password):
        with pymysql.connect(**config) as cursor:
            cursor.execute("SELECT username FROM users WHERE username=%s AND password=%s", (username, password))
            if cursor.fetchone():
                return True, 'logged in'
            return False, 'credentials do not match'

    # for new user
    def set_user(self, username, password):
        with pymysql.connect(**config) as cursor:

            cursor.execute("SELECT 1 FROM users WHERE username=%s", [username])
            if cursor.fetchone() is not None:
                return False, 'user already exists'

            else:
                data = (username, password, datetime.now())
                cursor.execute("INSERT INTO users VALUES (%s, %s, %s)", data)
                return True, 'user added to database'

    def delete_user(self, username, password):
        with pymysql.connect(**config) as cursor:
            print(username)
            cursor.execute("SELECT 1 FROM users WHERE (username, password) = (%s, %s)", (username, password))
            if cursor.fetchone() is None:
                return False, 'credentials do not match'

            else:
                cursor.execute("DELETE FROM enrollments WHERE username=%s", [username])
                cursor.execute("DELETE FROM users WHERE username=%s", [username])
                return True, 'user removed from database'

    def get_nearby_chats(self, location):

        with pymysql.connect(**config) as cursor:
            cursor.execute("""SELECT chat_id, name, description, 
                ST_X(location) AS "latitude",
                ST_Y(location) AS "longitude",
                (ST_Length(ST_GeometryFromWKB(ST_asWKB(LineString(location, ST_GeomFromText(%s)))))) AS distance
                FROM chats 
                ORDER BY distance ASC;""", [location])

            labels = ['chat_id', 'name', 'description', 'latitude', 'longitude', 'distance']
            chats = [{labels[idx]: field for idx, field in enumerate(record)}
                     for record in cursor.fetchall()]

            return True, 'chats fetched', chats

    def get_user_chats(self, username):
        with pymysql.connect(**config) as cursor:
            cursor.execute("""SELECT chat_id, name, description, 
                ST_X(location) AS "latitude",
                ST_Y(location) AS "longitude"
                FROM chats
                WHERE chat_id IN (
                    SELECT chat_id 
                    FROM enrollments
                    WHERE username=%s)
                """, [username])

            labels = ['chat_id', 'name', 'description', 'latitude', 'longitude']
            chats = [{labels[idx]: field for idx, field in enumerate(record)}
                     for record in cursor.fetchall()]
            return True, 'chats fetched', chats

    # returns chat info, enrolls, last n messages
    def get_chat(self, chat_id, username, time=None, limit=50, offset=0):
        with pymysql.connect(**config) as cursor:

            # user must be a non-banned member
            cursor.execute("SELECT banned FROM enrollments WHERE (chat_id, username)=(%s, %s)", (chat_id, username))
            record = cursor.fetchone()
            if record is None:
                return False, 'user is not a member of the chatroom', {}

            if record[0][0]:
                return False, 'user is banned', {}

            # CHAT
            cursor.execute("""SELECT name, description, start_date,
                ST_X(location) AS "latitude", 
                ST_Y(location) AS "longitude" 
                FROM chats WHERE chat_id=%s""", [chat_id])

            record = cursor.fetchone()
            chat = {
                'name': record[0],
                'description': record[1],
                'start_date': str(record[2].now()),
                'latitude': record[3],
                'longitude': record[4]
            }

            # USERS (not necessary)
            # cursor.execute('SELECT username, moderator, banned FROM enrollments WHERE chat_id=%s', [chat_id])
            #
            # users = {user: {'moderator': bool(ord(mod)), 'banned': bool(ord(ban))}
            #          for user, mod, ban in cursor.fetchall()}

            # MESSAGES
            if time is None:
                cursor.execute("""
                    SELECT message_id, username, send_date, value
                    FROM messages
                    WHERE chat_id=%s
                    ORDER BY send_date""", (chat_id,))
            else:
                cursor.execute("""
                    SELECT message_id, username, send_date, value
                    FROM messages
                    WHERE chat_id=%s AND send_date>=%s
                    ORDER BY send_date""", (chat_id, time))

            messages = [{'id': mesg_id, 'username': user, 'time': str(time.now()), 'value': mesg}
                        for mesg_id, user, time, mesg in cursor.fetchall()]

            # ENROLLMENTS
            cursor.execute("""
                SELECT username, moderator, banned
                FROM enrollments
                WHERE chat_id=%s""", (chat_id,))

            enrollments = [{
                'username': record[0],
                'moderator': bool(ord(record[1])),
                'banned': bool(ord(record[2]))
            } for record in cursor.fetchall()]

            return True, 'chat collected', {
                **chat,
                'messages': messages,
                'enrollments': enrollments
            }

    # for new chat
    def set_chat(self, name, location, description):
        with pymysql.connect(**config) as cursor:
            cursor.execute("SELECT UUID()")
            uuid = cursor.fetchone()[0]

            data = (uuid, datetime.now(), name, location, description)

            cursor.execute("INSERT INTO chats VALUES (%s, %s, %s, ST_GeomFromText(%s), %s)", data)

            return True, 'new chat added', {
                'chat_id': uuid,
                'name': name,
                'description': description
            }

    # for edit chat
    def update_chat(self, chat_id, username, name=None, location=None, description=None):
        with pymysql.connect(**config) as cursor:
            # check if user is a moderator
            cursor.execute(
                "SELECT 1 FROM enrollments WHERE (chat_id, username, moderator)=(%s, %s, 1)", (chat_id, username))
            if cursor.fetchone() is None:
                return False, 'user has insufficient rights to edit the chat'

            if name:
                cursor.execute("UPDATE chats SET name=%s WHERE chat_id=%s", (name, chat_id))

            if location:
                cursor.execute("UPDATE chats SET location=%s WHERE chat_id=%s", (location, chat_id))

            if description:
                cursor.execute("UPDATE chats SET description=%s WHERE chat_id=%s", (description, chat_id))

            return True, 'chat information has been updated'

    def delete_chat(self, chat_id, username):
        with pymysql.connect(**config) as cursor:
            # check if user is a moderator
            cursor.execute(
                "SELECT 1 FROM enrollments WHERE (chat_id, username, moderator)=(%s, %s, 1)", (chat_id, username))
            if cursor.fetchone() is None:
                return False, 'user has insufficient rights to edit the chat'

            cursor.execute("DELETE FROM enrollments WHERE chat_id=%s", (chat_id,))
            cursor.execute("DELETE FROM messages WHERE chat_id=%s", (chat_id,))
            cursor.execute("DELETE FROM chats WHERE chat_id=%s", (chat_id,))

            return True, 'chat information has been updated'

    def new_message(self, chat_id, username, message):

        with pymysql.connect(**config) as cursor:

            cursor.execute("SELECT banned FROM enrollments WHERE (chat_id, username)=(%s, %s)", (chat_id, username))
            record = cursor.fetchone()
            if record is None:
                return False, 'user is not a member of the chatroom'

            if record[0][0]:
                return False, 'user is banned'

            cursor.execute("INSERT INTO messages VALUES (UUID(), %s, %s, %s, %s)",
                           (chat_id, username, datetime.now(), message))

            return True, 'message added to database'

    def set_enrollment(self, chat_id, username, modded=False):
        with pymysql.connect(**config) as cursor:

            cursor.execute("SELECT 1 FROM enrollments WHERE (chat_id, username)=(%s, %s)", (chat_id, username))

            if cursor.fetchone() is not None:
                return False, 'user is already enrolled'

            cursor.execute("SELECT 1 FROM enrollments WHERE chat_id=%s", (chat_id,))
            if len(cursor.fetchall()) >= 50:
                return False, 'chat room is already full'

            cursor.execute("INSERT INTO enrollments VALUES (%s, %s, %s, 0)", (chat_id, username, modded))

            return True, 'user added to chat'

    def set_moderator(self, chat_id, moderator, username):
        with pymysql.connect(**config) as cursor:

            # check if moderator is a moderator
            cursor.execute(
                "SELECT moderator FROM enrollments WHERE (chat_id, username, moderator)=(%s, %s, 1)",
                (chat_id, moderator))

            if cursor.fetchone() is None:
                return False, 'user has insufficient rights to set a moderator'

            cursor.execute(
                "UPDATE enrollments SET moderator=1, banned=0 WHERE (chat_id, username)=(%s, %s)", (chat_id, username))

            return True, 'user has been modded'

    def set_banned(self, chat_id, moderator, username, status):
        with pymysql.connect(**config) as cursor:

            # check if moderator is a moderator
            cursor.execute(
                "SELECT 1 FROM enrollments WHERE (chat_id, username, moderator)=(%s, %s, 1)", (chat_id, moderator))
            if cursor.fetchone() is None:
                return False, 'user has insufficient rights to ban'

            # check if user is a moderator
            cursor.execute(
                "SELECT 1 FROM enrollments WHERE (chat_id, username, moderator)=(%s, %s, 1)", (chat_id, username))
            if cursor.fetchone() is not None:
                return False, 'a moderator may not be banned'

            cursor.execute(
                "UPDATE enrollments SET banned=%s WHERE (chat_id, username)=(%s, %s)",
                (int(status.lower() == 'true'), chat_id, username))

            return True, 'user ban has been set/unset'
