from flask import (
    request, redirect, session, render_template,
    url_for, flash, jsonify)
from flask_socketio import join_room, leave_room, send, emit
from Project import views, socketio, db, client_id, client_secret
from Project.models import User, UserInfo
from flask_login import current_user
from collections import defaultdict
from string import ascii_uppercase
import time, random, requests
from base64 import b64encode


# --------------------------------------- initial system begenning --------------------------------
rooms = {}
sockets = defaultdict(dict)


def generateUniqueCode(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break

    return code

def checkRoomCreationForm():
    form_info = request.form
    code = form_info.get("join-room")
    player_number = form_info.get("player-number")
    music_number = form_info.get("music-number")
    create = form_info.get("create", False)
    join = form_info.get("join", False)

    if join is not False and not code:
        flash('veuillez rentrer un code ', 'error')
        return redirect(url_for('home'))

    room = code


    if create is not False:
        if player_number == "" or music_number == "":
            flash('Il faut remplir ces deux cases', 'error')
            return redirect(url_for('home'))
        else:
            player_number = int(form_info.get("player-number"))
            music_number = int(form_info.get("music-number"))

        if player_number > 10 or player_number <= 1:
            flash('Le nombre de joueur ne peut être '
                  'inferieur à 2 ou supérieur à 10', 'error')
            return redirect(url_for('home'))

        elif music_number > 20 or music_number < 1:
            flash('Le nombre de music ne peut être '
                  'inferieur à 1 ou supérieur à 20', 'error')
            return redirect(url_for('home'))

        room = generateUniqueCode(12)
        rooms[room] = {
            "members": 0,
            "musicsNumber": 0,
            "currentMusicIndex": 0,
            "maxMusicNumber": music_number,
            "maxPlayerNumber": player_number,
            "players": [],
            "musics": [],
            "responseList": [],
            "ready": {},
            "points": {}
            }

    elif code not in rooms:
        flash(f'Ce code {code} n\'éxiste pas veuillez vérifier '
              'que vous n\'ayez pas fait de faute', 'error')
        return redirect(url_for('home'))

    session["room"] = room
    session["name"] = current_user.username

    if not session.get('access_token'):
        return redirect(f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri=http://127.0.0.1:5000/spotify_callback&scope=user-modify-playback-state%20user-read-playback-state%20user-library-read")

    return redirect(url_for('game'))


def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for('home'))

    if rooms[room]["members"] == rooms[room]["maxPlayerNumber"]:
        flash('Le salon est complet, vous ne pouvez pas rentrer', 'error')
        return redirect(url_for('home'))

    return render_template(
        'game.html', code=room,
        playerlist=rooms[room]["players"])


@socketio.on("connect")
def connect():
    room = session.get("room")
    name = session.get("name")

    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return

    join_room(room)

    rooms[room]["members"] += 1
    rooms[room]["players"].append(name)
    rooms[room]["ready"][name] = False

    sockets[room][name] = request.sid
    emit('username', {'username': name, 'room': room})
    send({'players': rooms[room]['players'],
          'ready': rooms[room]["ready"]}, room=room)


@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    if room not in rooms:
        return
    

    rooms[room]["musics"] = [
        music for music in rooms[room]["musics"]
        if music["player"] != name]

    if name in rooms[room]["players"]:
        rooms[room]["members"] -= 1
        rooms[room]["players"].remove(name)

    if room in sockets and name in sockets[room]:
        del sockets[room][name]

    if "ready" in rooms[room] and name in rooms[room]["ready"]:
        del rooms[room]["ready"][name]

    if rooms[room]["members"] <= 0:
        del rooms[room]
    leave_room(room)
    send({
        'players': rooms[room]['players'],
        'ready': rooms[room]["ready"]}, room=room)


@socketio.on("player_ready")
def playerReady(data):
    room = session.get("room")
    name = session.get("name")

    if not room or not name:
        return

    rooms[room]["ready"][name] = data["ready"]
    send({
        'players': rooms[room]['players'],
        'ready': rooms[room]["ready"]}, room=room)

    ready = all(rooms[room]["ready"].values())
    enough_player = len(rooms[room]["players"]) >= 2
    enough_music = len(rooms[room]["musics"]) >= 1

    if ready and enough_player and enough_music:
        for player in range(len(rooms[room]["players"])):
            username = User.query.filter_by(username=name).first()
            username.userinfo.number_game_played += 1
            name = rooms[room]["players"][player]
        db.session.commit()
        send({'start_game': True}, room=room)


from Project import app


def nextMusic(room, access_token):
    if room in rooms:
        current_index = rooms[room]["currentMusicIndex"]
        print("test de passage: 1")
        if current_index >= len(rooms[room]["musics"]):
            print(len(rooms[room]["musics"]))
            if rooms[room]["points"] is not None:
                print("test de passage: finale")
                sortedPoints = dict(sorted(rooms[room]["points"].items(),
                                        key=lambda item: item[1], reverse=True))
                rooms[room]["points"] = sortedPoints
                print(sortedPoints)
                for player in sortedPoints:
                    username = User.query.filter_by(username=player).first()
                    username.userinfo.number_game_win += 1
                    db.session.commit()

                socketio.emit("end-game", rooms[room]["points"], room=room)
                return
            elif rooms[room]["points"] is None:
                socketio.emit("end-game", rooms[room]["points"], room=room)
            return
        print("test de passage: 2")
        current_music = rooms[room]["musics"][current_index]
        track_id = current_music["track_id"]
        get_valide_access_token()
        print("test de passage: get_valide_access_token")

        print(f"{current_index} = {get_track_url(track_id, access_token)} : on {len(rooms[room]['musics'])}")
        current_track = get_track_url(track_id, access_token)
        print(current_track)
        if not current_track:
            current_index += 1
            rooms[room]['currentMusicIndex'] = current_index
            print(f"Aucune preview disponible pour le track Id {track_id}")
            handleNextMusic()
            return
        
        rooms[room]["responseList"] = []
        gameMaster = current_music["player"]
        rooms[room]["gameMaster"] = gameMaster

        print(f"Avant incrémentation : Index actuel {rooms[room]['currentMusicIndex']}")
        current_index += 1
        rooms[room]['currentMusicIndex'] = current_index
        print(f"Après incrémentation : Index actuel {rooms[room]['currentMusicIndex']}")
        for player in rooms[room]["players"]:
            emit("current_music", {
                'player': current_music["player"],
                'preview_url': current_track,
                'currentPlayer': player},
                room=room)


@socketio.on("next_music")
def handleNextMusic():
    room = session.get("room")
    access_token = session.get("access_token")
    if room:
        nextMusic(room, access_token)


@socketio.on("player_response")
def playerResponse(data):
    room = session.get("room")

    if data["name"] != rooms[room]["gameMaster"]:
        rooms[room]["responseList"].append({
                    "name": data["name"],
                    "response": data["response"],
                    })

    if len(rooms[room]["responseList"]) == rooms[room]["members"] - 1:
        gameMaster = rooms[room]["gameMaster"]
        gameMasterSid = sockets[room].get(gameMaster)
        socketio.emit('stop_music', room=room)
        if gameMasterSid:
            socketio.emit('evaluation_response',
                          rooms[room]["responseList"], room=gameMasterSid)


@socketio.on("end_of_round")
def endOfRound(name):
    room = session.get("room")
    if name != rooms[room]["gameMaster"]:
        rooms[room]["responseList"].append({
                    "name": name,
                    "response": "",
                    })

    if len(rooms[room]["responseList"]) == rooms[room]["members"] - 1:
        gameMaster = rooms[room]["gameMaster"]
        gameMasterSid = sockets[room].get(gameMaster)
        if gameMasterSid:
            socketio.emit('evaluation_response',
                          rooms[room]["responseList"], room=gameMasterSid)


@socketio.on("add_point")
def addPoint(name):
    room = session.get("room")
    access_token = session.get("access_token")

    if room in rooms and name in rooms[room]["players"]:
        if name not in rooms[room]["points"]:
            rooms[room]["points"][name] = 0

        rooms[room]["points"][name] += 1

    nextMusic(room, access_token)

# --------------------------------------- initial sytem end --------------------------------


def check_track():
    data = request.get_json()
    track_id = data.get('trackId')
    room = session.get('room')
    username = data.get('username')

    if track_id and room in rooms:
        if len(rooms[room]["musics"]) < rooms[room]["maxMusicNumber"]:
            rooms[room]['musics'].append({'track_id': track_id, 'player': username})
            return jsonify({'success': True}), 200
        else:
            return jsonify({'message': 'Nombre de musiques maximum atteintes'}), 200
    else:
        return jsonify({'error': 'missing trackId or room'}), 400
    
def get_track_url(track_id, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    response = requests.get(url, headers=headers)
    preview_url = response.json().get("preview_url")
    if response.status_code == 200:
        preview_url = response.json().get("preview_url")
        return preview_url
    else:
        print(f"Erreur {response.status_code} lors de la récuperation de la piste {track_id}")
        return None
        
def refresh_access_token():
    refresh_token = session.get('refresh_token')

    if not refresh_token:
        print("Aucun refresh_token n'est disponible")
        return None
    
    
    token_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + b64encode(f"{client_id}: {client_secret}".encode()).decode()
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post(token_url, headers=headers, data=data)

    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens['access_token']
        expires_in = tokens['expires_in']

        session['access_token'] = access_token
        session['token_expiration'] = time.time() + expires_in

        print('nouveau access_token récupérer')
        return access_token
    else:
        print(f"Erreur lors du rafraichissement du token: {response.status_code}, {response.json}")
        return None
    
def get_valide_access_token():
    if time.time() > session.get('token_expiration', 0):
        print("Token expiré, tentative de rafraichissement...")
        return refresh_access_token()
    
    return session.get('access_token')