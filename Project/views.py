from flask import render_template, request, redirect, url_for, send_from_directory, jsonify
from flask_login import logout_user, login_required
from Project import checkinformation
from Project.models import User
from Project import app
import os

@app.route('/')
@app.route('/Accueil', methods=['GET', 'POST'])
def home():
    if (request.method == 'POST'):   
        result = checkinformation.checkRoomCreationForm()
        if (result):
            return result
    return render_template('index.html')


@app.route('/Information')
def info():
    return render_template('info.html')


@app.route('/Type')
def type():
    return render_template('type.html')


@app.route('/Inscription', methods=['GET', 'POST'])
def signin():
    if (request.method == 'POST'):
        
        result = checkinformation.checkSigninForm()
        if (result):
            return result
    return render_template('signin.html')


@app.route('/Connexion', methods=['GET', 'POST'])
def login():
    if (request.method == 'POST'):
        result = checkinformation.CheckLoginForm()
        if (result):
            return result
    return render_template('login.html')


@app.route('/Deconnexion')
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route('/Compte')
@login_required
def account():
    return render_template('account.html')


@app.route('/jeu')
@login_required
def game():
    return checkinformation.room()

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    return checkinformation.audio()

@app.route('/uploads/<filename>')
def uploadedFile(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else:
        return jsonify({"error": "file not found"}), 404
    