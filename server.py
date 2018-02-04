from flask import Flask
from flask import request

from json import dumps

import sqlite3

connection = sqlite3.connect('./LocalChat.db')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users(
        user_id TEXT PRIMARY KEY,
        username TEXT,
        email TEXT,
        join_date DATETIME,
        pass_hash TEXT
    )''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS chats (
        chat_id TEXT PRIMARY KEY,
        start_date DATETIME,
        title TEXT,
        latitude TEXT,
        longitude TEXT,
        description TEXT
    )''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        message_id TEXT PRIMARY KEY,
        user_id TEXT,
        chat_id TEXT,
        send_date DATETIME,
        value TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id),
        FOREIGN KEY(chat_id) REFERENCES chats(chat_id)
    )''')

# Initialize globals
app = Flask(__name__)

# To send a POST in postman:
# https://stackoverflow.com/questions/39660074/post-image-data-using-postman

# Remember to create a text file with the api key sent in the post.
with open('api_key.txt', 'r') as keyfile:
    api_key = keyfile.readline().strip()


@app.route('/chat/', methods=['POST'])
def chat():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return str({'error': 'invalid api key'})

    status = True

    # Convert to json string and return
    return dumps({'success': status, 'passed_value': request.values['value']})


if __name__ == '__main__':
    app.run(port=8888)
