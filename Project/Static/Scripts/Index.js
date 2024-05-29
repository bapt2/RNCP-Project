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

function initAddEventListenerPopupCreationSalon() {
    btnInscription = document.getElementById("créer-salon")
    let popupBackground = document.querySelector(".popup-créer-salon")
    if (btnInscription != null){
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
    if (btnInscription != null){
        btnInscription.addEventListener("click", () => {
            afficherPopupRejoidreSalon()
        })
    
        popupBackground.addEventListener("click", (event) => {
            if (event.target === popupBackground)
                cacherPopupRejoidreSalon()
        })
    }
}

initAddEventListenerPopupCreationSalon()
initAddEventListenerPopupRejoindreSalon()