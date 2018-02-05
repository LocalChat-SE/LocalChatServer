## Server for Local Chat Application
Centralized server for communication between android users and message storage


### Documentation
Endpoints for the api are documented in the ChatServer.postman_collection.json.  
This documentation can be imported into postman, where you can also send requests.  
https://www.getpostman.com/  

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
4. Create './api_key.txt' with our api key inside. The docs use 'SecretKey' by default.
5. Start the server:
```
    python ./server.py
```
You should now be able to send requests to the server running locally on your computer.  
http://localhost:8888  
If you drop the url into a browser, it should say 'Not Found.' But that's fine, we'll be sending requests instead.  

### MySQL Local Setup
1. Download and install MySQL community edition, set it up as a dev machine.
``` 
    User: LocalChat
    Password: 0rZv5#VA
    User Port: 33060
```
