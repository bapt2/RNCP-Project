from flask import (
    request, redirect, session, render_template,
    url_for, flash, jsonify)
from flask_socketio import join_room, leave_room, send, emit
from Project import views, socketio, db, bcrypt, client_id
from flask_login import login_user, current_user
from werkzeug.utils import secure_filename
from Project.models import User, UserInfo
from collections import defaultdict
from string import ascii_uppercase
import requests
import random
import os


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
            "ready": {}
            }

    elif code not in rooms:
        flash(f'Ce code {code} n\'éxiste pas veuillez vérifier '
              'que vous n\'ayez pas fait de faute', 'error')
        return redirect(url_for('home'))

    session["room"] = room
    session["name"] = current_user.username

    print(f"token: {session.get('spotify_access_token')} check information")
    if not session.get('spotify_access_token'):
        return redirect(f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=token&redirect_uri=http://127.0.0.1:5000/spotify_callback&scope=user-modify-playback-state%20user-read-playback-state%20user-library-read")

    return redirect(url_for('spotify_callback'))


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
    
    leave_room(room)

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
    print(f"{rooms[room]['players']} s'est déconnecter")
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
        if current_index >= len(rooms[room]["musics"]):
            sortedPoints = dict(sorted(rooms[room]["points"].items(),
                                       key=lambda item: item[1], reverse=True))
            rooms[room]["points"] = sortedPoints

            for player in sortedPoints:
                username = User.query.filter_by(username=player).first()
                username.userinfo.number_game_win += 1
                db.session.commit()

            socketio.emit("winner", rooms[room]["points"], room=room)
            return

        current_music = rooms[room]["musics"][current_index]
        track_id = current_music["track_id"]
        current_track = get_track_url(track_id, access_token)
        print(current_track)
        if not current_track:
            print(f"Aucune preview disponible pour le track Id {track_id}")
            return
        
        rooms[room]["responseList"] = []
        gameMaster = rooms[room]["musics"][current_index]["player"]
        rooms[room]["gameMaster"] = gameMaster

        for player in rooms[room]["players"]:
            emit("current_music", {
                'player': current_music["player"],
                'preview_url': current_track,
                'currentPlayer': player},
                room=room)


@socketio.on("next_music")
def handleNextMusic():
    room = session.get("room")
    access_token = session.get("spotify_access_token")
    if room:
        nextMusic(room, access_token)


@socketio.on("player_response")
def playerResponse(data):
    room = session.get("room")

    print(data["name"], rooms[room]["gameMaster"])
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
    print(name)
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
    access_token = session.get("spotify_access_token")

    if room in rooms and name in rooms[room]["players"]:
        if "points" not in rooms[room]:
            rooms[room]["points"] = {}

        if name not in rooms[room]["points"]:
            rooms[room]["points"][name] = 0

        rooms[room]["points"][name] += 1

    rooms[room]["currentMusicIndex"] += 1
    print(f"{room}: {access_token}")
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
            print(f'{track_id} ajouter par {username}')
            return jsonify({'success': True}), 200
        else:
            print("test")
            return jsonify({'message': 'Nombre de musiques maximum atteintes'}), 200
    else:
        return jsonify({'error': 'missing trackId or room'}), 400
    
def get_track_url(track_id, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        preview_url = response.json().get("preview_url")
        return preview_url
    else:
        print(f"Erreur {response.status_code} lors de la récuperation de la piste {track_id}")
        return None