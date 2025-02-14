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
        if (body.classList.contains("menu-nav-active")) {
            body.classList.remove("menu-nav-active");
            menuMobile.classList.replace("bi-x", "bi-list");
        }
    })
});

/* animação dos itens com o atributo data anime */
const item = document.querySelectorAll("[data-anime]");

const animeScroll = () => {
    const windowTop = window.pageYOffset + window.innerHeight * 0.85;

    item.forEach(element => {
        if (windowTop > element.offsetTop) {
            element.classList.add("animate");
        } else {
            element.classList.remove("animate");
        }
    })
};

animeScroll();

window.addEventListener("scroll", () => {
    animeScroll();
});

// muda botão de enviar para botão de carregamento após a validação do reCAPTCHA
const btnEnviar = document.querySelector("#btn-enviar");
const btnEnviarLoader = document.querySelector("#btn-enviar-loader");
const form = document.querySelector("#form-contato");

form.addEventListener("submit", (event) => {
    event.preventDefault(); // impede o envio padrão para usar AJAX

    // verifica a validade do formulário
    if (!form.checkValidity()) {
        event.stopPropagation();
    } else {
        // verifica se o reCAPTCHA foi completado
        var recaptchaResponse = grecaptcha.getResponse();
        if (recaptchaResponse.length === 0) {
            alert("Por favor, complete a verificação do reCAPTCHA.");
        } else {
            // altera o botão para mostrar "enviando" e oculta o botão "enviar", também da como validado os campos do form
            btnEnviarLoader.style.display = "block";
            btnEnviar.style.display = "none";
            form.classList.add('was-validated');

            // faz a requisição AJAX
            const formData = new FormData(form);
            formData.append("g-recaptcha-response", recaptchaResponse); // adiciona o reCAPTCHA ao formData

            fetch("/send", {
                method: "POST",
                body: formData,
            })
            .then(response => response.json()) // recebe a resposta em JSON
            .then(data => {

                // exibe a mensagem de feedback
                const alerta = document.createElement("div");
                alerta.classList.add("alert", "alert-dismissible", "fade", "show", data.category);
                alerta.setAttribute("role", "alert");
                alerta.innerHTML = `<i class="bi bi-${data.icon} me-1"></i> ${data.message}`;

                // exibe a mensagem na tela no canto inferior
                document.body.appendChild(alerta);
                alerta.style.position = "fixed";
                alerta.style.bottom = "20px";
                alerta.style.left = "50%";
                alerta.style.transform = "translateX(-50%)";
                alerta.style.zIndex = 1050;

                // faz o alerta desaparecer após 5 segundos
                setTimeout(() => {
                    alerta.classList.remove("show");
                    setTimeout(() => {
                        alerta.remove(); // remove o alerta após o fade-out
                    }, 150);
                }, 3000);

                // reseta o formulário, reCAPTCHA e os botões
                form.reset();
                grecaptcha.reset(); // reseta o reCAPTCHA
                btnEnviarLoader.style.display = "none";
                btnEnviar.style.display = "block";
                form.classList.remove('was-validated'); // remove a classe de validação evita que os campos não fiquem vermelhos
            })
            .catch(error => {
                console.error("Erro:", error);
                alert("Ocorreu um erro, tente novamente mais tarde.");
                btnEnviarLoader.style.display = "none";
                btnEnviar.style.display = "block";
            });
        }
    }
});
