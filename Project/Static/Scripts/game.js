const socket = io();

socket.on("connect", () => {
    console.log("Connected to server")
})

socket.on("username", data => {
    const username = data.username
    sessionStorage.setItem("username", username)
})

socket.on("message", data => {
    if (data.players) {
        const playerList = document.getElementById("player-list")
        playerList.innerHTML = ""
        data.players.forEach(player => {
            const li = document.createElement("li")
            li.innerHTML = player
            playerList.appendChild(li)
        });
    }
    if (data.start_game) {
        waitingPanel = document.querySelector(".waiting-panel")
        gamePanel = document.querySelector(".game")
        waitingPanel.style.display = "none"
        gamePanel.style.display = "flex"
        socket.emit("next_music")
    }
})

socket.on("disconnect", () => {
    console.log("Disconnected from server")
})

let isPlaying = false

socket.on("current_music", data => {
    if (isPlaying) return

    isPlaying = true

    const currentMusicPlayer = data.player
    const currentMusicFile = data.filename
    const currentPlayer = sessionStorage.getItem("username")

    if (currentMusicPlayer === currentPlayer) {
        document.getElementById("action").innerHTML = "Vous allez évaluer les réponses"
    }
    else {
        document.getElementById("action").innerHTML = "vous allez deviner les musics"

        const responseInput = document.createElement('textarea')
        responseInput.placeholder = "Écriver votre réponse"
        document.querySelector(".player").appendChild(responseInput)

        const sendBtn = document.createElement('button')
        sendBtn.innerHTML = "Envoyer"
        document.querySelector(".player").appendChild(sendBtn)

        sendBtn.addEventListener("click", () => {
            const responseText = responseInput.value
            socket.emit('player_response', { response: responseText, name: currentPlayer })
            responseInput.value = ""
            responseInput.style.display = 'none'
            sendBtn.style.display = 'none'
        })

    }

    const audioPlayer = document.getElementById("audio-player")
    audioPlayer.pause();
    audioPlayer.src = `/uploads/${currentMusicFile}`
    console.log("Audio src: ", audioPlayer.src)
    audioPlayer.onloadeddata = () => {
        audioPlayer.play().then(() => {
            isPlaying = false

        }).catch(error => {
            console.error("Playback error: ", error)
            isPlaying = false
        })
    }

    audioPlayer.onended = () => {
        const allBtn = document.querySelectorAll('#player-anwser button')
        socket.emit("end_of_round", sessionStorage.getItem("username"))
        clearAnwser = document.querySelector(".player")
        clearAnwser.innerHTML = ""
        allBtn.forEach(button => {
            button.style.display = 'inline-block'
        })
    }

    audioPlayer.onerror = () => {
        console.error("Failed to load audio file")
        isPlaying = false
    }
})


socket.on("evaluation_response", data => {
    const responseList = document.getElementById("player-awnser")
    responseList.innerHTML = ""
    data.forEach(responsedata => {
        console.log(responsedata)
        const li = document.createElement("li")
        li.innerHTML = responsedata.name + ': ' + responsedata.response
        responseList.appendChild(li)

        const pointBtn = document.createElement("button")
        pointBtn.innerHTML = 'ajoute 1 point'
        pointBtn.style.display = 'none'
        li.appendChild(pointBtn)
        pointBtn.addEventListener("click", () => {
            socket.emit("add_point", responsedata.name)
            responseList.innerHTML = ""
        })
    })

    const allBtn = responseList.querySelectorAll('button')
    allBtn.forEach(button => {
        button.style.display = 'inline-block'

    })
})


socket.on("stop_music", () =>{
    const audioPlayer = document.getElementById("audio-player")
    audioPlayer.pause()
})


let isready = false
const readybtn = document.getElementById("ready")
readybtn.addEventListener("click", () => {
    isready = !isready
    readytxt = document.getElementById("ready-text")
    if (isready) {
        readytxt.style.color = "green"
        readytxt.innerHTML = "vous êtes prêt"
    }
    else {
        readytxt.style.color = "red"
        readytxt.innerHTML = "vous n'êtes pas prêt"
    }
    socket.emit("player_ready", { ready: isready })
})

const uploadForm = document.getElementById("upload-form");
const audioFileInput = document.getElementById("audio-file");

uploadForm.addEventListener("submit", (event) => {
    event.preventDefault()

    const files = audioFileInput.files;
    if (files.length == 0) {
        alert("veuillez envoyer au moins un fichier audio")
        return
    }

    const formData = new FormData()
    for (const file of files) {
        formData.append("audioFiles", file)
    }
    fetch("/upload-audio", {
        method: "POST",
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            console.log("Fichiers audio téléchargés avec succès: ", data)
        })
        .catch(error => {
            console.error("Erreur lors du chargement des fichiers audio: ", error)
        })
})

socket.on("winner", data =>{
    gamePanel = document.querySelector(".game")
    winnerPanel = document.querySelector(".winner")
    gamePanel.style.display = 'none'
    winnerPanel.style.display = 'flex'

    const [winner, winerPoints] = Object.entries(data)[0]
    h2 = document.getElementById("winner-text")
    h2.innerHTML = `Le gagnant est: ${winner} avec ${winerPoints}`

    const ranking = document.getElementById("ranking")
    ranking.innerHTML = ""
    for (const [player, point] of Object.entries(data)) {
        const li = document.createElement("li")
        li.innerHTML = `${player}: ${point} points`
        ranking.appendChild(li)
    }
})