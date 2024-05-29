from flask import render_template, request, redirect, url_for
from Project import app
from Project.models import User
from Project import checkinformation
from flask_login import logout_user, login_required


@app.route('/')
@app.route('/Accueil', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/Information')
def info():
    return render_template('info.html')


@app.route('/type')
def type():
    return render_template('type.html')


@app.route('/signin', methods=['GET', 'POST'])
def inscription():
    if (request.method == 'POST'):
        
        result = checkinformation.checkSigninForm()
        if (result):
            return result
    return render_template('signin.html')


@app.route('/login', methods=['GET', 'POST'])
def connection():
    if (request.method == 'POST'):
        result = checkinformation.CheckLoginForm()
        if (result):
            return result
    return render_template('login.html')


@app.route('/logout')
def deconnection():
    logout_user()
    return redirect(url_for('index'))



@app.route('/account')
@login_required
def account():
    return render_template('account.html')

