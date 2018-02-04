from flask import Flask
from flask import request

from json import dumps
import pymysql

hostname = 'localhost'
username = 'LocalChat'
password = '0rZv5#VA'
database = 'localchat'
# port 33060

connection = pymysql.connect(host=hostname, user=username, passwd=password)

with connection.cursor() as cursor:
    # cursor.execute("DROP DATABASE " + database)
    cursor.execute("CREATE DATABASE IF NOT EXISTS " + database)
    cursor.execute("use " + database)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
            user_id VARCHAR(255),
            username VARCHAR(255),
            email VARCHAR(255),
            join_date DATETIME,
            pass_hash VARCHAR(255),
            PRIMARY KEY (user_id)
        )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            chat_id VARCHAR(255),
            start_date DATETIME,
            title VARCHAR(255),
            location POINT,
            description VARCHAR(255),
            PRIMARY KEY (chat_id)
        )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            message_id VARCHAR(255),
            user_id VARCHAR(255),
            chat_id VARCHAR(255),
            send_date DATETIME,
            value VARCHAR(255),
            PRIMARY KEY (message_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
        )''')

connection.commit()


cursor = connection.cursor()

# Initialize globals
app = Flask(__name__)

# To send a POST in postman:
# https://stackoverflow.com/questions/39660074/post-image-data-using-postman

# Remember to create a text file with the api key sent in the post.
with open('api_key.txt', 'r') as keyfile:
    api_key = keyfile.readline().strip()


# username
# hash
@app.route('/login/', methods=['POST'])
def chat():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return str({'error': 'invalid api key'})

    with connection.cursor() as cursor:
        data = (request.values['username'], request.values['hash'])
        cursor.execute("SELECT * FROM users WHERE username=%s, hash=%s", data)
        status = cursor.fetchone() is not None

    # Convert to json string and return
    return dumps({'success': status, 'passed_value': request.values['value']})


if __name__ == '__main__':
    app.run(port=8888)
