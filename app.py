from flask import Flask, render_template, request, redirect, flash, session
from db import conectar
from functools import wraps
from pesquisa_lugares import LUGARES_PESQUISADOS, SEED_CHAVE
from config import ADMIN_MATRICULAS, ADMIN_SENHA

app = Flask(__name__)
app.secret_key = 'chave_secreta_potiguar'


# ============================================================
# SUPORTE ÀS SUGESTÕES DE LUGARES
# ============================================================

def garantir_tabela_sugestoes():
    """Cria a tabela de sugestões caso o banco já exista sem a migração nova."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sugestoes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(150) NOT NULL,
            categoria_id INT NULL,
            localizacao VARCHAR(200) NOT NULL,
            descricao TEXT NOT NULL,
            imagem VARCHAR(500) NULL,
            nome_sugerente VARCHAR(150) NULL,
            contato VARCHAR(180) NULL,
            status VARCHAR(30) NOT NULL DEFAULT 'Pendente',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
        """
    )
    conn.commit()
    cursor.close()
    conn.close()


# ============================================================
# ESTRUTURA DOS PONTOS TURÍSTICOS (MYSQL)
# ============================================================

def garantir_estrutura_pontos():
    """Mantém a tabela pontos_turisticos compatível sem apagar dados existentes."""
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SHOW COLUMNS FROM pontos_turisticos")
    colunas = {coluna['Field'] for coluna in cursor.fetchall()}

    alteracoes = []
    if 'resumo' not in colunas:
        alteracoes.append("ADD COLUMN resumo TEXT NULL AFTER nome")
    if 'historia' not in colunas:
        alteracoes.append("ADD COLUMN historia LONGTEXT NULL AFTER descricao")
    if 'curiosidades' not in colunas:
        alteracoes.append("ADD COLUMN curiosidades TEXT NULL AFTER historia")
    if 'nome_imagem2' not in colunas:
        alteracoes.append("ADD COLUMN nome_imagem2 VARCHAR(500) NULL AFTER nome_imagem")
    if 'nome_imagem3' not in colunas:
        alteracoes.append("ADD COLUMN nome_imagem3 VARCHAR(500) NULL AFTER nome_imagem2")
    if 'nome_imagem4' not in colunas:
        alteracoes.append("ADD COLUMN nome_imagem4 VARCHAR(500) NULL AFTER nome_imagem3")

    for alteracao in alteracoes:
        cursor.execute(f"ALTER TABLE pontos_turisticos {alteracao}")

    if alteracoes:
        conn.commit()

    cursor.close()
    conn.close()


def garantir_lugares_pesquisados():
    """Insere o pacote pesquisado uma única vez, sem recriar locais removidos depois."""
    garantir_estrutura_pontos()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conteudo_seeds (
                chave VARCHAR(150) PRIMARY KEY,
                aplicado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute('SELECT chave FROM conteudo_seeds WHERE chave = %s', (SEED_CHAVE,))
        if cursor.fetchone():
            return

        categorias_ids = {}
        for categoria_nome in sorted({item['categoria'] for item in LUGARES_PESQUISADOS}):
            cursor.execute('SELECT id FROM categorias WHERE nome = %s ORDER BY id LIMIT 1', (categoria_nome,))
            categoria = cursor.fetchone()
            if not categoria:
                cursor.execute('INSERT INTO categorias (nome) VALUES (%s)', (categoria_nome,))
                categorias_ids[categoria_nome] = cursor.lastrowid
            else:
                categorias_ids[categoria_nome] = categoria['id']

        for item in LUGARES_PESQUISADOS:
            cursor.execute(
                'SELECT id FROM pontos_turisticos WHERE LOWER(nome) = LOWER(%s) ORDER BY id LIMIT 1',
                (item['nome'],)
            )
            if cursor.fetchone():
                continue

            cursor.execute(
                """
                INSERT INTO pontos_turisticos
                (nome, resumo, descricao, historia, curiosidades, localizacao, nome_imagem, categoria_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    item['nome'],
                    item['resumo'],
                    item['historia'],
                    item['historia'],
                    item['curiosidades'],
                    item['localizacao'],
                    item.get('imagem'),
                    categorias_ids[item['categoria']]
                )
            )

        cursor.execute('INSERT INTO conteudo_seeds (chave) VALUES (%s)', (SEED_CHAVE,))
        conn.commit()

    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def buscar_lugares_por_categoria(*nomes):
    """Retorna os lugares cadastrados no MySQL para uma página de categoria."""
    garantir_lugares_pesquisados()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    placeholders = ', '.join(['%s'] * len(nomes))
    cursor.execute(
        f"""
        SELECT p.*, c.nome AS categoria_nome
        FROM pontos_turisticos p
        LEFT JOIN categorias c ON c.id = p.categoria_id
        WHERE c.nome IN ({placeholders})
        ORDER BY p.id DESC
        """,
        nomes
    )
    lugares = cursor.fetchall()
    cursor.close()
    conn.close()
    return lugares


# ============================================================
# ROTAS PÚBLICAS GERAIS
# ============================================================

@app.route('/')
@app.route('/index')
def index():
    return render_template('detalhes/index.html')


@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


@app.route('/cultural')
def cultural():
    lugares_banco = buscar_lugares_por_categoria('Cultural')
    return render_template('cultural.html', lugares_banco=lugares_banco)


@app.route('/historia')
def historia():
    lugares_banco = buscar_lugares_por_categoria('Histórico', 'Historico')
    return render_template('historia.html', lugares_banco=lugares_banco)


@app.route('/gastronomia')
def gastronomia():
    lugares_banco = buscar_lugares_por_categoria('Gastronômico', 'Gastronomico')
    return render_template('gastronomia.html', lugares_banco=lugares_banco)


@app.route('/barra-santana')
def barra_santana():
    return render_template('barra_santana.html')


@app.route('/evento')
def evento():
    lugares_banco = buscar_lugares_por_categoria('Eventos', 'Evento')
    return render_template('evento.html', lugares_banco=lugares_banco)

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

@app.route('/detalhe/docetentacao')
def docetentacao():
    return render_template(
        'detalhes/gastronomico/docetentacao.html')

@app.route('/detalhe/mapamina')
def mapamina():
    return render_template(
        'detalhes/gastronomico/mapamina.html')




# ============================================================
# ROTAS DETALHADAS - HISTÓRICO
# ============================================================


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

@app.route('/detalhe/igrejarosario')
def igrejarosario():
    return render_template(
        'detalhes/historico/igrejarosario.html'
    )

# ============================================================
# ROTAS DETALHADAS - CULTURAL
# ============================================================
@app.route('/detalhe/serra')
def serra():
    return render_template(
        'detalhes/cultural/serra.html'
    )

@app.route('/detalhe/nova_barra')
@app.route('/detalhe/novabarra')
def nova_barra():
    return render_template(
        'detalhes/cultural/nova_barra.html'
    )

@app.route('/detalhe/mercado_publico')
def mercado_publico():
    return render_template(
        'detalhes/cultural/mercado_publico.html'
    )


@app.route('/detalhe/festa_da_barra')
def festa_da_barra():
    return render_template(
        'detalhes/cultural/festa_da_barra.html'
    )

@app.route('/detalhe/calvagada')
def calvagada():
    return render_template(
        'detalhes/cultural/calvagada.html'
    )

@app.route('/detalhe/barragem')
def barragem():
    return render_template(
        'detalhes/cultural/barragem.html'
    )


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

@app.route('/detalhe/arcotriunfo')
def arcotriunfo():
    return render_template(
        'detalhes/cultural/arcotriunfo.html'
    )

# ============================================================
# ROTAS DETALHADAS - EVENTOS
# ============================================================

@app.route('/detalhe/festa_padroeira')
def festa_padroeira():
    return render_template(
        'detalhes/evento/festapadroeira.html'
    )

@app.route('/detalhe/festasantana')
def festasantana():
    return render_template(
        'detalhes/evento/festasantana.html'
    )

@app.route('/detalhe/festarosario')
def festarosario():
    return render_template(
        'detalhes/evento/festarosario.html'
    )



# ============================================================
# PÁGINA AUTOMÁTICA DOS LUGARES CADASTRADOS NO MYSQL
# ============================================================

@app.route('/detalhe/lugar/<int:lugar_id>')
def lugar_dinamico(lugar_id):
    garantir_estrutura_pontos()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT p.*, c.nome AS categoria_nome
        FROM pontos_turisticos p
        LEFT JOIN categorias c ON c.id = p.categoria_id
        WHERE p.id = %s
        """,
        (lugar_id,)
    )
    lugar = cursor.fetchone()
    cursor.close()
    conn.close()

    if not lugar:
        return 'Lugar não encontrado.', 404

    return render_template('detalhes/lugar_dinamico.html', lugar=lugar)

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

    # Também pesquisa os lugares cadastrados pelo painel e os registros pesquisados no MySQL.
    if termo:
        garantir_lugares_pesquisados()
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        like = f'%{termo}%'
        cursor.execute(
            """
            SELECT p.id, p.nome, p.resumo, p.descricao, p.historia, p.localizacao
            FROM pontos_turisticos p
            WHERE LOWER(p.nome) LIKE %s
               OR LOWER(COALESCE(p.resumo, '')) LIKE %s
               OR LOWER(COALESCE(p.descricao, '')) LIKE %s
               OR LOWER(COALESCE(p.historia, '')) LIKE %s
               OR LOWER(COALESCE(p.localizacao, '')) LIKE %s
            ORDER BY p.id DESC
            """,
            (like, like, like, like, like)
        )
        for lugar in cursor.fetchall():
            descricao_busca = lugar.get('resumo') or lugar.get('descricao') or lugar.get('historia') or 'Lugar cadastrado na Memória Potiguar.'
            resultados.append({
                'titulo': lugar['nome'],
                'descricao': descricao_busca,
                'url': f"/detalhe/lugar/{lugar['id']}"
            })
        cursor.close()
        conn.close()

    # buscar.html está dentro de templates/detalhes/
    return render_template(
        'detalhes/buscar.html',
        termo=termo,
        resultados=resultados
    )


# ============================================================
# SUGESTÕES DE LUGARES
# ============================================================

@app.route('/sugestao', methods=['GET', 'POST'])
def sugestao():
    garantir_tabela_sugestoes()

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM categorias ORDER BY nome')
    categorias = cursor.fetchall()

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        categoria_id = request.form.get('categoria') or None
        localizacao = request.form.get('endereco', '').strip()
        descricao = request.form.get('descricao', '').strip()
        imagem = request.form.get('imagem', '').strip() or None
        nome_sugerente = request.form.get('nome_sugerente', '').strip() or None
        contato = request.form.get('contato', '').strip() or None

        if not nome or not localizacao or not descricao:
            cursor.close()
            conn.close()
            flash('Preencha nome, localização e descrição.', 'danger')
            return redirect('/sugestao')

        cursor.execute(
            """
            INSERT INTO sugestoes
            (nome, categoria_id, localizacao, descricao, imagem, nome_sugerente, contato)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (nome, categoria_id, localizacao, descricao, imagem, nome_sugerente, contato)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Sugestão enviada! Ela ficará disponível para análise da administração.', 'success')
        return redirect('/sugestao')

    cursor.close()
    conn.close()
    return render_template('sugestao.html', categorias=categorias)


# ============================================================
# AUTENTICAÇÃO E CADASTRO
# ============================================================

@app.route('/login')
def login():
    return redirect('/cadastro')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        matricula_input = request.form.get('matricula', '').strip()
        senha_input = request.form.get('password', '')

        # Ignora os slots ainda vazios do config.py.
        matriculas_validas = {
            matricula.strip()
            for matricula in ADMIN_MATRICULAS
            if matricula and matricula.strip()
        }

        if matricula_input in matriculas_validas and senha_input == ADMIN_SENHA:
            session['admin_id'] = matricula_input
            session['admin_usuario'] = matricula_input
            session['admin_matricula'] = matricula_input
            return redirect('/admin')

        flash('Matrícula ou senha incorretas.', 'danger')
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
    """Painel administrativo com indicadores calculados automaticamente."""

    garantir_tabela_sugestoes()
    garantir_lugares_pesquisados()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT p.*, c.nome AS categoria_nome
        FROM pontos_turisticos p
        LEFT JOIN categorias c ON c.id = p.categoria_id
        ORDER BY p.id DESC
        """
    )
    lugares = cursor.fetchall()

    cursor.execute('SELECT * FROM categorias ORDER BY nome')
    categorias = cursor.fetchall()

    cursor.execute(
        """
        SELECT s.*, c.nome AS categoria_nome
        FROM sugestoes s
        LEFT JOIN categorias c ON c.id = s.categoria_id
        ORDER BY s.criado_em DESC, s.id DESC
        """
    )
    sugestoes = cursor.fetchall()

    cursor.close()
    conn.close()

    # Os números abaixo são montados a cada carregamento do painel.
    # Assim o administrador não precisa editar contadores manualmente.
    total_lugares = len(lugares)
    total_sugestoes = len(sugestoes)
    sugestoes_pendentes = sum(
        1 for item in sugestoes if str(item.get('status', '')).lower() == 'pendente'
    )
    sugestoes_aprovadas = sum(
        1 for item in sugestoes if str(item.get('status', '')).lower() == 'aprovada'
    )

    totais_por_categoria = {categoria['id']: 0 for categoria in categorias}
    for lugar in lugares:
        categoria_id = lugar.get('categoria_id')
        if categoria_id in totais_por_categoria:
            totais_por_categoria[categoria_id] += 1

    categorias_resumo = []
    for categoria in categorias:
        total = totais_por_categoria.get(categoria['id'], 0)
        percentual = round((total / total_lugares) * 100) if total_lugares else 0
        categorias_resumo.append({
            'id': categoria['id'],
            'nome': categoria['nome'],
            'total': total,
            'percentual': percentual
        })

    dashboard = {
        'total_lugares': total_lugares,
        'total_categorias': len(categorias),
        'total_sugestoes': total_sugestoes,
        'sugestoes_pendentes': sugestoes_pendentes,
        'sugestoes_aprovadas': sugestoes_aprovadas,
        'ultimos_lugares': lugares[:5],
        'categorias_resumo': categorias_resumo
    }

    # Quando o Admin recebe ?editar=ID, a própria tela do painel abre
    # uma seção de edição já preenchida com os dados do MySQL.
    lugar_edicao = None
    editar_id = request.args.get('editar', type=int)
    if editar_id:
        lugar_edicao = next(
            (lugar for lugar in lugares if lugar.get('id') == editar_id),
            None
        )
        if lugar_edicao is None:
            flash('Lugar não encontrado para edição.', 'danger')

    return render_template(
        'admin.html',
        lugares=lugares,
        categorias=categorias,
        sugestoes=sugestoes,
        dashboard=dashboard,
        lugar_edicao=lugar_edicao
    )


# ============================================================
# ADICIONAR LUGAR
# ============================================================

@app.route('/adicionar-lugar', methods=['POST'])
@login_requerido
def adicionar_lugar():
    garantir_estrutura_pontos()

    nome = request.form.get('nome', '').strip()
    categoria_id = request.form.get('categoria') or None
    localizacao = request.form.get('endereco', '').strip()
    resumo = request.form.get('resumo', '').strip()
    historia = request.form.get('historia', '').strip()
    curiosidades = request.form.get('curiosidades', '').strip()
    nome_imagem = (request.form.get('imagem1') or request.form.get('imagem') or '').strip()
    nome_imagem2 = request.form.get('imagem2', '').strip()
    nome_imagem3 = request.form.get('imagem3', '').strip()
    nome_imagem4 = request.form.get('imagem4', '').strip()

    if not nome or not categoria_id or not localizacao or not resumo or not historia:
        flash('Preencha nome, categoria, localização, resumo e história.', 'danger')
        return redirect('/admin#novo-lugar')

    # Mantém descricao preenchida para compatibilidade com partes antigas do projeto.
    descricao = historia

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''
            INSERT INTO pontos_turisticos
            (
                nome,
                resumo,
                descricao,
                historia,
                curiosidades,
                localizacao,
                nome_imagem,
                nome_imagem2,
                nome_imagem3,
                nome_imagem4,
                categoria_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''',
            (
                nome,
                resumo,
                descricao,
                historia,
                curiosidades or None,
                localizacao,
                nome_imagem or None,
                nome_imagem2 or None,
                nome_imagem3 or None,
                nome_imagem4 or None,
                categoria_id
            )
        )
        conn.commit()
        novo_id = cursor.lastrowid
        flash('Lugar cadastrado e publicado automaticamente no site!', 'success')
        return redirect(f'/detalhe/lugar/{novo_id}')

    except Exception as e:
        conn.rollback()
        print('ERRO BANCO:', e)
        flash(f'Erro ao salvar: {e}', 'danger')
        return redirect('/admin#novo-lugar')

    finally:
        cursor.close()
        conn.close()


# ============================================================
# EDITAR LUGAR CADASTRADO NO MYSQL
# ============================================================

@app.route('/admin/lugar/<int:lugar_id>/editar', methods=['POST'])
@login_requerido
def editar_lugar(lugar_id):
    """Atualiza um lugar no MySQL e reflete a alteração automaticamente no site."""
    garantir_estrutura_pontos()

    nome = request.form.get('nome', '').strip()
    categoria_id = request.form.get('categoria') or None
    localizacao = request.form.get('endereco', '').strip()
    resumo = request.form.get('resumo', '').strip()
    historia = request.form.get('historia', '').strip()
    curiosidades = request.form.get('curiosidades', '').strip()
    nome_imagem = (request.form.get('imagem1') or request.form.get('imagem') or '').strip()
    nome_imagem2 = request.form.get('imagem2', '').strip()
    nome_imagem3 = request.form.get('imagem3', '').strip()
    nome_imagem4 = request.form.get('imagem4', '').strip()

    if not nome or not categoria_id or not localizacao or not resumo or not historia:
        flash('Preencha nome, categoria, localização, resumo e história.', 'danger')
        return redirect(f'/admin?editar={lugar_id}#editar-lugar')

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            'SELECT id, nome FROM pontos_turisticos WHERE id = %s',
            (lugar_id,)
        )
        lugar = cursor.fetchone()

        if not lugar:
            flash('Lugar não encontrado ou já removido.', 'danger')
            return redirect('/admin#gerenciar-lugares')

        cursor.execute(
            '''
            UPDATE pontos_turisticos
            SET nome = %s,
                resumo = %s,
                descricao = %s,
                historia = %s,
                curiosidades = %s,
                localizacao = %s,
                nome_imagem = %s,
                nome_imagem2 = %s,
                nome_imagem3 = %s,
                nome_imagem4 = %s,
                categoria_id = %s
            WHERE id = %s
            ''',
            (
                nome,
                resumo,
                historia,  # descricao continua espelhando história por compatibilidade
                historia,
                curiosidades or None,
                localizacao,
                nome_imagem or None,
                nome_imagem2 or None,
                nome_imagem3 or None,
                nome_imagem4 or None,
                categoria_id,
                lugar_id
            )
        )
        conn.commit()
        flash(f'Lugar "{nome}" atualizado com sucesso no MySQL e no site.', 'success')
        return redirect('/admin#gerenciar-lugares')

    except Exception as e:
        conn.rollback()
        print('ERRO AO EDITAR LUGAR:', e)
        flash(f'Não foi possível salvar as alterações: {e}', 'danger')
        return redirect(f'/admin?editar={lugar_id}#editar-lugar')

    finally:
        cursor.close()
        conn.close()


# ============================================================
# REMOVER LUGAR CADASTRADO NO MYSQL
# ============================================================

@app.route('/admin/lugar/<int:lugar_id>/remover', methods=['POST'])
@login_requerido
def remover_lugar(lugar_id):
    """Remove um lugar do MySQL; as páginas e cards dinâmicos somem automaticamente."""
    garantir_estrutura_pontos()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            'SELECT id, nome FROM pontos_turisticos WHERE id = %s',
            (lugar_id,)
        )
        lugar = cursor.fetchone()

        if not lugar:
            flash('Lugar não encontrado ou já removido.', 'danger')
            return redirect('/admin#gerenciar-lugares')

        cursor.execute('DELETE FROM pontos_turisticos WHERE id = %s', (lugar_id,))
        conn.commit()
        flash(f'Lugar "{lugar["nome"]}" removido do site e do MySQL.', 'success')
        return redirect('/admin#gerenciar-lugares')

    except Exception as e:
        conn.rollback()
        print('ERRO AO REMOVER LUGAR:', e)
        flash(f'Não foi possível remover o lugar: {e}', 'danger')
        return redirect('/admin#gerenciar-lugares')

    finally:
        cursor.close()
        conn.close()


# ============================================================
# AÇÕES DAS SUGESTÕES NO PAINEL ADMIN
# ============================================================

@app.route('/admin/sugestao/<int:sugestao_id>/aprovar', methods=['POST'])
@login_requerido
def aprovar_sugestao(sugestao_id):
    garantir_tabela_sugestoes()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM sugestoes WHERE id = %s', (sugestao_id,))
    item = cursor.fetchone()

    if not item:
        cursor.close()
        conn.close()
        flash('Sugestão não encontrada.', 'danger')
        return redirect('/admin')

    garantir_estrutura_pontos()
    cursor.execute(
        """
        INSERT INTO pontos_turisticos
        (nome, resumo, descricao, historia, curiosidades, localizacao, nome_imagem, categoria_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            item['nome'],
            item['descricao'],
            item['descricao'],
            item['descricao'],
            None,
            item['localizacao'],
            item['imagem'],
            item['categoria_id']
        )
    )
    cursor.execute("UPDATE sugestoes SET status = 'Aprovada' WHERE id = %s", (sugestao_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Sugestão aprovada e adicionada aos lugares cadastrados.', 'success')
    return redirect('/admin')


@app.route('/admin/sugestao/<int:sugestao_id>/recusar', methods=['POST'])
@login_requerido
def recusar_sugestao(sugestao_id):
    garantir_tabela_sugestoes()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE sugestoes SET status = 'Recusada' WHERE id = %s", (sugestao_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Sugestão marcada como recusada.', 'success')
    return redirect('/admin')


# ============================================================
# INICIAR APLICAÇÃO
# ============================================================

if __name__ == '__main__':
    app.run(debug=True)