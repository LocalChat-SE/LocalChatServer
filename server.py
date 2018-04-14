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

# I would have just decorated the api key and login checks to remove some duplicated code.
# Unfortunately, flask seems to be checking string literal function names for repeats.


# read from the request arguments if the body is undefined.
def parse_request():
    body = request.get_data().decode('utf-8')
    try:
        return json.loads(body)
    except ValueError:
        return request.values


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
    data = parse_request()

    # Ensure key is valid
    if data['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' in session:
        return json.dumps({'status': True, 'description': 'user already logged into server'})

    status, description = database.get_user(data['username'], data['password'])

    if status:
        session['username'] = data['username']

    return json.dumps({'status': status, 'description': description})


@app.route('/logout', methods=['POST'])
def logout():
    data = parse_request()

    # Ensure key is valid
    if data['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': True, 'description': 'already logged out'})

    session.pop('username', None)
    return json.dumps({'status': True, 'description': 'logged off server'})


@app.route('/new_user', methods=['POST'])
def new_user():
    data = parse_request()

    # Ensure key is valid
    if data['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    status, description = database.set_user(data['username'], data['password'])

    # Convert to json string and return
    return json.dumps({'status': status, 'description': description})


@app.route('/delete_user', methods=['POST'])
def delete_user():
    req_data = parse_request()

    # Ensure key is valid
    if req_data['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    status, description = database.delete_user(session['username'], req_data['password'])

    # Convert to json string and return
    return json.dumps({'status': status, 'description': description})


@app.route('/new_chat', methods=['POST'])
def new_chat():
    req_data = parse_request()

    # Ensure key is valid
    if req_data['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    data = (req_data['name'], req_data['location'], req_data['description'])

    status, description, chat_id = database.set_chat(*data)
    database.set_enrollment(chat_id, session['username'], modded=True)

    return json.dumps({
        'status': status,
        'description': description,
        'data': {'chat_id': chat_id}
    })


@app.route('/update_chat_name', methods=['POST'])
def update_chat_name():
    req_data = parse_request()

    # Ensure key is valid
    if req_data['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    status, description = database.update_chat(
        req_data['chat_id'], session['username'], name=req_data['name'])

    return json.dumps({'status': status, 'description': description})


@app.route('/update_chat_location', methods=['POST'])
def update_chat_location():
    req_data = parse_request()

    # Ensure key is valid
    if req_data['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    status, description = database.update_chat(
        req_data['chat_id'], session['name'], location=req_data['location'])

    return json.dumps({'status': status, 'description': description})


@app.route('/update_chat_description', methods=['POST'])
def update_chat_description():
    req_data = parse_request()

    # Ensure key is valid
    if req_data['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    status, description = database.update_chat(
        req_data['chat_id'], session['name'], description=req_data['description'])

    return json.dumps({'status': status, 'description': description})


@app.route('/set_enrollment', methods=['POST'])
def set_enrollment():
    req_data = parse_request()

    # Ensure key is valid
    if req_data['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    status, description = database.set_enrollment(req_data['chat_id'], session['username'])

    return json.dumps({'status': status, 'description': description})


@app.route('/set_moderator', methods=['POST'])
def set_moderator():
    req_data = parse_request()

    # Ensure key is valid
    if req_data['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    status, description = database.set_moderator(
        req_data['chat_id'], session['username'], req_data['username'])

    return json.dumps({'status': status, 'description': description})


@app.route('/set_banned', methods=['POST'])
def set_banned():
    req_data = parse_request()

    # Ensure key is valid
    if req_data['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    status, description = database.set_banned(
        req_data['chat_id'], session['username'], req_data['username'], req_data['banned'])

    return json.dumps({'status': status, 'description': description})


@app.route('/get_nearby_chats', methods=['POST'])
def get_nearby_chats():
    req_data = parse_request()

    # Ensure key is valid
    if req_data['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    status, description, chats = database.get_nearby_chats(req_data['location'])

    return json.dumps({
        'status': status,
        'description': description,
        'data': chats
    })


@app.route('/get_user_chats', methods=['POST'])
def get_user_chats():
    req_data = parse_request()

    # Ensure key is valid
    if req_data['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    status, description, chats = database.get_user_chats(session['username'])

    return json.dumps({
        'status': status,
        'description': description,
        'data': chats
    })


@app.route('/get_chat', methods=['POST'])
def get_chat():
    req_data = parse_request()
    # Ensure key is valid
    if req_data['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    status, description, data = database.get_chat(
        req_data['chat_id'], session['username'], req_data['limit'], req_data['offset'])

    return json.dumps({
        'status': status,
        'description': description,
        'data': data
    })


@app.route('/new_message', methods=['POST'])
def new_message():
    req_data = parse_request()

    # Ensure key is valid
    if req_data['api_key'] != api_key:
        return json.dumps({'status': False, 'description': 'invalid api key'})

    if 'username' not in session:
        return json.dumps({'status': False, 'description': 'user is not logged in'})

    data = (req_data['chat_id'], session['username'], req_data['value'])
    status, description = database.new_message(*data)

    return json.dumps({'status': status, 'description': description})


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
