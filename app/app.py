import os
from flask import Flask, request, render_template, redirect, url_for, flash, g, session
import mysql.connector
from werkzeug.utils import secure_filename


app = Flask(__name__)


app.secret_key = '24e23c43d423c434343vfghfgd'


# Configurações do banco de dados a partir das variáveis de ambiente
app.config['MYSQL_HOST'] = os.getenv('DB_HOST', 'db')
app.config['MYSQL_USER'] = os.getenv('DB_USER', 'quizzify_user')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD', 'quizzify_pass')
app.config['MYSQL_DATABASE'] = os.getenv('DB_NAME', 'quizzify_db')


# Configurações do upload
UPLOAD_FOLDER = 'static/images/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
            flash('Preencha todos os campos!', 'primary')
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
                flash('Credenciais inválidas!', 'warning')

        except mysql.connector.Error as err:
            app.logger.error(f"Erro na verificação de login: {err}")
            flash('Erro ao acessar a base de dados.', 'danger')

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


@app.route('/user')
def show_user():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, username, photo, is_active FROM users")
        users = cursor.fetchall()
        cursor.close()
        
        return render_template('users.html', users=users)
    except mysql.connector.Error as err:
        app.logger.error(f"Erro ao buscar usuários: {err}")
        flash('Erro ao buscar usuários na base de dados.', 'danger')
        return render_template('users.html', users=[])


@app.route('/add_user', methods=['POST'])
def add_user():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    
    if not username or not password or not email:
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
        
        # Processar upload da foto
        photo_filename = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Usaremos o ID que será gerado
                photo_filename = f"user_temp_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        
        # Inserir novo usuário
        cursor.execute("INSERT INTO users (username, password, email, photo) VALUES (%s, %s, %s, %s)", 
                      (username, password, email, photo_filename))
        user_id = cursor.lastrowid
        
        # Renomear a foto com o ID correto
        if photo_filename:
            new_filename = f"user_{user_id}_{filename}"
            os.rename(
                os.path.join(app.config['UPLOAD_FOLDER'], photo_filename),
                os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            )
            cursor.execute("UPDATE users SET photo = %s WHERE id = %s", (new_filename, user_id))
        
        db.commit()
        cursor.close()
        
        flash('Utilizador adicionado com sucesso!', 'success')
    except Exception as err:
        db.rollback()
        app.logger.error(f"Erro ao adicionar usuário: {err}")
        # Remover foto temporária se existir
        if 'photo_filename' in locals() and photo_filename:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            except OSError:
                pass
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


@app.route('/update_user/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')
            
            # Processar upload da foto
            photo_filename = None
            if 'photo' in request.files:
                file = request.files['photo']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    photo_filename = f"user_{user_id}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            
            # Atualizar dados do usuário
            update_query = "UPDATE users SET username = %s, password = %s, email = %s"
            params = [username, password, email]
            
            if photo_filename:
                update_query += ", photo = %s"
                params.append(photo_filename)
            
            update_query += " WHERE id = %s"
            params.append(user_id)
            
            cursor.execute(update_query, tuple(params))
            db.commit()
            flash('Utilizador atualizado com sucesso!', 'success')
            return redirect(url_for('show_user'))
        
        # GET - Mostrar formulário de edição
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        
        if not user:
            flash('Utilizador não encontrado!', 'error')
            return redirect(url_for('show_user'))
            
        return render_template('edit_user.html', user=user)
    
    except mysql.connector.Error as err:
        db.rollback()
        app.logger.error(f"Erro ao atualizar usuário: {err}")
        flash('Erro ao atualizar utilizador.', 'danger')
        return redirect(url_for('show_user'))


@app.route('/toggle_user/<int:user_id>', methods=['POST'])
def toggle_user(user_id):
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Obter estado atual
        cursor.execute("SELECT is_active FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('Utilizador não encontrado!', 'danger')
            return redirect(url_for('show_user'))
        
        # Inverter estado
        new_state = not user['is_active']
        cursor.execute("UPDATE users SET is_active = %s WHERE id = %s", 
                       (new_state, user_id))
        db.commit()
        cursor.close()
        
        status = "ativado" if new_state else "desativado"
        flash(f'Acesso do utilizador {status} com sucesso!', 'success')
    
    except mysql.connector.Error as err:
        db.rollback()
        app.logger.error(f"Erro ao alterar estado do usuário: {err}")
        flash('Erro ao alterar estado do utilizador.', 'danger')
    
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
    # Cria a pasta de uploads se não existir
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    app.run(debug=True)