from flask import Flask, render_template, redirect, request, flash, jsonify
from flask_mail import Mail, Message
from contato import Contato
from dotenv import load_dotenv
import os
import requests
load_dotenv()
import logging

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

# @app.route("/geolocalizacao", methods=["GET"])
# def geolocalizacao():

# 	if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
# 		user_ip = request.environ['REMOTE_ADDR']
# 	else:
# 		user_ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()

# 	token = os.getenv("USERLOCATION")
# 	ip_address = request.args.get('ip', user_ip)
	
# 	headers = {
# 		'Authorization': f'Bearer {token}',
# 		'Content-Type': 'application/json'
# 	}

# 	# faz a requisição à API de geolocalização
# 	url = f"https://api.invertexto.com/v1/geoip/{ip_address}"
# 	response = requests.get(url, headers=headers)

# 	#app.logger.debug(f"Status Code: {response.status_code}")
# 	#app.logger.debug(f"Response Text: {response.text}")

# 	if response.status_code == 200:
# 		data = response.json()  # converte a resposta em JSON
# 		return jsonify(data)  # retorna os dados em formato JSON
# 	else:
# 		return response.text

@app.route('/geolocalizacao', methods=['POST','GET'])
def receive_location():
	return render_template("teste.html")

	# print(request)

	# data = request.get_json()
	# latitude = data.get('latitude')
	# longitude = data.get('longitude')

	# if latitude is None or longitude is None:
	# 	return jsonify({'error': 'Latitude and Longitude are required'}), 400

	# # Processar a localização conforme necessário
	# response = {
	# 	'message': 'Location received',
	# 	'latitude': latitude,
	# 	'longitude': longitude
	# }
	# return jsonify(response), 200


# verifica se o script está sendo executado diretamente
if __name__ == "__main__":
	# inicia o servidor Flask em modo dev
	app.run(debug=True)
