from flask import Flask, render_template, request, session, redirect
from config import NOME_SISTEMA, VERSAO
from firebase import iniciar_firebase
from datetime import datetime, timedelta

app = Flask(__name__)

app.secret_key = "BarberFlow2026"

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
        "barba": 15,
        "corte_barba_pigmentacao": 65
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
            configuracao["corte"] = int(doc.get("corte", 30))

            configuracao["pigmentacao"] = int(doc.get("pigmentacao", 60))

            configuracao["corte_barba"] = int(doc.get("corte_barba", 40))

            configuracao["corte_sobrancelha"] = int(doc.get("corte_sobrancelha", 35))

            configuracao["barba"] = int(doc.get("barba", 15))

            configuracao["corte_barba_pigmentacao"] = int(
               doc.get("corte_barba_pigmentacao", 65)
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

            ag["id"] = item.id

            lista.append(ag)


    # Ordenar por data e horário
    lista.sort(
        key=lambda x: datetime.strptime(
            f"{x.get('data')} {x.get('hora')}",
            "%d/%m/%Y %H:%M"
        )
    )


    return lista


@app.route("/")
def inicio():

    return render_template(
        "index.html"
    )
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        senha = request.form["senha"]

        if senha == "019283":

            session["admin"] = True

            return redirect("/admin")

        else:

            return """
            <h2>❌ Senha incorreta</h2>
            <a href="/login">Tentar novamente</a>
            """

    return """
    <h2>🔒 Login Administrativo</h2>

    <form method="POST">

        <input 
        type="password" 
        name="senha"
        placeholder="Senha">

        <button>
        Entrar
        </button>

    </form>
    """


@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect("/login")
    

@app.route("/admin")
def admin():

    if "admin" not in session:
        return redirect("/login")

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

    todos_agendamentos = listar_agendamentos()

    hoje = datetime.now().date()

    limite = hoje + timedelta(
        days=config["semanas_agenda"] * 7
    )

    agendamentos = []

    for ag in todos_agendamentos:

        data_ag = datetime.strptime(
            ag["data"],
            "%d/%m/%Y"
        ).date()

        if hoje <= data_ag <= limite:
            agendamentos.append(ag)


    return render_template(
    "agenda.html",
    agendamentos=agendamentos,
    inicio_expediente=config["inicio_expediente"],
    fim_expediente=config["fim_expediente"],
    semanas_agenda=config["semanas_agenda"],
    config=config,
    session=session
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
                "corte": int(corte),
                "pigmentacao": int(pigmentacao),
                "corte_barba": int(corte_barba),
                "corte_sobrancelha": int(corte_sobrancelha),
                "barba": int(barba),
                "corte_barba_pigmentacao": int(corte_barba_pigmentacao)

            })

            encontrado = True


        if not encontrado:

            db.collection("configuracoes").add({

                "inicio_expediente": inicio,
                "fim_expediente": fim,
                "semanas_agenda": semanas,
                "corte": int(corte),
                "pigmentacao": int(pigmentacao),
                "corte_barba": int(corte_barba),
                "corte_sobrancelha": int(corte_sobrancelha),
                "barba": int(barba),
                "corte_barba_pigmentacao": int(corte_barba_pigmentacao)

            })


    return '''
    <h2>✅ Configurações salvas!</h2>
    <a href="/admin">Voltar</a>
    '''

@app.route("/editar_agendamento/<id>")
def editar_agendamento(id):

    if "admin" not in session:
        return redirect("/login")

    agendamento = db.collection("agendamentos").document(id).get()

    if agendamento.exists:

        dados = agendamento.to_dict()

        dados["id"] = id

        return render_template(
            "editar.html",
            agendamento=dados
        )

    return "Agendamento não encontrado"
@app.route("/salvar_edicao/<id>", methods=["POST"])
def salvar_edicao(id):

    if "admin" not in session:
        return redirect("/login")

    nome = request.form["nome"]
    servico = request.form["servico"]
    data = request.form["data"]
    hora = request.form["hora"]
    duracao = request.form["duracao"]


    data_obj = datetime.strptime(
        data,
        "%Y-%m-%d"
    )

    data = data_obj.strftime(
        "%d/%m/%Y"
    )


    novo_inicio = datetime.strptime(
        f"{data} {hora}",
        "%d/%m/%Y %H:%M"
    )


    novo_fim = novo_inicio + timedelta(
        minutes=int(duracao)
    )


    existentes = listar_agendamentos()


    for ag in existentes:

        if ag["id"] != id and ag.get("data") == data:


            inicio_existente = datetime.strptime(
                f"{ag['data']} {ag['hora']}",
                "%d/%m/%Y %H:%M"
            )


            fim_existente = inicio_existente + timedelta(
                minutes=int(ag.get("duracao", 30))
            )


            if novo_inicio < fim_existente and novo_fim > inicio_existente:

                return """
                <h2>❌ Horário ocupado!</h2>
                <p>Esse horário já possui outro atendimento.</p>
                <a href="/agenda">Voltar</a>
                """


    if db:

        db.collection("agendamentos").document(id).update({

            "nome": nome,
            "servico": servico,
            "data": data,
            "hora": hora,
            "duracao": int(duracao)

        })


    return redirect("/agenda")
    
@app.route("/cancelar_agendamento/<id>")
def cancelar_agendamento(id):

    if "admin" not in session:
        return redirect("/login")

    if db:

        db.collection("agendamentos").document(id).delete()

    return redirect("/agenda")
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
