from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
import re
import logging
import requests
import bleach

# carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "64bit")

# configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# configuração do Flask-Mail
app.config.update({
    "MAIL_SERVER": "smtp.gmail.com",
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.getenv("EMAIL"),
    "MAIL_PASSWORD": os.getenv("PASSWORD")  # 2fa senha do app google
})
mail = Mail(app)

# configuração do Flask-Limiter para evitar spam
limiter = Limiter(get_remote_address, app=app)

# sanitização dos campos de texto
def sanitizar_entrada(texto):
    """Sanitiza o texto removendo qualquer conteúdo potencialmente malicioso."""
    return bleach.clean(texto, tags=[], attributes={}, strip=True)  # Usar strip=True para maior segurança

# validação do e-mail
def validar_email(email):
    """Valida o formato do e-mail usando uma regex mais robusta."""
    regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if re.match(regex, email):
        return True
    return False

# verifica e-mail temporário
def email_temporario(email):
    """Verifica se o e-mail pertence a um serviço temporário."""
    try:
        response = requests.get(f"https://open.kickbox.com/v1/disposable/{email}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("disposable", False)
        else:
            logger.error(f"Erro ao verificar e-mail temporário: Código de status {response.status_code}")
            return False
    except requests.RequestException as e:
        logger.error(f"Erro ao verificar e-mail temporário: {e}")
        return False

def validar_recaptcha(response):
    """Valida o reCAPTCHA v2."""
    secret_key = os.getenv("RECAPTCHA_SECRET_KEY")
    if not secret_key:
        logger.error("Chave secreta do reCAPTCHA não configurada.")
        return False
    
    payload = {"secret": secret_key, "response": response}
    
    try:
        # requisição ao Google para validar o reCAPTCHA
        r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload, timeout=10) 
        r.raise_for_status()  # verifica se a requisição foi bem-sucedida (status 2xx)
        
        # valida a resposta
        result = r.json()
        
        if result.get("success"):
            logger.info("reCAPTCHA validado com sucesso.")
            return True
        else:
            # se não for válido, loga a mensagem de erro
            logger.warning(f"Falha na validação do reCAPTCHA: {result.get('error-codes', 'sem erro específico')}")
            return False
    
    except requests.exceptions.Timeout:
        logger.error("Erro: tempo de conexão com o reCAPTCHA excedido.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao validar reCAPTCHA: {e}")
    
    return False

# @app.before_request
# def before_request():
#    pass
    

@app.after_request
def after_request(response):
    
    # adiciona cabeçalhos de segurança para prevenir XSS, ataques clickjacking e MITM
    response.headers['X-Content-Type-Options'] = 'nosniff'  # previne que o navegador "adivinhe" o tipo de conteúdo
    response.headers['X-XSS-Protection'] = '1; mode=block'   # ativa a proteção contra ataques XSS
    response.headers['X-Frame-Options'] = 'DENY'             # impede que a página seja carregada dentro de um iframe
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'  # força o uso de HTTPS

    return response
    

@app.route("/")
def index():
    site_key = os.getenv("RECAPTCHA_SITE_KEY")  # reCAPTCHA
    return render_template("index.html", site_key=site_key)

# ajax para enviar o contato
@app.route("/send", methods=["POST"])
@limiter.limit("5 per minute")  # limite de 5 requisições por minuto
def send():
    try:
        nome = sanitizar_entrada(request.form.get("nome", "").strip())
        email = sanitizar_entrada(request.form.get("email", "").strip())
        mensagem = sanitizar_entrada(request.form.get("mensagem", "").strip())
        recaptcha_response = request.form.get("g-recaptcha-response")  # validação reCAPTCHA
        
        # validações
        if not nome or not email or not mensagem:
            # são campos required, porém, valida no back-end também
            logger.warning("Campos obrigatórios não preenchidos")
            return jsonify({"message": "Todos os campos são obrigatórios", "category": "alert-danger", "icon": "exclamation-triangle-fill"}), 400

        # limite de caracteres
        if len(mensagem) > 500:
            logger.warning(f"Limite de caracteres de 500 excedido para mensagem: {email}")
            return jsonify({"message": "Limite de caracteres excedido para o campo de mensagem", "category": "alert-danger", "icon": "exclamation-triangle-fill"}), 400

        if not validar_email(email):
            logger.warning(f"E-mail inválido: {email}")
            return jsonify({"message": "E-mail inválido", "category": "alert-danger", "icon": "exclamation-triangle-fill"}), 400

        if email_temporario(email):
            logger.warning(f"E-mail temporário detectado: {email}")
            return jsonify({"message": "E-mails temporários não são permitidos", "category": "alert-danger", "icon": "exclamation-triangle-fill"}), 400

        if not validar_recaptcha(recaptcha_response):
            logger.warning("Falha na verificação reCAPTCHA")
            return jsonify({"message": "Verificação reCAPTCHA falhou", "category": "alert-danger", "icon": "exclamation-triangle-fill"}), 400

        recipients = os.getenv("RECIPIENTS", "").split(",")

        msg = Message(
            subject=f"Nova mensagem de {nome}",
            sender=app.config.get("MAIL_USERNAME"),
            recipients=recipients,
            body=f"""
            Mensagem recebida do portfólio! 💬

            Nome: {nome}
            E-mail: {email}

            Mensagem:
            {mensagem}
            """
        )

        try:
            mail.send(msg)
            logger.info(f"Mensagem enviada com sucesso de {nome} ({email})")
            return jsonify({"message": "Mensagem enviada com sucesso", "category": "alert-success", "icon": "check-circle-fill"}), 200
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem de {nome} ({email}): {e}")
            return jsonify({"message": f"Erro ao enviar a mensagem. Tente novamente mais tarde. Erro: {e}", "category": "alert-danger", "icon": "exclamation-triangle-fill"}), 500

    except Exception as e:
        logger.error(f"Erro ao processar requisição: {e}")
        return jsonify({"message": "Você atingiu o limite de envio. Tente novamente em um minuto.", "category": "alert-warning", "icon": "exclamation-triangle-fill"}), 429

if __name__ == "__main__":
    app.run(debug=True)
