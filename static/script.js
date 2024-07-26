/* menu lateral responsivo */

const menuMobile = document.querySelector(".menu-mobile")
const body = document.querySelector("body")


menuMobile.addEventListener('click', () => {
    menuMobile.classList.contains("bi-list")
    ? menuMobile.classList.replace("bi-list","bi-x") /* if */
    : menuMobile.classList.replace("bi-x","bi-list"); /* else */

    body.classList.toggle("menu-nav-active") /* volta o header */
})
