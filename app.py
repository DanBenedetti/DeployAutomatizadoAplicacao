from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from datetime import date
import os

app = Flask(__name__)
app.secret_key = 'umsegredoforteaqui'  # Altere para sua chave de sessão forte

# Função para converter TIME (timedelta) do MySQL para "HH:MM"
def formatar_horario_mysql(time_value):
    if time_value is None:
        return ""
    try:
        # Se já for string, apenas retorna os 5 primeiros caracteres
        if isinstance(time_value, str):
            return time_value[:5]
        # Se for timedelta: converte para HH:MM
        total_seconds = int(time_value.total_seconds())
        horas = total_seconds // 3600
        minutos = (total_seconds % 3600) // 60
        return f"{horas:02d}:{minutos:02d}"
    except Exception:
        return str(time_value)

# Configuração do Banco de Dados (agora compatível com Docker)
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'db')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'Danilo')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'D@n153218')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DATABASE', 'crud_flask')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3306))

mysql = MySQL(app)

# ----------------- ROTA AJAX PARA HORÁRIOS DISPONÍVEIS ----------------
@app.route('/horarios_disponiveis', methods=['GET'])
def horarios_disponiveis():
    data = request.args.get('data')
    todos_horarios = [
        "10:00", "10:30", "11:00", "11:30", "12:00", "12:30",
        "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
        "16:00", "16:30", "17:00", "17:30"
    ]
    if not data:
        return jsonify({'horarios': todos_horarios})
    cur = mysql.connection.cursor()
    cur.execute("SELECT horario FROM agendamentos WHERE data = %s", (data,))
    ocupados = [formatar_horario_mysql(h[0]) for h in cur.fetchall()]
    disponiveis = [h for h in todos_horarios if h not in ocupados]
    cur.close()
    return jsonify({'horarios': disponiveis})

# ----------------- ROTAS DO SISTEMA -------------------

@app.route('/')
def home():
    if 'cliente_id' in session:
        return redirect(url_for('painel_cliente'))
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro_cliente():
    erro = None
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        cpf = request.form['cpf'].strip()
        telefone = request.form['telefone'].strip()
        senha = request.form['senha']

        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM clientes WHERE cpf = %s", (cpf,))
        existente = cur.fetchone()
        if existente:
            erro = "Já existe um cliente cadastrado com este CPF."
        else:
            hashed_senha = generate_password_hash(senha)
            cur.execute(
                "INSERT INTO clientes (nome, cpf, telefone, senha) VALUES (%s, %s, %s, %s)",
                (nome, cpf, telefone, hashed_senha)
            )
            mysql.connection.commit()
            cur.close()
            flash("Cadastro realizado com sucesso! Faça login para agendar seu horário.", "success")
            return redirect(url_for('login'))
        cur.close()
    return render_template('cadastro.html', erro=erro)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf = request.form['cpf'].strip()
        senha = request.form['senha']
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, nome, senha FROM clientes WHERE cpf = %s", (cpf,))
        cliente = cur.fetchone()
        cur.close()
        if cliente and check_password_hash(cliente[2], senha):
            session['cliente_id'] = cliente[0]
            session['cliente_nome'] = cliente[1]
            flash(f'Bem-vindo(a), {cliente[1]}!', 'success')
            return redirect(url_for('painel_cliente'))
        else:
            flash('CPF e/ou senha incorretos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da sua conta.', 'success')
    return redirect(url_for('login'))

@app.route('/painel')
def painel_cliente():
    if 'cliente_id' not in session:
        flash('Por favor, faça login para acessar seu painel.', 'danger')
        return redirect(url_for('login'))
    # Exibe os agendamentos já existentes na tela do painel
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, servico, data, horario FROM agendamentos WHERE cliente_id = %s ORDER BY data, horario", (session['cliente_id'],))
    ags = cur.fetchall()
    agendamentos = [{
        'id': a[0],
        'servico': a[1],
        'data': a[2].strftime('%d/%m/%Y'),
        'horario': formatar_horario_mysql(a[3])
    } for a in ags]
    cur.close()
    return render_template('painel.html', nome=session['cliente_nome'], agendamentos=agendamentos)

# -------------------- AGENDAMENTO COM AJAX --------------------------
@app.route('/agendamento', methods=['GET', 'POST'])
def agendamento():
    if 'cliente_id' not in session:
        flash('Você precisa estar logado para agendar horários.', 'danger')
        return redirect(url_for('login'))

    min_date = datetime.now().strftime("%Y-%m-%d")
    servico_selecionado = ""
    data_selecionada = ""
    horario_selecionado = ""
    todos_horarios = [
        "10:00", "10:30", "11:00", "11:30", "12:00", "12:30",
        "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
        "16:00", "16:30", "17:00", "17:30"
    ]

    if request.method == 'POST':
        servico = request.form['servico']
        data_ag = request.form['data']
        hora_ag = request.form['horario']
        servico_selecionado = servico
        data_selecionada = data_ag
        horario_selecionado = hora_ag

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM agendamentos WHERE data = %s AND horario = %s",
            (data_ag, hora_ag)
        )
        ocupado = cur.fetchone()[0] > 0
        if ocupado:
            flash("Esse horário já está agendado! Escolha outro.", "danger")
        else:
            cur.execute(
                "INSERT INTO agendamentos (cliente_id, servico, data, horario) VALUES (%s, %s, %s, %s)",
                (session['cliente_id'], servico, data_ag, hora_ag)
            )
            mysql.connection.commit()
            flash(f"Agendado: {servico} dia {data_ag} às {hora_ag}.", "success")
            cur.close()
            return redirect(url_for('painel_cliente'))
        cur.close()

    # Ao exibir pela primeira vez, pode mostrar todos da "data_selecionada" (template AJAX já recarrega)
    data_ref = data_selecionada or min_date
    cur = mysql.connection.cursor()
    cur.execute("SELECT horario FROM agendamentos WHERE data = %s", (data_ref,))
    ocupados = [formatar_horario_mysql(h[0]) for h in cur.fetchall()]
    horarios_disponiveis = [h for h in todos_horarios if h not in ocupados]
    cur.close()

    return render_template(
        'agendamento.html',
        min_date=min_date,
        horarios_disponiveis=horarios_disponiveis,
        servico_selecionado=servico_selecionado,
        data_selecionada=data_selecionada,
        horario_selecionado=horario_selecionado
    )
# Rota para agendamentos
@app.route('/meus_agendamentos')
def meus_agendamentos():
    if 'cliente_id' not in session:
        flash('Por favor, faça login para visualizar seus agendamentos.', 'danger')
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT servico, data, horario FROM agendamentos WHERE cliente_id = %s ORDER BY data, horario", (session['cliente_id'],))
    ags = cur.fetchall()
    agendamentos = [{
        'servico': a[0],
        'data': a[1].strftime('%d/%m/%Y'),
        'horario': formatar_horario_mysql(a[2])
    } for a in ags]
    cur.close()
    return render_template('meus_agendamentos.html', agendamentos=agendamentos)

# Rota para excluir agendamentos
@app.route('/excluir_agendamento/<int:id>')
def excluir_agendamento(id):
    # Adapta para que só apague se o agendamento for do cliente logado
    if 'cliente_id' not in session:
        flash('Por favor, faça login para excluir agendamentos.', 'danger')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    # Opcional: só deixa excluir se agendamento pertence ao cliente
    cur.execute("DELETE FROM agendamentos WHERE id = %s AND cliente_id = %s", (id, session['cliente_id']))
    mysql.connection.commit()
    cur.close()
    flash('Agendamento excluído com sucesso!', 'success')
    return redirect(url_for('painel_cliente'))

# Rota para alterar agendamentos
@app.route('/alterar_agendamento/<int:id>', methods=['GET', 'POST'])
def alterar_agendamento(id):
    if 'cliente_id' not in session:
        flash('Por favor, faça login para alterar agendamentos.', 'danger')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    # Pega o agendamento do cliente logado
    cur.execute("SELECT servico, data, horario FROM agendamentos WHERE id = %s AND cliente_id = %s", (id, session['cliente_id']))
    ag = cur.fetchone()

    if not ag:
        flash('Agendamento não encontrado.', 'danger')
        cur.close()
        return redirect(url_for('painel_cliente'))

    servico_atual, data_atual, horario_atual = ag[0], ag[1], formatar_horario_mysql(ag[2])

    if request.method == 'POST':
        novo_servico = request.form['servico']
        nova_data = request.form['data']
        novo_horario = request.form['horario']

        # Verifica se já existe outro agendamento nesse horário/data
        cur.execute("""
            SELECT COUNT(*) FROM agendamentos 
            WHERE data = %s AND horario = %s AND id != %s
        """, (nova_data, novo_horario, id))
        conflito = cur.fetchone()[0] > 0

        if conflito:
            flash("Esse horário já está ocupado para essa data!", "danger")
        else:
            cur.execute("""
                UPDATE agendamentos 
                SET servico = %s, data = %s, horario = %s
                WHERE id = %s AND cliente_id = %s
            """, (novo_servico, nova_data, novo_horario, id, session['cliente_id']))
            mysql.connection.commit()
            cur.close()
            flash("Agendamento alterado com sucesso!", "success")
            return redirect(url_for('painel_cliente'))

    else:
        # Exibe formulário preenchido
        novo_servico = servico_atual
        nova_data = data_atual.strftime("%Y-%m-%d")
        novo_horario = horario_atual

    # Horários possíveis (ajuste se necessário)
    todos_horarios = [
        "10:00", "10:30", "11:00", "11:30", "12:00", "12:30",
        "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
        "16:00", "16:30", "17:00", "17:30"
    ]

    # Horários ocupados neste dia, exceto o horário atual deste agendamento
    cur.execute("""
        SELECT horario FROM agendamentos 
        WHERE data = %s AND id != %s
    """, (nova_data, id))
    ocupados = [formatar_horario_mysql(h[0]) for h in cur.fetchall()]
    horarios_disponiveis = [h for h in todos_horarios if (h not in ocupados or h == novo_horario)]

    cur.close()
    return render_template(
        'alterar_agendamento.html',
        servico_atual=novo_servico,
        data_atual=nova_data,
        horario_atual=novo_horario,
        horarios_disponiveis=horarios_disponiveis,
        agendamento_id=id,
        min_date=date.today().strftime("%Y-%m-%d")
    )

# Rota para excluir cliente por ID - somente durante testes!
@app.route('/apagar_cliente/<int:id>')
def apagar_cliente(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM clientes WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash(f'Cliente com id {id} deletado.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
