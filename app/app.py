import os
from flask import Flask, request, render_template, redirect, url_for, flash, g, session
import mysql.connector
from werkzeug.utils import secure_filename
from mysql.connector import IntegrityError


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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        photo = request.files.get('photo')

        if not username or not password or not email:
            flash('Todos os campos são obrigatórios!', 'warning')
            return redirect(url_for('register'))

        try:
            db = get_db()
            cursor = db.cursor()

            # Verificar se já existe
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                flash('Nome de utilizador já existe!', 'warning')
                return redirect(url_for('register'))

            filename = None
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            cursor.execute("INSERT INTO users (username, password, email, photo) VALUES (%s, %s, %s, %s)",
                           (username, password, email, filename))
            db.commit()
            flash('Conta criada com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            db.rollback()
            app.logger.error(f"Erro ao registrar: {e}")
            flash('Erro ao criar conta.', 'danger')

        finally:
            cursor.close()
            db.close()

    return render_template('register.html')

@app.route('/submit_score', methods=['POST'])
def submit_score():
    if 'user_id' not in session:
        return {'status': 'error', 'message': 'Utilizador não autenticado'}, 401

    data = request.get_json()
    categoria = data.get('categoria')
    pontuacao = data.get('pontuacao')

    if not categoria or pontuacao is None:
        return {'status': 'error', 'message': 'Dados incompletos'}, 400

    try:
        db = get_db()
        cursor = db.cursor()

        query = """
        INSERT INTO pontuacoes (user_id, categoria, pontuacao)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (session['user_id'], categoria, pontuacao))
        db.commit()
        return {'status': 'success', 'message': 'Pontuação gravada com sucesso!'}

    except mysql.connector.errors.IntegrityError:
        return {'status': 'error', 'message': 'Pontuação já submetida para esta categoria'}, 409

    except mysql.connector.Error as err:
        db.rollback()
        app.logger.error(f"Erro ao gravar pontuação: {err}")
        return {'status': 'error', 'message': 'Erro de base de dados'}, 500

    finally:
        cursor.close()
        
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
    #db = get_db()  # Conecta ao banco de dados e dos ranks atribui um limite de utilizadores a aparecer na lista de rankiadas (PÓDIO)
   # cursor = db.cursor(dictionary=True)
   # cursor.execute("""
    #    SELECT u.username, SUM(p.pontuacao) AS total_pontuacao
   #     FROM pontuacoes p
   #     JOIN users u ON p.user_id = u.id
    #    GROUP BY u.username
   #     ORDER BY total_pontuacao DESC
    #    LIMIT 3
   # """)
    #top_jogadores = cursor.fetchall()
    return render_template("principal_base.html") #top_jogadores=top_jogadores

@app.route('/Conhecimento_geral')
def Conhecimento_geral():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))
    return render_template('Conhecimento_geral.html')

@app.route('/Entretenimento')
def Entretenimento():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))
    return render_template('Entretenimento.html')

@app.route('/Desporto')
def Desporto():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))
    return render_template('Desporto.html')

@app.route('/Ciência')
def Ciência():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))
    return render_template('Ciência.html')

@app.route('/definicoes')
def definicoes():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))
    return render_template('definicoes.html')

@app.route('/definicoes_base')
def definicoes_base():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))
    return render_template('definicoes_base.html')
 
@app.route('/rank_estatisticas')
def ranke_estatisticas():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))
    return render_template('rank_estatisticas.html')

@app.route('/rank')
def ranking():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
    SELECT u.username, SUM(p.pontuacao) AS total_pontuacao
    FROM pontuacoes p
    JOIN users u ON p.user_id = u.id
    GROUP BY u.username
    ORDER BY total_pontuacao DESC
    """)

    ranking_data = cursor.fetchall()

    return render_template('rank.html', ranking=ranking_data)


@app.route('/estatisticas')
def estatisticas():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Pontuação por categoria
    cursor.execute("""
        SELECT categoria, SUM(pontuacao) AS total
        FROM pontuacoes
        WHERE user_id = %s
        GROUP BY categoria
    """, (user_id,))
    categoria_stats = cursor.fetchall()

    # Usa o dicionário global CATEGORIAS_NOME
    from app import CATEGORIAS_NOME  # ou garante que está acessível aqui

    # Define o máximo possível por categoria
    maximos_categoria = {
        'Conhecimento_geral': 100,
        'Entretenimento': 100,
        'Desporto': 100,
        'Ciência': 100
    }

    progresso = {}
    for row in categoria_stats:
        nome_categoria = CATEGORIAS_NOME.get(row['categoria'], 'Outra')
        maximo = maximos_categoria.get(nome_categoria, 100)
        progresso[nome_categoria] = int((row['total'] / maximo) * 100)

    # Histórico de pontuações (últimos 5 quizzes)
    cursor.execute("""
        SELECT pontuacao, data FROM pontuacoes
        WHERE user_id = %s
        ORDER BY data DESC
        LIMIT 5
    """, (user_id,))
    historico = cursor.fetchall()
    historico.reverse()

    # Formata as datas para o gráfico
    for row in historico:
        row['data'] = row['data'].strftime('%d/%m/%Y')

    return render_template('estatisticas.html', progresso=progresso, historico=historico)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    # Verifica se o utilizador está logado
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

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

        # Construir query de atualização
        update_query = "UPDATE users SET username = %s, password = %s, email = %s"
        params = [username, password, email]

        if photo_filename:
            update_query += ", photo = %s"
            params.append(photo_filename)

        update_query += " WHERE id = %s"
        params.append(user_id)

        try:
            cursor.execute(update_query, tuple(params))
            db.commit()
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('edit_profile'))
        except Exception as e:
            db.rollback()
            flash('Erro ao atualizar perfil.', 'danger')
            app.logger.error(f"Erro ao atualizar perfil: {e}")

    # Método GET — carregar dados atuais do utilizador
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        flash('Utilizador não encontrado.', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('edit_profile.html', user=user)

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


@app.route('/busca', methods=['GET'])
def busca():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro!', 'warning')
        return redirect(url_for('login'))    
    termo = request.args.get('q')
    return f"Você buscou por: {termo}"



# Mapeamento de nomes de categorias para os seus IDs
CATEGORIAS = {
    "Ciência": 1,
    "Conhecimento_geral": 2,
    "Desporto": 3,
    "Entretenimento": 4,
}
# Inverso: de ID para nome (para mostrar nas views)
CATEGORIAS_NOME = {v: k.capitalize() for k, v in CATEGORIAS.items()}

@app.route('/save_score', methods=['POST'])
def save_score():
    data = request.get_json()  # <- RECEBER JSON
    pontuacao = data.get('pontuacao')
    categoria = data.get('categoria')
    user_id = session.get('user_id')

    app.logger.info(f"Recebido: pontuacao={pontuacao}, categoria={categoria}, user_id={user_id}")

    if not pontuacao or not categoria or not user_id:
        return jsonify({"message": "Dados incompletos!"}), 400

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO pontuacoes (user_id, categoria, pontuacao) VALUES (%s, %s, %s)",
            (user_id, int(categoria), int(pontuacao))
        )
        db.commit()
        return jsonify({"message": "Pontuação salva com sucesso!"}), 200
    except mysql.connector.IntegrityError:
        db.rollback()
        return jsonify({"message": "Pontuação já existe para esta categoria!"}), 409
    except mysql.connector.Error as err:
        db.rollback()
        app.logger.error(f"Erro ao salvar pontuação: {err}")
        return jsonify({"message": "Erro ao salvar pontuação."}), 500
    finally:
        cursor.close()



if __name__ == "__main__":
    # Cria a pasta de uploads se não existir
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    app.run(debug=True)