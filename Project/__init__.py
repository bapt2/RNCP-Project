from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from requests import post, get
from flask import Flask
import base64
import json
import os

load_dotenv()

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), 'uploads'))
ALLOWED_EXTENSION = {'mp3', 'wav', 'ogg'}

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

migrate = Migrate()
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

bcrypt = Bcrypt(app)

db = SQLAlchemy(app)

socketio = SocketIO(app)
socketio.init_app(app)

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

login_manager = LoginManager(app)
login_manager.login_view = 'login'

from Project.models import User, UserInfo
with app.app_context():
    db.create_all()

migrate.init_app(app, db)
# ne pas supprimer permet l'accès au routes
from Project import views