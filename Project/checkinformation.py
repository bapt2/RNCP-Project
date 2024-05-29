from flask import request, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from Project import db, bcrypt
from Project.models import User
from Project import views


def checkSigninForm():
    form_info = request.form
    name = form_info.get("pseudo")
    email = form_info.get("email")
    password = form_info.get("password")


    if not checkUsername(name):
        flash('Ce nom d\'utilisateur existe déja veuillez en choisir un autre', 'error')
        return redirect(url_for('inscription'))

    if not checkEmail(email):
        flash('Cette email existe déja veuillez en choisir un autre', 'error')
        return redirect(url_for('inscription'))
    
    if not checkPassword(password):
        flash('Ce mot de passe est trop court', 'error')
        return redirect(url_for('inscription'))

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=name, mail=email, password=hashed_password)
            
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('connection'))

def CheckLoginForm():
    form_info = request.form
    email = form_info.get("email")
    password = form_info.get("password")
    user = User.query.filter_by(mail=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        return redirect(url_for('index'))
    else:
        flash('Cette email ou ce mot de passe sont incorrecte', 'error')
        return redirect(url_for('login'))


def checkUsername(username):
    user = User.query.filter_by(username=username).first()

    if user:
        return False 
    return True


def checkEmail(email):
    email = User.query.filter_by(mail=email).first()

    if email:
        return False
    return True

def checkPassword(password):

    if password.length < 8:
        return False
    return True