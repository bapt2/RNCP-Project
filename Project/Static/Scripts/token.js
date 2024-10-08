window.onload = function() {
    const hash = window.location.hash.substring(1)
    const tokenParam = hash.split('&').find(elem => elem.startsWith('access_token'))
    if (tokenParam) {
        access_token = tokenParam.split('=')[1]

        sessionStorage.setItem('spotify_access_token', access_token)

        fetch('store_token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token: access_token })
        }).then(response => {
            if (response.ok) {
                window.location.href = "/jeu"
            } else { console.error('Failed to store access token') }
        })
    } else {
        console.error('Access token not found in the url')
    }
}
