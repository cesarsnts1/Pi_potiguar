from flask import Flask, render_template, request, redirect, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave_secreta_potiguar'


def conectar_banco():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# ----------------------------
# ROTAS PÚBLICAS GERAIS
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


@app.route('/cultural')  
def cultural():
    return render_template('cultural.html')




# ROTAS DETALHADAS: GASTRONOMIA


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



# ROTAS DETALHADAS: HISTÓRICO 

@app.route('/detalhe/casafortecuo')
def casafortecuo():
    return render_template('detalhes/casafortecuo.html')


@app.route('/detalhe/cruzeiroalmas')
def cruzeiroalmas():
    return render_template('detalhes/cruzeiroalmas.html')


@app.route('/detalhe/casteloengady')
def casteloengady():
    return render_template('detalhes/casteloengady.html')


@app.route('/detalhe/museuserido')
def museuserido():
    return render_template('detalhes/museuserido.html')


@app.route('/detalhe/igrejamatriz')
def igrejamatriz():
    return render_template('detalhes/igrejamatriz.html')



# ROTAS DETALHADAS: CULTURAL















# ----------------------------
# AUTENTICAÇÃO E CADASTRO
# ----------------------------

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
# PAINEL ADMINISTRATIVO
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
        flash('O novo lugar foi cadastrado com êxito na Memória Potiguar.', 'success')

    except sqlite3.Error as e:
        print(f'Erro no banco: {e}')
        flash('Erro ao tentar salvar no banco de dados.', 'danger')

    finally:
        conn.close()

    return redirect('/admin')


@app.route('/logout')
def logout():
    flash('Você saiu do painel administrativo.', 'info')
    return redirect('/index')


if __name__ == '__main__':
    app.run(debug=True)