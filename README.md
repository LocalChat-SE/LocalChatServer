## Server for Local Chat Application
Centralized server for communication between android users and message storage


### Specification
Send message:
1. Accept message via the flask API
2. Store message in LocalChat.db
3. Send message or notification to user

Retrieve chat history:
1. Accept request for history
2. Query database for history
3. Return history

Search nearby chats:
1. Accept request for nearby chats
2. Query database for nearby chats
3. Return nearby chats

### Setup
1. Clone this repository with git. 'Github for Windows' has a nice GUI for folks just starting out.
2. Install python 3. 
    - I recommend installing 'for all users' and enabling edits to the path variable.
    - Run ```python --version``` in console to check proper installation. Should print python 3.x.
3. Install the python dependencies. In windows, from CMD or PowerShell:
```
    cd [PATH_TO_CLONED_REPOSITORY]
    pip install -r requirements.txt
```
4. Create './api_key.txt' with our api key inside.
5. Start the server:
```
    python ./server.py
```
You should now be able to send requests to the server running locally on your computer.
http://localhost:8888
If you drop the url into a browser, it should say 'Not Found.' But that's fine, we'll be sending requests instead.
