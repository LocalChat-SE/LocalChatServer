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
    cursor.execute("use " + database)

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

connection.commit()


# For debugging only
@app.route("/")
def index():
    with connection.cursor() as cursor:
        table_name = 'users'
        cursor.execute('SELECT * FROM ' + table_name)
        return render_template('table.html', title=table_name, items=cursor.fetchall())


@app.route('/login', methods=['POST'])
def login():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return str({'status': False, 'description': 'invalid api key'})

    # Attempt to login
    with connection.cursor() as cursor:
        data = (request.values['username'], request.values['pass_hash'])
        cursor.execute("SELECT * FROM users WHERE username=%s, pass_hash=%s", data)

        if cursor.fetchone() is not None:
            session['username'] = request.values['username']
            return dumps({'status': True, 'description': 'logged into server'})

        else:
            return dumps({'status': False, 'description': 'credentials do not match'})


@app.route('/logout', methods=['POST'])
def logout():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return str({'status': False, 'description': 'invalid api key'})

    with connection.cursor() as cursor:
        data = (request.values['username'], request.values['pass_hash'])
        cursor.execute("SELECT * FROM users WHERE username=%s, pass_hash=%s", data)

        if cursor.fetchone() is not None:
            session.pop(request.values['username'], None)
            return dumps({'status': True, 'description': 'logged off server'})

        else:
            return dumps({'status': False, 'description': 'credentials do not match'})


@app.route('/new_user', methods=['POST'])
def new_user():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return str({'status': False, 'description': 'invalid api key'})

    with connection.cursor() as cursor:

        cursor.execute("SELECT 1 FROM users WHERE email=%s", [request.values['email']])
        if cursor.fetchone() is not None:
            status = False
            description = 'user already exists'

        else:
            data = (request.values['username'], request.values['email'], datetime.now(), request.values['pass_hash'])
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
        return str({'status': False, 'description': 'invalid api key'})

    with connection.cursor() as cursor:

        data = (request.values['username'], request.values['pass_hash'])

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
        return str({'status': False, 'description': 'invalid api key'})

    with connection.cursor() as cursor:

        data = (request.values['username'], request.values['pass_hash'])

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


if __name__ == '__main__':
    app.run(port=8888)
