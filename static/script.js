/* abre e fecha o menu lateral */
const menuMobile = document.querySelector(".menu-mobile");
const body = document.querySelector("body");

menuMobile.addEventListener('click', () => {
    menuMobile.classList.contains("bi-list")
        ? menuMobile.classList.replace("bi-list", "bi-x") /* if */
        : menuMobile.classList.replace("bi-x", "bi-list"); /* else */
    body.classList.toggle("menu-nav-active"); /* volta o menu */
});


/* desabilita menu ao clicar em item e muda icone para list */ 
const navItem = document.querySelectorAll(".nav-item");

navItem.forEach(item => {
    item.addEventListener("click", () => {
        if(body.classList.contains("menu-nav-active")){
            body.classList.remove("menu-nav-active");
            menuMobile.classList.replace("bi-x","bi-list");
        }
    })
})

/* animação dos itens com o atributo data anime */
const item = document.querySelectorAll("[data-anime]");

const animeScroll = () => {
    /* pega o topo de acordo com a tela */
    const windowTop = window.pageYOffset + window.innerHeight * 0.85;

    item.forEach(element => {
        if (windowTop > element.offsetTop){
            element.classList.add("animate");
        }else{
            element.classList.remove("animate");
        }
    })
}

animeScroll()

window.addEventListener("scroll", () => {
    animeScroll();
})