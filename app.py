from flask import Flask, render_template, request, redirect, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave_secreta_potiguar'


def conectar_banco():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# ----------------------------
# ROTAS PÚBLICAS
# ----------------------------

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


@app.route('/categorias')
def categorias():
    return render_template('categorias.html')


@app.route('/historia')
def historia():
    return render_template('historia.html')


@app.route('/gastronomia')
def gastronomia():
    return render_template('gastronomia.html')


@app.route('/cutural')
def cutural():
    return render_template('cutural.html')



# ROTA CORRIGIDA: Agora aceita o formato /detalhe/recantotapera
# ROTA CORRIGIDA COM O CAMINHO DA SUBPASTA

#GASTRONOMICO
@app.route('/detalhe/recantotapera')
def recantotapera():
    return render_template('detalhes/recantotapera.html')

@app.route('/detalhe/gastrobar')
def gastrobar():
    return render_template('detalhes/gastrobar.html')

@app.route('/detalhe/pracatrailers')
def pracatrailers():
    return render_template('detalhes/pracatrailers.html')

@app.route('/detalhe/temperoterra')
def temperoterra():
    return render_template('detalhes/temperoterra.html')

@app.route('/detalhe/mozafla')
def mozafla():
    return render_template('detalhes/mozafla.html')

@app.route('/detalhe/restaurantezorro')
def restaurantezorro():
    return render_template('detalhes/restaurantezorro.html')






@app.route('/detalhe/artesanato')
def artesanato():
    return render_template('detalhes/artesanato.html')

@app.route('/detalhe/casacultura')
def casacultura():
    return render_template('detalhes/casacultura.html')


@app.route('/detalhe/casafortecuo')
def casafortecuo():
    return render_template('detalhes/casafortecuo.html')
gastrobar
@app.route('/login')
def login():
    return redirect('/cadastro')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():

    if request.method == 'POST':
        usuario_input = request.form.get('username')
        senha_input = request.form.get('password')

        conn = conectar_banco()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM usuarios
            WHERE (matricula = ? OR email = ?) AND senha = ?
        ''', (usuario_input, usuario_input, senha_input))

        usuario_encontrado = cursor.fetchone()

        conn.close()

        if usuario_encontrado:
            return redirect('/admin')
        else:
            flash('Matrícula/E-mail ou senha incorretos.', 'danger')
            return redirect('/cadastro')

    return render_template('cadastro.html')


# ----------------------------
# ROTAS ADMIN
# ----------------------------

@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/adicionar-lugar', methods=['POST'])
def adicionar_lugar():

    nome = request.form.get('nome')
    categoria = request.form.get('categoria')
    endereco = request.form.get('endereco')
    descricao = request.form.get('descricao')
    imagem = request.form.get('imagem')

    conn = conectar_banco()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO lugares
            (nome, categoria, endereco, descricao, imagem)
            VALUES (?, ?, ?, ?, ?)
        ''', (nome, categoria, endereco, descricao, imagem))

        conn.commit()

        flash('O novo lugar foi cadastrado com êxito na Memória Potiguar.')

    except sqlite3.Error as e:
        print(f'Erro no banco: {e}')
        flash('Erro ao tentar salvar no banco de dados.')

    finally:
        conn.close()

    return redirect('/admin')


@app.route('/logout')
def logout():
    flash('Você saiu do painel administrativo.')
    return redirect('/index')


if __name__ == '__main__':
    app.run(debug=True)