import hashlib
from flask import Flask, render_template, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required
from flask_login import logout_user
import sqlite3
import csv

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

users = {
    "manha": {"password": hashlib.sha256("123cdl".encode()).hexdigest(), "id": "usuariom"},
    "noite": {"password": hashlib.sha256("123cdl".encode()).hexdigest(), "id": "usuarion"},
}

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id in users else None

def criar_tabela():
    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visitantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_visitante TEXT,
            atividades TEXT,
            data DATE DEFAULT CURRENT_DATE
        )
    ''')

    conn.commit()
    conn.close()

@app.route('/criar_tabela')
def rota_criar_tabela():
    criar_tabela()
    return 'Tabela criada com sucesso!'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['usuario']
        password = request.form['senha']

        user = users.get(username)

        if user and hashlib.sha256(password.encode()).hexdigest() == user['password']:
            user_obj = User(user['id'])
            login_user(user_obj)
            return render_template('index.html')
        else:
            return render_template('login.html', error='Credenciais inválidas')

    return render_template('login.html')

@app.route('/home')
@login_required
def index():
    return render_template('index.html')

@app.route('/sair')
@login_required
def sair():
    logout_user()
    return render_template('login.html')

@app.route('/salvar', methods=['POST'])
def salvar():
    numero_ordem = request.form['numero_ordem']

    tipo_visitante_codigo = request.form['tipo_visitante']

    atividades = []
    for key, value in request.form.items():
        if key.startswith('atividade_') and value == 'A':
            atividade_codigo = key.split('_')[1]
            atividades.append(converter_codigo_para_nome(atividade_codigo, atividades_options))

    tipo_visitante = converter_codigo_para_nome(tipo_visitante_codigo, tipo_visitante_options)

    try:
        conn = sqlite3.connect('dados.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO visitantes (tipo_visitante, atividades)
            VALUES (?, ?)
        ''', (tipo_visitante, ', '.join(atividades)))

        conn.commit()
        conn.close()

        return jsonify({'mensagem': f'Visitante {numero_ordem} salvo com sucesso!'})
    except Exception as e:
        print(f"Erro ao salvar no banco de dados: {e}")
        return jsonify({'mensagem': 'Erro ao salvar no banco de dados'}), 500
    
@app.route('/gerar_relatorio', methods=['POST'])
def gerar_relatorio():
    start_date = request.form['start-date']
    end_date = request.form['end-date']

    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT tipo_visitante, atividades, data FROM visitantes
        WHERE data BETWEEN ? AND ?
    ''', (start_date, end_date))
    rows = cursor.fetchall()
    conn.close()

    csv_filename = 'relatorio.csv'
    with open(csv_filename, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Ordem', 'Data', 'Tipo de Visitante', 'Atividades'])
        for idx, row in enumerate(rows, start=1):
            csv_writer.writerow([idx, row['data'], row['tipo_visitante'], row['atividades']])

    return jsonify({'mensagem': 'Relatório gerado com sucesso!', 'filename': csv_filename})

def converter_codigo_para_nome(codigo, options):
    for option in options:
        if option['value'] == codigo:
            return option['label']
    return None

tipo_visitante_options = [
    {'value': 'A', 'label': 'Aluno Extensão'},
    {'value': 'B', 'label': 'Aluno Graduação'},
    {'value': 'C', 'label': 'Aluno Pós-Graduação'},
    {'value': 'D', 'label': 'Docente'},
    {'value': 'E', 'label': 'Diretor'},
    {'value': 'F', 'label': 'Funcionário'},
    {'value': 'G', 'label': 'Gestor'},
    {'value': 'H', 'label': 'Institucional'},
    {'value': 'I', 'label': 'Visitante'},
    
]

atividades_options = [
    {'value': 'A', 'label': 'Pesquisa no Acervo'},
    {'value': 'B', 'label': 'Estudo em Grupo'},
    {'value': 'C', 'label': 'Estudo/Leitura Individual'},
    {'value': 'D', 'label': 'Acesso aos Micros'},
    {'value': 'E', 'label': 'Visita'},
    {'value': 'F', 'label': 'Normalização'},
    {'value': 'G', 'label': 'Pesquisa na Internet'},
    {'value': 'H', 'label': 'Orientação de Pesquisa'},
    {'value': 'I', 'label': 'Levantamento Bibliográfico'},
]

if __name__ == '__main__':
    criar_tabela()
    app.run(debug=True)
