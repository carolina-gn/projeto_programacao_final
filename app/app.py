    # from flask import Flask
# from flask import Flask, render_template
from flask import Flask, request, render_template, redirect, url_for, flash, g
import mysql.connector
import os # para receber as credenciais de acesso a base do container

app = Flask(__name__)

app.secret_key='84yt9y9g49946yyg3hghh98hg35jhge6'

# Configurações do banco de dados a partir das variáveis de ambiente
app.config['MYSQL_HOST'] = os.getenv('DB_HOST', 'db')  # 'db' é o nome do serviço no compose
app.config['MYSQL_USER'] = os.getenv('DB_USER', 'flask_user')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD', 'flask_password')
app.config['MYSQL_DATABASE'] = os.getenv('DB_NAME', 'flask_db')

# Gerir coneções com a base
def get_db():
    if 'db' not in g: # valida que nao existe conexão com o objeto especial g (namespace global durante o ciclo de vida de uma requisição)
        try:
        # criar a conexão
            g.db = mysql.connector.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD'],
                database=app.config['MYSQL_DATABASE']
            )
            app.logger.info("Nova conexão com a base de dados estabelecida")
            return "Conexão bem-sucedida!"
        except mysql.connector.Error as err:
            app.logger.error(f"Falha na conexão com a base: {err}")
            return f"Erro: {e}"
            raise
    return g.db


# encerra a conexão com uso do decorador
@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
            app.logger.info("Conexão com a base de dados fechada")
        except mysql.connector.Error as err:
            app.logger.error(f"Erro ao fechar conexão: {err}")

 
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Preencha todos os campos!', 'error')
        elif len(password) < 6:
            flash('Senha deve ter 6+ caracteres!', 'error')
        elif password != "123456":
            flash('Senha incorreta!', 'error')
        # simular acesso a database
        elif username == "admin" and password == "123456":
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciais inválidas!', 'error')

    return render_template('login.html')

@app.route("/")
def home():
    connection_status = get_db()
    return render_template('login.html', connection_status=connection_status)

@app.route('/dashboard')
def dashboard():
    # return "Página restrita - Dashboard"
    return render_template('index.html')

@app.route('/user/<username>')
def show_user(username):
    return f"Agora lixou,{username}!"

@app.route('/busca', methods=['GET'])
def busca():
    termo = request.args.get('q')
    return f"Você buscou por: {termo}"

@app.route("/index")
def sobre():
    return render_template('index.html')

@app.route('/base')
def base():
    return render_template('base.html')

@app.route("/sobre")
def sobre():
    return render_template('sobre.html')

if __name__ == "__main__":
    app.run(debug=True)  

