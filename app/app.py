from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

app.secret_key='84yt9y9g49946yyg3hghh98hg35jhge6'
 
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
    return render_template('login.html')

@app.route('/user/<username>')
def show_user(username):
    return f"Agora lixou,{username}!"

@app.route('/base')
def base():
    return render_template('base.html')

@app.route("/sobre")
def sobre():
    return render_template('sobre.html')

if __name__ == "__main__":
    app.run(debug=True)  