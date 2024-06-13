from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask import Flask
from dotenv import load_dotenv
from flask_socketio import SocketIO
import os

load_dotenv()

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), 'uploads'))
ALLOWED_EXTENSION = {'mp3', 'wav', 'ogg'}

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] =  os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

bcrypt = Bcrypt(app)

db = SQLAlchemy(app)

socketio = SocketIO(app)
socketio.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'connection'

from Project.models import User
with app.app_context():
    db.create_all()
# ne pas supprimer permet l'accès au routes
from Project import views

