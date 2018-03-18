from flask import Flask
from flask import request, render_template, session

import json
from MySQLManager import MySQLManager

# Initialize globals
app = Flask(__name__)

# Used to encrypt session info
app.secret_key = '9@hGy1%UVBAf8!mUe0^QydC7'

config = json.load(open('./config.json', 'r'))
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
    users, chats, messages, chat_members = database.get_all()
    return render_template('table.html', users=users, chats=chats, messages=messages, chat_members=chat_members)


@app.route('/reset_all', methods=['POST'])
def reset_all():
    database.reset_all()
    session.pop('username', None)
    return json.dumps({'status': True, 'description': 'database reset'})


@app.route('/login', methods=['POST'])
def login():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' in session:
        return json.dumps({'status': True, 'description': 'user already logged into server'})

    status, description = database.get_user(request.values['username'], request.values['password'])

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

    status, description = database.set_user(request.values['username'], request.values['password'])

    # Convert to json string and return
    return json.dumps({'status': status, 'description': description})


@app.route('/delete_user', methods=['POST'])
def delete_user():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    status, description = database.delete_user(session['username'], request.values['password'])

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
        'username': request.values['title'],
        'location': request.values['location'],
        'description': request.values['description']
    }

    status, description, chat_id = database.set_chat(**data)

    return json.dumps({
        'status': status,
        'description': description,
        'data': {'chat_id': chat_id}
    })


@app.route('/set_enrollment', methods=['POST'])
def set_enrollment():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    status, description = database.set_enrollment(request.values['chat_id'], session['username'])

    return json.dumps({'status': status, 'description': description})


@app.route('/set_moderator', methods=['POST'])
def set_moderator():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    status, description = database.set_enrollment(
        request.values['chat_id'], session['username'], moderator=request.values['moderator'])

    return json.dumps({'status': status, 'description': description})


@app.route('/set_banned', methods=['POST'])
def set_banned():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    status, description = database.set_enrollment(
        request.values['chat_id'], session['username'], banned=request.values['banned'])

    return json.dumps({'status': status, 'description': description})


@app.route('/get_nearby_chats', methods=['POST'])
def get_nearby_chats():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    # If user is specified, then it will only return chats for that user
    status, description, chats = database.get_nearby_chats(request.values['location'])

    return json.dumps({
        'status': status,
        'description': description,
        'data': chats
    })


@app.route('/get_user_chats', methods=['POST'])
def get_user_chats():
    # Ensure key is valid
    if request.values['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    # If user is specified, then it will only return chats for that user
    status, description, chats = database.get_user_chats(session['username'])

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

    data = (request.values['chat_id'], session['username'], request.values['value'])
    status, description = database.new_message(*data)

    return json.dumps({'status': status, 'description': description})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
