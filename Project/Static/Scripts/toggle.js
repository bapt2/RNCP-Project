const toggleSwitch = document.getElementById('toggleSwitch')
const statusLabel = document.getElementById('status')

function loadTheme(){
    fetch('/get-theme')
    .then(response => response.json())
    .then(data =>{
        if (data.theme){
            if (data.theme ==='night') {
                document.body.classList.add('night-mode')
                if (toggleSwitch != null) {
                    toggleSwitch.checked = true
                    statusLabel.textContent = 'Nuit'
                }
            } else{
                document.body.classList.remove('night-mode')
                if (toggleSwitch != null) {
                    toggleSwitch.checked = false
                    statusLabel.textContent = 'Jour'
                }
            }
        } else{
            console.error("Erreur lors de la récupération du thème");
        }
    })
    .catch(error =>{
        console.error("Erreur de réseau: ", error);
    })
}

let debounceTimer

function debounceSaveTheme(theme){
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() =>{
        fetch('/save-theme',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({theme: theme}),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Préférence de thème sauvegarder:', data)
        })
        .catch(error =>{
            console.error('Erreur lors de la sauvegarde de la préference:', error);
            
        });
    }, 500)
}

if (toggleSwitch != null) {
    toggleSwitch.addEventListener('change', () =>{
        const theme = toggleSwitch.checked ? 'night' : 'day'
    
        if (toggleSwitch.checked){
            document.body.classList.add('night-mode')
            statusLabel.textContent = 'Nuit'        
        } else{
            document.body.classList.remove('night-mode')
            statusLabel.textContent = 'Jour'
        }
    
        debounceSaveTheme(theme)
    })
}

document.addEventListener('DOMContentLoaded', loadTheme)