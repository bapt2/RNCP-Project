# RNCP-Project

## Techologies used
### Back
* Python
* Sqlite

#### Library
* Flask
* Flask-sqlalchemy
* Flask_bcrypt
* Flask-login
* Flask-socketio
* Requests
* Dotenv

### Front
* HTML
* CSS
* Javascript

### Dependancies
```
Flask: 3.0.3 or highter
Flask-SQLAlchemy: 3.1.1 or highter
Flask-Bcrypt: 1.0.1 or highter
Flask-Login: 0.6.3 or highter
Flask-SocketIO: 5.3.6 or highter
python-dotenv: 1.0.1 or highter
requests: 2.32.2 or highter
Sqlite3: 3.37.2 or highter
```

## Virtual Environment
### Create your environement
```
$ python3 -m venv name
$ source name/bin/activate
```

### Install dependancies
```
$ pip install flask
$ pip install flask-sqlalchemy
$ pip install flask_bcrypt
$ pip install flask-login
$ pip install flask-socketio
$ pip install python-dotenv
$ pip install requests
```

#### Sqlite3
```
apt install sqlite3
```
if not working
```
sudo apt install sqlite3
```

## Start the server
this command bellow will create the app and initialise the database or create one if doesn't existe
```
$ python3 run.py
```