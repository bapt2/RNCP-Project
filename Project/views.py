from flask import (
    render_template, request, redirect, url_for,
    send_from_directory, flash,jsonify, session)
import requests
from flask_login import logout_user, login_required, current_user
from Project import checkinformation
from Project.game import check_track, checkRoomCreationForm, room, refresh_access_token
from Project.models import User, UserInfo
from Project import app, db, client_id, client_secret
from base64 import b64encode
import os, time


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


@app.route('/spotify_callback')
def spotify_callback():
    redirect_uri = "http://127.0.0.1:5000/spotify_callback"
    code = request.args.get('code')
    token_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + b64encode(f"{client_id}:{client_secret}".encode()).decode()
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }
    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
        expires_in = tokens['expires_in']

        session['access_token'] = access_token
        session['refresh_token'] = refresh_token
        session['token_expiration'] = time.time() + expires_in
        print("L'access_token et le refresh_token sont bien sauvegarder")
        return redirect(url_for('game'))

    else:
        print(f"Erreur: {response.status_code}, {response.json()}")
        return redirect(url_for('home'))

    
@app.route('/search_music', methods=['GET'])
def search_music():
    query = request.args.get('query')
    access_token = session.get('access_token')

    if not access_token:
        refresh_access_token()
        return None
    
    search_url = f"https://api.spotify.com/v1/search?q=${query}&type=track"
    headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json'
        }
    
    response = requests.get(search_url, headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'erreur': f"Il y a  une erreur avec l'api de spotify {response.status_code}, {response.json()}"})


@app.route('/select_track', methods=["POST"])
def select_track():
    return check_track()


# permet de verifier les information de l'utilisateur
@app.route('/verify_token')
def verify_token():
    access_token = session.get('spotify_access_token')
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        return jsonify({'user_info': user_info, 'scopes': session.get('spotify_access_token')}), 200
    else:
        return jsonify({'error': 'Invalid token or expired token', 'details': response.json()}), response.status_code