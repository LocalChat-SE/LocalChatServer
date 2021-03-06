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
If you drop the url into a browser, it will format the entire database into tables in your browser. This is to make debugging easy!  

### MySQL Local Setup
1. Download and install MySQL community edition, set it up as a dev machine.
``` 
    User: LocalChat
    Password: 0rZv5#VA
    User Port: 33060
```
2. Sometimes the server is stubborn and won't start. This can be fixed via running the following command in an administrator cmd session:
```
"C:\Program Files\MySQL\MySQL Server 5.7\bin\mysqld" --install
```
You may need to tweak the path.
