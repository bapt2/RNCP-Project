from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] =  os.getenv('SQLALCHEMY_DATABASE_URI')
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'connection'
from Project.models import User
with app.app_context():
    db.create_all()

# ne pas supprimer permet l'accès au routes
from Project import views
