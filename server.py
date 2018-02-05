from flask import Flask
from flask import request, render_template, session

from json import dumps
import pymysql
import warnings
from datetime import datetime

# Ignore warnings for attempting to create the database when the database has already been created
warnings.filterwarnings('ignore', '.*1050.*')
warnings.filterwarnings('ignore', '.*1007.*')

# MySQL credentials
hostname = 'localhost'
username = 'LocalChat'
password = '0rZv5#VA'
database = 'localchat'
# port 33060

connection = pymysql.connect(host=hostname, user=username, passwd=password)

# Initialize globals
app = Flask(__name__)

# Used to encrypt session info
app.secret_key = '9@hGy1%UVBAf8!mUe0^QydC7'

# To send a POST in postman:
# https://stackoverflow.com/questions/39660074/post-image-data-using-postman

# Remember to create a text file with the api key sent in the post.
with open('api_key.txt', 'r') as keyfile:
    api_key = keyfile.readline().strip()

with connection.cursor() as cursor:
    # cursor.execute("DROP DATABASE " + database)
    cursor.execute("CREATE DATABASE IF NOT EXISTS " + database)
    cursor.execute("USE " + database)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
            user_id VARCHAR(36),
            username VARCHAR(255),
            email VARCHAR(255),
            join_date DATETIME,
            pass_hash VARCHAR(255),
            PRIMARY KEY (user_id)
        )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            chat_id VARCHAR(36),
            start_date DATETIME,
            title VARCHAR(255),
            location POINT,
            description VARCHAR(255),
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
            PRIMARY KEY (chat_id, user_id),
            FOREIGN KEY (chat_id) REFERENCES users(user_id),
            FOREIGN KEY (user_id) REFERENCES chats(chat_id)
        )''')

connection.commit()


# For debugging only
@app.route("/")
def index():
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()

        cursor.execute('SELECT * FROM chats')
        chats = cursor.fetchall()

        cursor.execute('SELECT * FROM messages')
        messages = cursor.fetchall()

        return render_template('table.html', users=users, chats=chats, messages=messages)


@app.route('/login', methods=['POST'])
def login():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return dumps({'status': False, 'description': 'invalid api key'})

    if 'user_id' in session:
        return dumps({'status': True, 'description': 'user already logged into server'})

    # Attempt to login
    with connection.cursor() as cursor:
        data = (request.values['username'], request.values['pass_hash'])
        user_id = cursor.execute("SELECT user_id FROM users WHERE username=%s, pass_hash=%s", data).fetchOne()

    if user_id is None:
        return dumps({'status': False, 'description': 'credentials do not match'})

    session['user_id'] = user_id
    return dumps({'status': True, 'description': 'logged into server'})


@app.route('/logout', methods=['POST'])
def logout():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return dumps({'status': False, 'description': 'invalid api key'})

    # Use credentials to log out
    with connection.cursor() as cursor:
        data = (request.values['username'], request.values['pass_hash'])
        user_id = cursor.execute("SELECT user_id FROM users WHERE username=%s, pass_hash=%s", data).fetchOne()

    if user_id is None:
        return dumps({'status': False, 'description': 'credentials do not match'})

    session.pop(request.values['user_id'], None)
    return dumps({'status': True, 'description': 'logged off server'})


@app.route('/new_user', methods=['POST'])
def new_user():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return dumps({'status': False, 'description': 'invalid api key'})

    data = (request.values['username'], request.values['email'], datetime.now(), request.values['pass_hash'])

    with connection.cursor() as cursor:

        cursor.execute("SELECT 1 FROM users WHERE email=%s", [request.values['email']])
        if cursor.fetchone() is not None:
            status = False
            description = 'user already exists'

        else:
            cursor.execute("INSERT INTO users VALUES (UUID(), %s, %s, %s, %s)", data)
            status = True
            description = 'user added to database'

            connection.commit()

    # Convert to json string and return
    return dumps({'status': status, 'description': description})


@app.route('/delete_user', methods=['POST'])
def delete_user():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return dumps({'status': False, 'description': 'invalid api key'})

    if 'user_id' not in session:
        return dumps({'status': False, 'description': 'user is not logged in'})

    data = (session['user_id'], request.values['pass_hash'])

    with connection.cursor() as cursor:

        cursor.execute("SELECT 1 FROM users WHERE username=%s AND pass_hash=%s", data)
        if cursor.fetchone() is None:
            status = False
            description = 'user does not exist'

        else:
            cursor.execute("DELETE FROM users WHERE username=%s AND pass_hash=%s", data)
            status = True
            description = 'user removed from database'

            connection.commit()

    # Convert to json string and return
    return dumps({'status': status, 'description': description})


@app.route('/new_chat', methods=['POST'])
def new_chat():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return dumps({'status': False, 'description': 'invalid api key'})

    if 'user_id' not in session:
        return dumps({'status': False, 'description': 'user is not logged in'})

    with connection.cursor() as cursor:
        uuid = cursor.execute("SELECT UUID()").fetchOne()
        data = (uuid,
                datetime.now(),
                request.values['title'],
                request.values['location'],
                request.values['description'])

        cursor.execute("INSERT INTO chats VALUES (%s, %s, %s, %s, %s)", data)
        cursor.execute("INSERT INTO chat_members VALUES (%s, %s)", (uuid, session['user_id']))

        connection.commit()

    return dumps({'status': True, 'description': 'chat added to database'})


@app.route('/join_chat', methods=['POST'])
def join_chat():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return dumps({'status': False, 'description': 'invalid api key'})

    if 'user_id' not in session:
        return dumps({'status': False, 'description': 'user is not logged in'})

    with connection.cursor() as cursor:
        data = (request.values['chat_id'], session['user_id'])

        cursor.execute("SELECT 1 from chat_members WHERE (chat_id, user_id)=(%s, %s)", data)
        if cursor.fetchOne() is not None:
            return dumps({'status': False, 'description': 'user already in group'})

        cursor.execute("INSERT INTO chat_members VALUES (%s, %s)", data)
        connection.commit()

    return dumps({'status': True, 'description': 'user added to chat'})


@app.route('/new_message', methods=['POST'])
def new_message():

    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return dumps({'status': False, 'description': 'invalid api key'})

    if 'user_id' not in session:
        return dumps({'status': False, 'description': 'user is not logged in'})

    data = (session['user_id'], request.values['chat_id'], datetime.now(), request.values['value'])

    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO messages VALUES (UUID(), %s, %s, %s, %s)", data)
        connection.commit()

    return dumps({'status': True, 'description': 'message added to database'})


if __name__ == '__main__':
    app.run(port=8888)
