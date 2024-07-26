from flask import Flask, render_template, redirect

# cria a instância do aplicativo Flask
app = Flask(__name__)

# toda rota é seguida de uma função
@app.route("/")
def index():
	return render_template("index.html")

# verifica se o script está sendo executado diretamente
if __name__ == "__main__":
	# inicia o servidor Flask em modo dev
	app.run(debug=True)
