function validateConnection() {
    let btnConnection = document.getElementById("connection-validate")

    let email = document.getElementById("email-log-in")
    let mdp = document.getElementById("password-log-in")

    email.addEventListener("keyup", () => {
        if (!validerEmail(email.value)) {
            email.setCustomValidity("email invalide, par example: exemple@gmail.com")
        }
        else {
            email.setCustomValidity("")
        }
    })

    mdp.addEventListener("keyup", () =>{
        if (!validerMdp(mdp.value)){
            mdp.setCustomValidity("mot de passe invalide, doit avoir au minimum 8 character")
        }
        else{
            mdp.setCustomValidity("")
        }
    })
    
    btnConnection.addEventListener("submit", (event) => {
        event.defaultPrevented()

        validerMdp(mdp)
        validerEmail(email.value)
    })
}


function validerNom(nom) {
    if (nom.length < 2) {
        return false
    }
    return true
}

function validerEmail(email) {
    let regex = new RegExp("[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\\.[a-zA-Z0-9._-]+")
    if (regex.test(email)) {
        return true
    }
    return false
}

function validerMdp(mdp) {
    if (mdp.length < 8) {
        return false
    }
    return true
}

validateConnection()