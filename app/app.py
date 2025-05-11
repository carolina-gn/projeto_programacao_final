from flask import Flask, request, render_template, redirect, url_for, flash, g, session
import mysql.connector
import os


app = Flask(__name__)


app.secret_key = 'buf37gf783g7g9whcu24hdiuv9vu94fbfbf8g8g4'


# Configurações do banco de dados a partir das variáveis de ambiente
app.config['MYSQL_HOST'] = os.getenv('DB_HOST', 'db')
app.config['MYSQL_USER'] = os.getenv('DB_USER', 'flask_user')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD', 'flask_password')
app.config['MYSQL_DATABASE'] = os.getenv('DB_NAME', 'flask_db')


# Gerir coneções com a base
def get_db():
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD'],
                database=app.config['MYSQL_DATABASE']
            )
            app.logger.info("Nova conexão com a base de dados estabelecida")
        except mysql.connector.Error as err:
            app.logger.error(f"Falha na conexão com a base: {err}")
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


@app.route('/login',  methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Preencha todos os campos!', 'error')
            return render_template('login.html')

        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            cursor.close()

            if user:
                # Salvar informações do usuário na sessão
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash('Login bem-sucedido!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Credenciais inválidas!', 'error')

        except mysql.connector.Error as err:
            app.logger.error(f"Erro na verificação de login: {err}")
            flash('Erro ao acessar a base de dados.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu com sucesso!', 'info')
    return redirect(url_for('home'))


@app.route("/")
def home():
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))
    return render_template('index.html')


# @app.route('/user')
# def show_user():
#     if 'user_id' not in session:
#         flash('Por favor, faça login primeiro!', 'warning')
#         return redirect(url_for('login'))
#     return render_template('users.html')
# @app.route('/user/<username>')
# def show_user(username):
#     if 'user_id' not in session:
#         flash('Por favor, faça login primeiro!', 'warning')
#         return redirect(url_for('login'))    
#     return f"Bem-vindo, {username}!"
@app.route('/user')
def show_user():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        cursor.close()
        
        return render_template('users.html', users=users)
    except mysql.connector.Error as err:
        app.logger.error(f"Erro ao buscar usuários: {err}")
        flash('Erro ao buscar usuários na base de dados.', 'error')
        return render_template('users.html', users=[])


@app.route('/add_user', methods=['POST'])
def add_user():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        flash('Preencha todos os campos!', 'error')
        return redirect(url_for('show_user'))
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Verificar se o usuário já existe
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            flash('Nome de utilizador já existe!', 'warning')
            cursor.close()
            return redirect(url_for('show_user'))
        
        # Inserir novo usuário
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                      (username, password))
        db.commit()
        cursor.close()
        
        flash('Utilizador adicionado com sucesso!', 'success')
    except mysql.connector.Error as err:
        db.rollback()
        app.logger.error(f"Erro ao adicionar usuário: {err}")
        flash('Erro ao adicionar utilizador.', 'danger')
    
    return redirect(url_for('show_user'))

@app.route('/delete_user/<int:user_id>', methods=['GET'])
def delete_user(user_id):
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))
    
    if user_id == session['user_id']:
        flash('Não pode excluir o próprio utilizador!', 'danger')
        return redirect(url_for('show_user'))
    
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()
        cursor.close()
        
        flash('Utilizador excluído com sucesso!', 'danger')
    except mysql.connector.Error as err:
        db.rollback()
        app.logger.error(f"Erro ao excluir usuário: {err}")
        flash('Erro ao excluir utilizador.', 'danger')
    
    return redirect(url_for('show_user'))


@app.route("/sobre")
def sobre():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))    
    return render_template('sobre.html')


@app.route('/busca', methods=['GET'])
def busca():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))    
    termo = request.args.get('q')
    return f"Você buscou por: {termo}"


if __name__ == "__main__":
    app.run(debug=True)