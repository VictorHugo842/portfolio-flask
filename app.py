from flask import Flask, render_template, redirect, request, flash, jsonify
from flask_mail import Mail, Message
from contato import Contato
from dotenv import load_dotenv
import os
import requests
import logging

load_dotenv()

# cria a instância do aplicativo Flask
app = Flask(__name__)

app.secret_key = "64bit"

mail_settings = {
	"MAIL_SERVER":"smtp.gmail.com",
	"MAIL_PORT":465,
	"MAIL_USE_TLS": False,
	"MAIL_USE_SSL": True,
	"MAIL_USERNAME": os.getenv("EMAIL"), 
	"MAIL_PASSWORD":os.getenv("PASSWORD")
}

#tentaasorte -> remember

app.config.update(mail_settings)
mail = Mail(app)

# configura o nível de log para DEBUG(debug, error, info, warning, critical)
app.logger.setLevel(logging.DEBUG)

# toda rota é seguida de uma função
@app.route("/")
def index():
	return render_template("index.html")

# envio de e-mail
@app.route("/send", methods=["GET","POST"])
def send():
	if request.method == "POST":
		# chama função que atribui as variavéis recebido do form
		formContato = Contato(
			request.form["nome"],
			request.form["email"],
			request.form["mensagem"]
		)

		# mensagem formata em f-string
		msg = Message(
			subject = f'{formContato.nome} te enviou uma mensagem através do portfólio.',
			sender = app.config.get("MAIL_USERNAME"),
			recipients=["victor99.santos@gmail.com","giovana99.fagundes@gmail.com"],
			body = f'''O usuário {formContato.nome} com o e-mail {formContato.email} te enviou a seguinte mensagem:

			{formContato.mensagem}
			'''
		)
		
		# envio
		mail.send(msg)
		flash("Mensagem enviada com sucesso!")
	return redirect("/")


# verifica se o script está sendo executado diretamente
if __name__ == "__main__":
	# inicia o servidor Flask em modo dev
	app.run(debug=True)
