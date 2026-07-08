from flask import Flask, render_template, request
from config import NOME_SISTEMA, VERSAO
from firebase import iniciar_firebase
from datetime import datetime, timedelta

app = Flask(__name__)

db = iniciar_firebase()


def pegar_configuracao():

    configuracao = {
        "inicio_expediente": "11:00",
        "fim_expediente": "18:00",
        "semanas_agenda": 2,
        "corte": 30,
        "pigmentacao": 60,
        "corte_barba": 40,
        "corte_sobrancelha": 35,
        "barba": 15
    }

    if db:

        dados = db.collection("configuracoes").limit(1).stream()

        for item in dados:

            doc = item.to_dict()

            configuracao["inicio_expediente"] = doc.get(
                "inicio_expediente",
                "11:00"
            )

            configuracao["fim_expediente"] = doc.get(
                "fim_expediente",
                "18:00"
            )

            configuracao["semanas_agenda"] = int(
                doc.get("semanas_agenda", 2)
            )

    return configuracao


def listar_clientes():

    lista = []

    if db:

        dados = db.collection("clientes").stream()

        for item in dados:

            lista.append(item.to_dict())

    return lista



def listar_agendamentos():

    lista = []

    if db:

        dados = db.collection("agendamentos").stream()

        for item in dados:

            ag = item.to_dict()

            lista.append(ag)

    return lista



@app.route("/")
def inicio():

    return render_template(
        "index.html"
    )

@app.route("/admin")
def admin():

    config = pegar_configuracao()

    return render_template(
        "admin.html",
        config=config
    )



@app.route("/clientes")
def clientes():

    return render_template(
        "clientes.html"
    )



@app.route("/lista_clientes")
def lista_clientes():

    return render_template(
        "lista_clientes.html",
        clientes=listar_clientes()
    )

@app.route("/agenda")
def agenda():

    config = pegar_configuracao()

    agendamentos = listar_agendamentos()


    return render_template(
        "agenda.html",
        agendamentos=agendamentos,
        inicio_expediente=config["inicio_expediente"],
        fim_expediente=config["fim_expediente"],
        semanas_agenda=config["semanas_agenda"]
    )



@app.route("/cadastrar_cliente", methods=["POST"])
def cadastrar_cliente():

    nome = request.form["nome"]
    telefone = request.form["telefone"]


    if db:

        db.collection("clientes").add({

            "nome": nome,
            "telefone": telefone,
            "data": datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            )

        })

        mensagem = "Cliente salvo no Firebase!"

    else:

        mensagem = "Firebase não conectado."



    return f"""

    <h1>💈 {mensagem}</h1>

    <p>Nome: {nome}</p>
    <p>Telefone: {telefone}</p>

    <br>

    <a href="/clientes">
    Voltar
    </a>

    """



@app.route("/cadastrar_agendamento", methods=["POST"])
def cadastrar_agendamento():

    nome = request.form["nome"]

    servico = request.form["servico"]

    data_original = request.form["data"]


    data_obj = datetime.strptime(
        data_original,
        "%Y-%m-%d"
    )


    data = data_obj.strftime(
        "%d/%m/%Y"
    )


    hora = request.form["hora"]

    duracao = int(
        request.form["duracao"]
    )


    novo_inicio = datetime.strptime(
        f"{data} {hora}",
        "%d/%m/%Y %H:%M"
    )


    novo_fim = novo_inicio + timedelta(
        minutes=duracao
    )


    if db:

        existentes = listar_agendamentos()


        for ag in existentes:


            if ag.get("data") == data:


                inicio_existente = datetime.strptime(
                    f"{ag['data']} {ag['hora']}",
                    "%d/%m/%Y %H:%M"
                )


                fim_existente = (
                    inicio_existente +
                    timedelta(
                        minutes=int(
                            ag.get("duracao", 30)
                        )
                    )
                )


                if novo_inicio < fim_existente and novo_fim > inicio_existente:


                    return """

                    <h1>❌ Horário ocupado!</h1>

                    <p>
                    Já existe atendimento nesse período.
                    </p>

                    <a href="/agenda">
                    Voltar
                    </a>

                    """



        db.collection("agendamentos").add({

            "nome": nome,
            "servico": servico,
            "data": data,
            "hora": hora,
            "duracao": duracao

        })


        mensagem = "Agendamento salvo!"


    else:

        mensagem = "Firebase não conectado."

    return f"""

    <h1>💈 {mensagem}</h1>

    <p>Cliente: {nome}</p>
    <p>Serviço: {servico}</p>
    <p>Data: {data}</p>
    <p>Horário: {hora}</p>
    <p>Duração: {duracao} minutos</p>

    <br>

    <a href="/agenda">
    Voltar para agenda
    </a>

    """



@app.route("/teste")
def teste():

    return {

        "sistema": NOME_SISTEMA,
        "versao": VERSAO,
        "status": "online"

    }

@app.route("/salvar_configuracoes", methods=["POST"])
def salvar_configuracoes():

    inicio = request.form["inicio_expediente"]
    fim = request.form["fim_expediente"]
    semanas = int(request.form["semanas_agenda"])

    corte = request.form["corte"]
    pigmentacao = request.form["pigmentacao"]
    corte_barba = request.form["corte_barba"]
    corte_sobrancelha = request.form["corte_sobrancelha"]
    barba = request.form["barba"]
    corte_barba_pigmentacao = request.form["corte_barba_pigmentacao"]

    if db:

        docs = db.collection("configuracoes").limit(1).stream()

        encontrado = False

        for doc in docs:
                    
            db.collection("configuracoes").document(doc.id).update({
                "inicio_expediente": inicio,
                "fim_expediente": fim,
                "semanas_agenda": semanas,
                "corte": corte,
                "pigmentacao": pigmentacao,
                "corte_barba": corte_barba,
                "corte_sobrancelha": corte_sobrancelha,
                "barba": barba,
                "corte_barba_pigmentacao": corte_barba_pigmentacao
            })

            encontrado = True

        if not encontrado:
            db.collection("configuracoes").add({
                "inicio_expediente": inicio,
                "fim_expediente": fim,
                "semanas_agenda": semanas,
                "corte": corte,
                "pigmentacao": pigmentacao,
                "corte_barba": corte_barba,
                "corte_sobrancelha": corte_sobrancelha,
                "barba": barba
            })

    return '''
    <h2>✅ Configurações salvas!</h2>
    <a href="/admin">Voltar</a>
    '''


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
