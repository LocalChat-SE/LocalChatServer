from flask import Flask
from flask import request, render_template, session

import json
from MySQLManager import MySQLManager

# Initialize globals
app = Flask(__name__)

# Used to encrypt session info
app.secret_key = '9@hGy1%UVBAf8!mUe0^QydC7'

config = json.load('./config.json')
if config['type'] == 'MySQL':
    database = MySQLManager()
else:
    raise ValueError('Unknown database type')

# To send a POST in postman:
# https://stackoverflow.com/questions/39660074/post-image-data-using-postman

# Remember to create a text file with the api key sent in the post.
with open('api_key.txt', 'r') as keyfile:
    api_key = keyfile.readline().strip()


# For debugging only
@app.route("/")
def index():
    users, chats, messages, chat_members = database.getAll()
    return render_template('table.html', users=users, chats=chats, messages=messages, chat_members=chat_members)


@app.route('/login', methods=['POST'])
def login():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' in session:
        return json.dumps({'status': True, 'description': 'user already logged into server'})

    status, description = database.get_user(request.values['username'], request.values['pass_hash'])

    if status:
        session['username'] = request.values['username']

    return json.dumps({'status': status, 'description': description})


@app.route('/logout', methods=['POST'])
def logout():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': True, 'description': 'already logged out'})

    session.pop('username', None)
    return json.dumps({'status': True, 'description': 'logged off server'})


@app.route('/new_user', methods=['POST'])
def new_user():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    status, description = database.set_user(request.values['username'], request.values['pass_hash'])

    # Convert to json string and return
    return json.dumps({'status': status, 'description': description})


@app.route('/delete_user', methods=['POST'])
def delete_user():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    status, description = database.delete_user(session['username'], request.values['pass_hash'])

    # Convert to json string and return
    return json.dumps({'status': status, 'description': description})


@app.route('/new_chat', methods=['POST'])
def new_chat():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    data = {
        'chatID': None,
        'name': request.values['title'],
        'location': request.values['location'],
        'description': request.values['description']
    }

    status, description, chat_id = database.set_chat(**data)

    return json.dumps({
        'status': status,
        'description': description,
        'data': {'chat_id': chat_id}
    })


@app.route('/join_chat', methods=['POST'])
def join_chat():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    status, description = database.set_enrollment(session['username'], session['chat_id'])

    return json.dumps({'status': status, 'description': description})


@app.route('/get_nearby_chats', methods=['POST'])
def get_nearby_chats():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    status, description, chats = database.get_chats(request.values['location'])

    return json.dumps({
        'status': status,
        'description': description,
        'data': chats
    })


@app.route('/new_message', methods=['POST'])
def new_message():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    data = (session['username'], request.values['chat_id'], request.values['value'])
    status, description = database.new_message(*data)

    return json.dumps({'status': status, 'description': description})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
