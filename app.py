from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.security import check_password_hash
from db import conectar

app = Flask(__name__)
app.secret_key = 'chave_secreta_potiguar'


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


#  GASTRONOMIA

@app.route('/detalhe/recantotapera')
def recantotapera():
    return render_template('detalhes/recantotapera.html')


@app.route('/detalhe/pracatrailers')
def pracatrailers():
    return render_template('detalhes/pracatrailers.html')


@app.route('/detalhe/temperoterra')
def temperoterra():
    return render_template('detalhes/temperoterra.html')


@app.route('/detalhe/zorro')
def zorro():
    return render_template('detalhes/zorro.html')


# HISTÓRICO
@app.route('/detalhe/velhabarra')
def velhabarra():
    return render_template('detalhes/velhabarra.html')

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


@app.route('/detalhe/catedralsantana')
def catedralsantana():
    return render_template('detalhes/catedralsantana.html')


# ROTAS DETALHADAS: CULTURAL




# AUTENTICAÇÃO E CADASTRO


@app.route('/login')
def login():
    return redirect('/cadastro')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        usuario_input = request.form.get('username')
        senha_input = request.form.get('password')

        conn = conectar()
        cursor = conn.cursor(dictionary=True, buffered=True)

        cursor.execute(
            'SELECT * FROM administradores WHERE usuario = %s',
            (usuario_input,)
        )
        admin = cursor.fetchone()
        cursor.close()
        conn.close()

        if admin and check_password_hash(admin['senha'], senha_input):
            session['admin_id'] = admin['id']
            session['admin_usuario'] = admin['usuario']
            return redirect('/admin')
        else:
            flash('Usuário ou senha incorretos.', 'danger')
            return redirect('/cadastro')

    return render_template('cadastro.html')


# ----------------------------
# PAINEL ADMINISTRATIVO
# ----------------------------

def login_requerido(f):
    """Decorador simples para proteger rotas do admin."""
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Faça login para acessar o painel.', 'warning')
            return redirect('/cadastro')
        return f(*args, **kwargs)
    return wrapper


@app.route('/admin')
@login_requerido
def admin():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM pontos_turisticos ORDER BY id DESC')
    lugares = cursor.fetchall()
    cursor.execute('SELECT * FROM categorias ORDER BY nome')
    categorias = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin.html', lugares=lugares, categorias=categorias)


@app.route('/adicionar-lugar', methods=['POST'])
@login_requerido
def adicionar_lugar():

    nome = request.form.get('nome')
    categoria_id = request.form.get('categoria')
    localizacao = request.form.get('endereco')
    descricao = request.form.get('descricao')
    nome_imagem = request.form.get('imagem')

    conn = conectar()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO pontos_turisticos
            (
                nome,
                descricao,
                localizacao,
                nome_imagem,
                categoria_id
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            nome,
            descricao,
            localizacao,
            nome_imagem,
            categoria_id
        ))

        conn.commit()

        flash(
            'Novo lugar cadastrado com êxito na Memória Potiguar!',
            'success'
        )

    except Exception as e:

        conn.rollback()

        print("ERRO BANCO:", e)

        flash(
            f'Erro ao salvar: {e}',
            'danger'
        )

    finally:

        cursor.close()
        conn.close()

    return redirect('/admin')


if __name__ == '__main__':
    app.run(debug=True)