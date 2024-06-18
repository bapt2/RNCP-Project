function validatesignin() {
    let btnSignin = document.getElementById("inscription-validate")

    let nom = document.getElementById("pseudo")
    let email = document.getElementById("email-inscription")
    let mdp = document.getElementById("password-inscription")

    nom.addEventListener("keyup", () => {
        if (!validerNom(nom.value)) {
            nom.setCustomValidity("nom invalide, doit avoir 2 character au minimum")
        }
        else {
            nom.setCustomValidity("")
        }
    })

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

validatesignin()