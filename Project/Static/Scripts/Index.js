function afficherPopupCreationSalon() {
    let popupInscription = document.querySelector(".popup-créer-salon")
    popupInscription.classList.add("active")
}

function cacherPopupCreationSalon() {
    let popupInscription = document.querySelector(".popup-créer-salon")
    popupInscription.classList.remove("active")
}

function afficherPopupRejoidreSalon() {
    let popupInscription = document.querySelector(".popup-rejoindre-salon")
    popupInscription.classList.add("active")
}

function cacherPopupRejoidreSalon() {
    let popupInscription = document.querySelector(".popup-rejoindre-salon")
    popupInscription.classList.remove("active")
}

function validateRoomCreation() {
    let playerNumber = document.getElementById("player-number")
    let musicNumber = document.getElementById("music-number")

    playerNumber.addEventListener("keyup", () => {
        if (playerNumber.value < 1 || playerNumber.value > 20) {
            playerNumber.setCustomValidity("Le nombre de joueur ne peut être inferieur à 2 ou supérieur à 10")
        }
        else {
            playerNumber.setCustomValidity("")
        }
    })

    musicNumber.addEventListener("keyup", () => {
        if (musicNumber.value < 1 || musicNumber.value > 20) {
            console.log("bijour")
            musicNumber.setCustomValidity("Le nombre de music ne peut être inferieur à 1 ou supérieur à 20")
        }
        else {
            musicNumber.setCustomValidity("")
        }
    })
}

function initAddEventListenerPopupCreationSalon() {
    btnInscription = document.getElementById("créer-salon")
    let popupBackground = document.querySelector(".popup-créer-salon")
    if (btnInscription != null) {
        btnInscription.addEventListener("click", () => {
            afficherPopupCreationSalon()
        })

        popupBackground.addEventListener("click", (event) => {
            if (event.target === popupBackground)
                cacherPopupCreationSalon()
        })
    }
}

function initAddEventListenerPopupRejoindreSalon() {
    btnInscription = document.getElementById("rejoindre-salon")
    let popupBackground = document.querySelector(".popup-rejoindre-salon")
    if (btnInscription != null) {
        btnInscription.addEventListener("click", () => {
            afficherPopupRejoidreSalon()

        })

        popupBackground.addEventListener("click", (event) => {
            if (event.target === popupBackground)
                cacherPopupRejoidreSalon()
        })
    }
}

function checkPlayerNumber(playerNumber) {
    if (playerNumber <= 1 || playerNumber > 10) {
        return false
    }
    return true
}

function checkMusicNumber(musicNumber) {
    if (musicNumber < 1 || musicNumber > 20) {
        return false
    }
    return true
}


initAddEventListenerPopupCreationSalon()
initAddEventListenerPopupRejoindreSalon()


function mobileNavbarDisplay(){
    navbarBtn = document.getElementById("navbar-button")
    isOpen = false
    navbarBtn.addEventListener("click", () =>{
        mobileNavbar = document.querySelector(".mobile-navbar")
        if (!isOpen){
            mobileNavbar.style.display = 'block'

            isOpen = true
        } else{
            mobileNavbar.style.display = 'none'
            isOpen = true
        }
    })
}

mobileNavbarDisplay()