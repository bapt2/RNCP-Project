navbarBtnOpen = document.getElementById("navbar-button-open")
navbarBtnClose = document.getElementById("navbar-button-close")
isOpen = false

function handleResize() {
    if (window.matchMedia("(min-width: 997px)").matches) {
        resetMobileNavBar()
    }
}

function resetMobileNavBar() {
    header = document.querySelector(".title-nav-connection")
    mobileNavbar = document.querySelector(".mobile-navbar")
    signInLogIn = document.querySelector(".sign-in-log-in")
    headerh1 = document.querySelector(".title-nav-connection h1")
    leftSection = document.querySelector(".left-section")
    account = document.querySelector(".sign-in-log-in #compte")
    if (isOpen) {
        if (leftSection != null) {
            leftSection.style.height = '90vh'
        }
        if (account){
            account.style.marginTop = "12px"
        }
        navbarBtnOpen.style.display = 'flex'
        mobileNavbar.style.display = 'none'
        header.style.paddingBottom = '60px'
        signInLogIn.style.top = '0.5%'
        headerH1.style.top = '1%'
        isOpen = false
    }
}

function handleHeaderBorder() {
    mobileNavbar = document.querySelector(".mobile-navbar")
    const linksCount = mobileNavbar.querySelectorAll('a').length
    header = document.querySelector(".title-nav-connection")
    let paddingBottom = 60 + (linksCount * 21)
    header.style.paddingBottom = `${paddingBottom}px`
}

function mobileNavbarDisplay() {

    const formElement = document.querySelectorAll('input, textarea, select')
    if (formElement.length > 0) {
        formElement.forEach(element => {
            element.addEventListener("click", () => {
                if (isOpen) {
                    resetMobileNavBar()
                }
            })
        })
    }

    mobileNavbar = document.querySelector(".mobile-navbar")
    navbarBtnOpen.addEventListener("click", (e) => {
        headerH1 = document.querySelector(".title-nav-connection h1")
        signInLogIn = document.querySelector(".sign-in-log-in")
        leftSection = document.querySelector(".left-section")
        account = document.querySelector(".sign-in-log-in #compte")
        if (!isOpen) {
            handleHeaderBorder()
            if (leftSection != null) {
                leftSection.style.height = '80vh'
            }
            if (account){
                account.style.marginTop = "20px"
                headerH1.style.top = '5%'
            }
            mobileNavbar.style.display = 'block'
            navbarBtnOpen.style.display = 'none'
            signInLogIn.style.top = '3.5%'
            headerH1.style.top = '4.5%'
            isOpen = true
        }
        e.stopPropagation()
    })

    navbarBtnClose.addEventListener("click", () => {
        resetMobileNavBar()
    })

    mobileNavbar.addEventListener("click", (e) => {
        if (isOpen) {
            e.stopPropagation()
        }
    })

    document.addEventListener("click", () => {
        if (isOpen) {
            resetMobileNavBar()
        }
    })

}

window.addEventListener('resize', handleResize)
handleResize()
mobileNavbarDisplay()