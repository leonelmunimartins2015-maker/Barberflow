from flask import Flask, render_template, request
from config import NOME_SISTEMA, VERSAO
from firebase import iniciar_firebase
from datetime import datetime

app = Flask(__name__)

db = iniciar_firebase()


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/clientes")
def clientes():
    return render_template("clientes.html")


@app.route("/lista_clientes")
def lista_clientes():

    clientes = []

    if db:
        dados = db.collection("clientes").stream()

        for cliente in dados:
            clientes.append(cliente.to_dict())

    return render_template(
        "lista_clientes.html",
        clientes=clientes
    )


@app.route("/cadastrar_cliente", methods=["POST"])
def cadastrar_cliente():

    nome = request.form["nome"]
    telefone = request.form["telefone"]

    if db:
        db.collection("clientes").add({
            "nome": nome,
            "telefone": telefone,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M")
        })

        mensagem = "Cliente salvo no Firebase!"

    else:
        mensagem = "Firebase não conectado."


    return f"""
    <h1>💈 {mensagem}</h1>
    <p>Nome: {nome}</p>
    <p>Telefone: {telefone}</p>
    <br>
    <a href="/clientes">Voltar</a>
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
