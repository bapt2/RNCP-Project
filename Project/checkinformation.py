from flask import request, redirect, session, render_template, url_for, flash, jsonify
from Project import views, socketio, db, bcrypt
from flask_socketio import join_room, leave_room, send, emit
from flask_login import login_user, current_user
from werkzeug.utils import secure_filename
from collections import defaultdict
from string import ascii_uppercase
from Project.models import User
import random, os


rooms = {}
sockets = defaultdict(dict)

def generate_unique_code(length):
    while True:
        code =  ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break

    return code

def checkSigninForm():
    form_info = request.form
    name = form_info.get("pseudo")
    email = form_info.get("email")
    password = form_info.get("password")


    if not checkUsername(name):
        flash('Ce nom d\'utilisateur existe déja veuillez en choisir un autre', 'error')
        return redirect(url_for('signin'))

    if not checkEmail(email):
        flash('Cette email existe déja veuillez en choisir un autre', 'error')
        return redirect(url_for('signin'))
    
    if not checkPassword(password):
        flash('Ce mot de passe est trop court', 'error')
        return redirect(url_for('signin'))

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=name, mail=email, password=hashed_password)
            
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('login'))

def CheckLoginForm():
    form_info = request.form
    email = form_info.get("email")
    password = form_info.get("password")
    user = User.query.filter_by(mail=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        return redirect(url_for('home'))
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

    if len(password) < 8:
        return False
    return True

def checkRoomCreationForm():
    form_info = request.form
    code = form_info.get("join-room")
    player_number = form_info.get("player-number")
    music_number = form_info.get("music-number")
    create = form_info.get("create", False)
    join = form_info.get("join", False)

    if join != False and not code:
            flash('veuillez rentrer un code ', 'error')
            return redirect(url_for('home'))   

    room = code

    if create != False:
        if player_number == "" or music_number == "":
            flash('Il faut remplir ces deux cases', 'error')
            return redirect(url_for('home'))
        else:
            player_number = int(form_info.get("player-number"))
            music_number = int(form_info.get("music-number"))
            
        if player_number > 10 or player_number <= 1:
            flash('Le nombre de joueur ne peut être inferieur à 2 ou supérieur à 10', 'error')
            return redirect(url_for('home'))
                
        elif music_number > 20 or music_number < 1:
            flash('Le nombre de music ne peut être inferieur à 1 ou supérieur à 20', 'error')
            return redirect(url_for('home'))
            
        room = generate_unique_code(12)
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
        flash(f'Ce code {code} n\'éxiste pas veuillez vérifier que vous n\'ayez pas fait de faute', 'error')
        return redirect(url_for('home'))


    session["room"] = room
    session["name"] = current_user.username
    return redirect(url_for('game'))


def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for('home'))
    
    if rooms[room]["members"] == rooms[room]["maxPlayerNumber"]:
        flash('Le salon est complet, vous ne pouvez pas rentrer', 'error')
        return redirect(url_for('home'))
    
    return render_template('game.html', code=room, playerlist=rooms[room]["players"])


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

    rooms[room]["members"] +=1
    rooms[room]["players"].append(name)
    rooms[room]["ready"][name] = False

    sockets[room][name] = request.sid
    emit('username', {'username': name})
    send({'players': rooms[room]['players'], 'ready': rooms[room]["ready"]}, room=room)


@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    player_musics = [music for music in rooms[room]["musics"] if music["player"] == name]
    for music in player_musics:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], music["filename"])
        if os.path.exists(file_path):
            os.remove(file_path)
        rooms[room]["musics"].remove(music)

    if room in rooms:
        rooms[room]["members"] -=1
        rooms[room]["players"].remove(name)
        
        del sockets[room][name]
        
        if rooms[room]["ready"]:
            del rooms[room]["ready"][name]

        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({'players': rooms[room]['players'], 'ready': rooms[room]["ready"]}, room=room)


@socketio.on("player_ready")
def playerReady(data):
    room = session.get("room")
    name = session.get("name")

    if not room or not name:
        return
    
    rooms[room]["ready"][name] = data["ready"]
    send({'players': rooms[room]['players'], 'ready': rooms[room]["ready"]}, room=room)

    if all(rooms[room]["ready"].values()) and len(rooms[room]["players"]) >= 2 and len(rooms[room]["musics"]) >= 1:
        send({'start_game': True}, room=room)



from Project import app, ALLOWED_EXTENSION

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION

def audio():
    if 'audioFiles' not in request.files:
        return jsonify({"error": "no file part"}), 400
    
    files = request.files.getlist('audioFiles')
    if not files:
        return jsonify({"error": "no selected file"}), 400
    
   
    saved_file = []
    room = session.get("room")
    name = session.get("name")

    if room not in rooms:
        return jsonify({"error": "Room not found"}), 400

    for file in files:
        if len(rooms[room]["musics"]) < rooms[room]["maxMusicNumber"]:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                print(f"saving file to: {file_path}")
                file.save(file_path)
                saved_file.append(filename)
                rooms[room]["musics"].append({"filename": filename, "player": name})
            else:
                return jsonify({"error": "files type not allowed: {file.filename}"}), 400
        else:
                return jsonify({"error": "can't add more music: {file.filename}"}), 400

        
    return jsonify({"message": "files successfully uploaded", "files": saved_file}), 200

def nextMusic(room):
    if room in rooms:
        current_index = rooms[room]["currentMusicIndex"]
        if current_index >= len(rooms[room]["musics"]):
            sortedPoints = dict(sorted(rooms[room]["points"].items(), key=lambda item: item[1], reverse=True))
            rooms[room]["points"] = sortedPoints
            socketio.emit("winner", rooms[room]["points"], room=room)    
            return
        
        current_music = rooms[room]["musics"][current_index]
        
        rooms[room]["responseList"] = []
        rooms[room]["gameMaster"] = rooms[room]["musics"][current_index]["player"]

        for player in rooms[room]["players"]:
            emit("current_music", {
                'player': current_music["player"],
                'filename': current_music["filename"],
                'currentPlayer': player},
                room=room)

@socketio.on("next_music")
def handleNextMusic():
    room = session.get("room")
    if room:
        nextMusic(room)
    
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

            socketio.emit('evaluation_response', rooms[room]["responseList"], room=gameMasterSid)
    

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
            socketio.emit('evaluation_response', rooms[room]["responseList"], room=gameMasterSid)


@socketio.on("add_point")
def addPoint(name):
    room = session.get("room")
    if room in rooms and name in rooms[room]["players"]:
        if "points" not in rooms[room]:
            rooms[room]["points"] = {}

        if name not in rooms[room]["points"]:
            rooms[room]["points"][name] = 0

        rooms[room]["points"][name] += 1

    rooms[room]["currentMusicIndex"] +=1
    nextMusic(room)
