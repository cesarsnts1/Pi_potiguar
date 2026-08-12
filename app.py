from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.security import check_password_hash
from db import conectar
from functools import wraps

app = Flask(__name__)
app.secret_key = 'chave_secreta_potiguar'


# ============================================================
# ROTAS PÚBLICAS GERAIS
# ============================================================

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


@app.route('/cultural')
def cultural():
    return render_template('cultural.html')


@app.route('/historia')
def historia():
    return render_template('historia.html')


@app.route('/gastronomia')
def gastronomia():
    return render_template('gastronomia.html')


@app.route('/barra-santana')
def barra_santana():
    return render_template('barra_santana.html')


@app.route('/evento')
def eventos():
    return render_template('evento.html')


# ============================================================
# ROTAS DETALHADAS - GASTRONOMIA
# ============================================================

@app.route('/detalhe/recantotapera')
def recantotapera():
    return render_template(
        'detalhes/gastronomico/recantotapera.html'
    )


@app.route('/detalhe/temperoterra')
def temperoterra():
    return render_template(
        'detalhes/gastronomico/temperoterra.html'
    )


@app.route('/detalhe/zorro')
def zorro():
    return render_template(
        'detalhes/gastronomico/zorro.html'
    )


# ============================================================
# ROTAS DETALHADAS - HISTÓRICO
# ============================================================

@app.route('/detalhe/novabarra')
def novabarra():
    return render_template(
        'detalhes/historico/novabarra.html'
    )


@app.route('/detalhe/casafortecuo')
def casafortecuo():
    return render_template(
        'detalhes/historico/casafortecuo.html'
    )


@app.route('/detalhe/casteloengady')
def casteloengady():
    return render_template(
        'detalhes/historico/casteloengady.html'
    )


@app.route('/detalhe/museuserido')
def museuserido():
    return render_template(
        'detalhes/historico/museuserido.html'
    )


@app.route('/detalhe/catedralsantana')
def catedralsantana():
    return render_template(
        'detalhes/historico/catedralsantana.html'
    )


@app.route('/detalhe/casapedra')
def casapedra():
    return render_template(
        'detalhes/historico/casapedra.html'
    )


# ============================================================
# ROTAS DETALHADAS - CULTURAL
# ============================================================

@app.route('/detalhe/casacultura')
def casacultura():
    return render_template(
        'detalhes/cultural/casacultura.html'
    )


@app.route('/detalhe/artesanato')
def artesanato():
    return render_template(
        'detalhes/cultural/artesanato.html'
    )


# ============================================================
# ROTAS DETALHADAS - EVENTOS
# ============================================================

@app.route('/detalhe/festa_padroeira')
def festa_padroeira():
    return render_template(
        'detalhes/evento/festa_padroeira.html'
    )


# ============================================================
# BARRA DE PESQUISA
# ============================================================

@app.route('/buscar')
def buscar():

    termo = request.args.get('q', '').strip().lower()

    resultados = []

    paginas = [

        {
            'titulo': 'Velha Barra de Santana',
            'descricao': (
                'História da antiga Barra de Santana, '
                'sua origem, cultura, cotidiano, resistência '
                'e reassentamento.'
            ),
            'url': '/barra-santana'
        },

        {
            'titulo': 'Nova Barra de Santana',
            'descricao': (
                'Conheça a Nova Barra de Santana '
                'e o reassentamento das famílias.'
            ),
            'url': '/detalhe/novabarra'
        },

        {
            'titulo': 'Casa Forte Cuó',
            'descricao': (
                'História e importância da Casa Forte Cuó.'
            ),
            'url': '/detalhe/casafortecuo'
        },

        {
            'titulo': 'Castelo de Engady',
            'descricao': (
                'Conheça a história do Castelo de Engady.'
            ),
            'url': '/detalhe/casteloengady'
        },

        {
            'titulo': 'Museu do Seridó',
            'descricao': (
                'História e cultura do Seridó.'
            ),
            'url': '/detalhe/museuserido'
        },

        {
            'titulo': 'Catedral de Santana',
            'descricao': (
                'História da Catedral de Santana.'
            ),
            'url': '/detalhe/catedralsantana'
        },

        {
            'titulo': 'Casa de Pedra',
            'descricao': (
                'Conheça a história da Casa de Pedra.'
            ),
            'url': '/detalhe/casapedra'
        },

        {
            'titulo': 'Casa de Cultura',
            'descricao': (
                'Cultura e memória da região do Seridó.'
            ),
            'url': '/detalhe/casacultura'
        },

        {
            'titulo': 'Artesanato',
            'descricao': (
                'Artesanato e tradições culturais do Seridó.'
            ),
            'url': '/detalhe/artesanato'
        },

        {
            'titulo': 'Festa da Padroeira',
            'descricao': (
                'Festas e tradições religiosas da região.'
            ),
            'url': '/detalhe/festa_padroeira'
        }
    ]

    # Procurar o termo
    if termo:

        for pagina in paginas:

            texto = (
                pagina['titulo']
                + ' '
                + pagina['descricao']
            ).lower()

            if termo in texto:
                resultados.append(pagina)

    # buscar.html está dentro de templates/detalhes/
    return render_template(
        'detalhes/buscar.html',
        termo=termo,
        resultados=resultados
    )


# ============================================================
# AUTENTICAÇÃO E CADASTRO
# ============================================================

@app.route('/login')
def login():
    return redirect('/cadastro')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():

    if request.method == 'POST':

        usuario_input = request.form.get('username')
        senha_input = request.form.get('password')

        conn = conectar()
        cursor = conn.cursor(
            dictionary=True,
            buffered=True
        )

        cursor.execute(
            '''
            SELECT *
            FROM administradores
            WHERE usuario = %s
            ''',
            (usuario_input,)
        )

        admin = cursor.fetchone()

        cursor.close()
        conn.close()

        if admin and check_password_hash(
            admin['senha'],
            senha_input
        ):

            session['admin_id'] = admin['id']
            session['admin_usuario'] = admin['usuario']

            return redirect('/admin')

        else:

            flash(
                'Usuário ou senha incorretos.',
                'danger'
            )

            return redirect('/cadastro')

    return render_template('cadastro.html')


# ============================================================
# PROTEÇÃO DAS ROTAS ADMINISTRATIVAS
# ============================================================

def login_requerido(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if 'admin_id' not in session:

            flash(
                'Faça login para acessar o painel.',
                'warning'
            )

            return redirect('/cadastro')

        return f(*args, **kwargs)

    return wrapper


# ============================================================
# PAINEL ADMINISTRATIVO
# ============================================================

@app.route('/admin')
@login_requerido
def admin():

    conn = conectar()

    cursor = conn.cursor(
        dictionary=True
    )

    cursor.execute(
        'SELECT * FROM pontos_turisticos ORDER BY id DESC'
    )

    lugares = cursor.fetchall()

    cursor.execute(
        'SELECT * FROM categorias ORDER BY nome'
    )

    categorias = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'admin.html',
        lugares=lugares,
        categorias=categorias
    )


# ============================================================
# ADICIONAR LUGAR
# ============================================================

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

        cursor.execute(
            '''
            INSERT INTO pontos_turisticos
            (
                nome,
                descricao,
                localizacao,
                nome_imagem,
                categoria_id
            )
            VALUES (%s, %s, %s, %s, %s)
            ''',
            (
                nome,
                descricao,
                localizacao,
                nome_imagem,
                categoria_id
            )
        )

        conn.commit()

        flash(
            'Novo lugar cadastrado com êxito na Memória Potiguar!',
            'success'
        )

    except Exception as e:

        conn.rollback()

        print('ERRO BANCO:', e)

        flash(
            f'Erro ao salvar: {e}',
            'danger'
        )

    finally:

        cursor.close()
        conn.close()

    return redirect('/admin')


# ============================================================
# INICIAR APLICAÇÃO
# ============================================================

if __name__ == '__main__':
    app.run(debug=True)