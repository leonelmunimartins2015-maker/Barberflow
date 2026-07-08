from flask import Flask, render_template, request
from config import NOME_SISTEMA, VERSAO

app = Flask(__name__)


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/clientes")
def clientes():
    return render_template("clientes.html")


@app.route("/cadastrar_cliente", methods=["POST"])
def cadastrar_cliente():

    nome = request.form["nome"]
    telefone = request.form["telefone"]

    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Cliente cadastrado</title>
    </head>

    <body style="background:#111;color:white;text-align:center;font-family:Arial">

        <h1>✅ Cliente cadastrado!</h1>

        <p>Nome: {nome}</p>
        <p>Telefone: {telefone}</p>

        <br>

        <a href="/clientes" style="color:#c89b3c">
            Voltar para clientes
        </a>

    </body>
    </html>
    """


@app.route("/teste")
def teste():
    return {
        "sistema": NOME_SISTEMA,
        "versao": VERSAO,
        "status": "online"
    }


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
