from flask import (
    render_template, request, redirect, url_for,
    send_from_directory, flash,jsonify, session)
import requests
from flask_login import logout_user, login_required, current_user
from Project import checkinformation
from Project.game import check_track, checkRoomCreationForm, room
from Project.models import User, UserInfo
from Project import app, db
import os


@app.route('/')
@app.route('/Accueil', methods=['GET', 'POST'])
def home():
    if (request.method == 'POST'):
        result = checkRoomCreationForm()
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
    userinfo = UserInfo.query.filter_by(user_id=current_user.id).first()
    print(userinfo.user.username)
    return render_template('account.html')


@app.route('/jeu')
@login_required
def game():
    return room()


@app.route('/uploads/<filename>')
def uploadedFile(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else:
        return jsonify({"error": "file not found"}), 404


@app.route('/save-theme', methods=['POST'])
def save_theme():
    data = request.get_json()
    theme = data.get('theme')

    userinfo = UserInfo.query.filter_by(user_id=current_user.id).first()
    if theme == 'night':
        userinfo.night_mode = True
    else:
        userinfo.night_mode = False
    db.session.commit()
    userinfo = UserInfo.query.filter_by(user_id=current_user.id).first()
    print("thème reçu: ", theme)
    print("thème dans la db: ", userinfo.night_mode)

    return jsonify({'message': 'thème sauvegarder avec succès', 'thème': theme})

@app.route('/get-theme', methods=['GET'])
def get_theme():
    if current_user.is_authenticated:
        userinfo = UserInfo.query.filter_by(user_id=current_user.id).first()
        if userinfo:
            theme = 'night' if userinfo.night_mode else 'day'
            return jsonify({'theme': theme})
        else:
            return jsonify({'message': 'Utilisateur non trouvé'}), 404
    else:
        return jsonify({'theme': 'day'})

@app.route('/store_token', methods=['POST'])
def store_token():
    data = request.json

    access_token = data.get('token')
    print(f"token : {access_token}")
    if access_token:
        session['spotify_access_token'] = access_token
        return jsonify({'message': 'token stored successfully'}), 200
    else:
        return jsonify({'error': 'no token provided'}), 400

@app.route('/spotify_callback')
def spotify_callback():
    print('test')
    access_token = request.args.get('access_token')
    print(f"token : {access_token}")
    print(f"token: {session.get('spotify_access_token')} check information")
    if access_token:
        session['spotify_access_token'] = access_token
        
        #return redirect(url_for('verify_token'))
        return redirect(url_for('game'))

    elif session.get('spotify_access_token'):
        #return redirect(url_for('verify_token'))
        return redirect(url_for('game'))

    else:
        flash("Erreur de connexion à Spotify", "error")
        return redirect(url_for('home'))


@app.route('/get_token', methods=['GET'])
def get_token():
    access_token = session.get('spotify_access_token')
    if access_token:
        return jsonify({'token': access_token}), 200
    else:
        return jsonify({'error': "token not found"}), 404


# permet de verifier les information de l'utilisateur
@app.route('/verify_token')
def verify_token():
    access_token = session.get('spotify_access_token')
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    print(f'response: {response}')

    if response.status_code == 200:
        user_info = response.json()
        return jsonify({'user_info': user_info, 'scopes': session.get('spotify_access_token')}), 200
    else:
        return jsonify({'error': 'Invalid token or expired token', 'details': response.json()}), response.status_code
    

@app.route('/select_track', methods=["POST"])
def select_track():
    return check_track()