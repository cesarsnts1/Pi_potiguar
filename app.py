from flask import Flask, render_template, request, redirect, flash, session, Response, abort, url_for
from db import conectar
from functools import wraps
from pesquisa_lugares import LUGARES_PESQUISADOS, SEED_CHAVE
from config import ADMIN_MATRICULAS, ADMIN_SENHA
import os

app = Flask(__name__)
app.secret_key = 'chave_secreta_potiguar'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # até 32 MB por envio

MAX_IMAGEM_BYTES = 8 * 1024 * 1024  # 8 MB por imagem
TIPOS_IMAGEM_PERMITIDOS = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}


def detectar_tipo_imagem(dados):
    if dados.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg'
    if dados.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png'
    if dados[:4] == b'RIFF' and dados[8:12] == b'WEBP':
        return 'image/webp'
    if dados.startswith((b'GIF87a', b'GIF89a')):
        return 'image/gif'
    return None


def ler_imagem_upload(campo, obrigatoria=False):
    """Lê uma imagem do formulário, valida formato/tamanho e devolve dados para o MySQL."""
    arquivo = request.files.get(campo)

    if not arquivo or not arquivo.filename:
        if obrigatoria:
            raise ValueError('A imagem de capa é obrigatória.')
        return None

    dados = arquivo.read(MAX_IMAGEM_BYTES + 1)
    if len(dados) > MAX_IMAGEM_BYTES:
        raise ValueError(f'A imagem {arquivo.filename} ultrapassa o limite de 8 MB.')

    tipo_real = detectar_tipo_imagem(dados)
    if tipo_real not in TIPOS_IMAGEM_PERMITIDOS:
        raise ValueError(f'O arquivo {arquivo.filename} não é uma imagem JPG, PNG, WEBP ou GIF válida.')

    nome = os.path.basename(arquivo.filename).strip()[:500] or 'imagem'
    return {'dados': dados, 'tipo': tipo_real, 'nome': nome}


def campos_ponto_sem_blobs(alias='p'):
    """Campos usados nas consultas sem carregar os LONGBLOBs inteiros na memória."""
    return f"""
        {alias}.id, {alias}.nome, {alias}.resumo, {alias}.descricao, {alias}.historia,
        {alias}.curiosidades, {alias}.receita, {alias}.sugestao_lugar,
        {alias}.localizacao, {alias}.latitude, {alias}.longitude,
        {alias}.nome_imagem, {alias}.nome_imagem2, {alias}.nome_imagem3, {alias}.nome_imagem4,
        {alias}.categoria_id,
        CASE WHEN {alias}.imagem IS NOT NULL AND OCTET_LENGTH({alias}.imagem) > 0 THEN 1 ELSE 0 END AS tem_imagem1,
        CASE WHEN {alias}.imagem2 IS NOT NULL AND OCTET_LENGTH({alias}.imagem2) > 0 THEN 1 ELSE 0 END AS tem_imagem2,
        CASE WHEN {alias}.imagem3 IS NOT NULL AND OCTET_LENGTH({alias}.imagem3) > 0 THEN 1 ELSE 0 END AS tem_imagem3,
        CASE WHEN {alias}.imagem4 IS NOT NULL AND OCTET_LENGTH({alias}.imagem4) > 0 THEN 1 ELSE 0 END AS tem_imagem4
    """


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
    if 'receita' not in colunas:
        alteracoes.append("ADD COLUMN receita LONGTEXT NULL AFTER curiosidades")
    if 'sugestao_lugar' not in colunas:
        alteracoes.append("ADD COLUMN sugestao_lugar TEXT NULL AFTER receita")
    if 'latitude' not in colunas:
        alteracoes.append("ADD COLUMN latitude DECIMAL(10,7) NULL AFTER localizacao")
    if 'longitude' not in colunas:
        alteracoes.append("ADD COLUMN longitude DECIMAL(10,7) NULL AFTER latitude")
    if 'nome_imagem2' not in colunas:
        alteracoes.append("ADD COLUMN nome_imagem2 VARCHAR(500) NULL AFTER nome_imagem")
    if 'nome_imagem3' not in colunas:
        alteracoes.append("ADD COLUMN nome_imagem3 VARCHAR(500) NULL AFTER nome_imagem2")
    if 'nome_imagem4' not in colunas:
        alteracoes.append("ADD COLUMN nome_imagem4 VARCHAR(500) NULL AFTER nome_imagem3")
    if 'tipo_imagem' not in colunas:
        alteracoes.append("ADD COLUMN tipo_imagem VARCHAR(50) NULL AFTER nome_imagem4")
    if 'imagem' not in colunas:
        alteracoes.append("ADD COLUMN imagem LONGBLOB NULL AFTER tipo_imagem")
    if 'tipo_imagem2' not in colunas:
        alteracoes.append("ADD COLUMN tipo_imagem2 VARCHAR(50) NULL AFTER imagem")
    if 'imagem2' not in colunas:
        alteracoes.append("ADD COLUMN imagem2 LONGBLOB NULL AFTER tipo_imagem2")
    if 'tipo_imagem3' not in colunas:
        alteracoes.append("ADD COLUMN tipo_imagem3 VARCHAR(50) NULL AFTER imagem2")
    if 'imagem3' not in colunas:
        alteracoes.append("ADD COLUMN imagem3 LONGBLOB NULL AFTER tipo_imagem3")
    if 'tipo_imagem4' not in colunas:
        alteracoes.append("ADD COLUMN tipo_imagem4 VARCHAR(50) NULL AFTER imagem3")
    if 'imagem4' not in colunas:
        alteracoes.append("ADD COLUMN imagem4 LONGBLOB NULL AFTER tipo_imagem4")

    for alteracao in alteracoes:
        cursor.execute(f"ALTER TABLE pontos_turisticos {alteracao}")

    if alteracoes:
        conn.commit()

    # Compatibilidade com bancos criados antes da troca de Gastronomico por Comidas.
    cursor.execute("SELECT id FROM categorias WHERE nome = 'Comidas' ORDER BY id LIMIT 1")
    categoria_comidas = cursor.fetchone()
    cursor.execute("SELECT id FROM categorias WHERE nome IN ('Gastronômico', 'Gastronomico') ORDER BY id LIMIT 1")
    categoria_antiga = cursor.fetchone()
    if categoria_antiga and not categoria_comidas:
        cursor.execute("UPDATE categorias SET nome = 'Comidas' WHERE id = %s", (categoria_antiga['id'],))
        conn.commit()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS locais_comida (
            id INT AUTO_INCREMENT PRIMARY KEY,
            comida_id INT NOT NULL,
            ordem TINYINT NOT NULL,
            nome VARCHAR(180) NOT NULL,
            endereco VARCHAR(250) NOT NULL,
            latitude DECIMAL(10,7) NOT NULL,
            longitude DECIMAL(10,7) NOT NULL,
            UNIQUE KEY uq_comida_ordem (comida_id, ordem),
            FOREIGN KEY (comida_id) REFERENCES pontos_turisticos(id) ON DELETE CASCADE
        )
        """
    )
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

        itens_seed = [
            item for item in LUGARES_PESQUISADOS
            if item.get('categoria') not in ('Gastronômico', 'Gastronomico')
        ]

        categorias_ids = {}
        for categoria_nome in sorted({item['categoria'] for item in itens_seed}):
            cursor.execute('SELECT id FROM categorias WHERE nome = %s ORDER BY id LIMIT 1', (categoria_nome,))
            categoria = cursor.fetchone()
            if not categoria:
                cursor.execute('INSERT INTO categorias (nome) VALUES (%s)', (categoria_nome,))
                categorias_ids[categoria_nome] = cursor.lastrowid
            else:
                categorias_ids[categoria_nome] = categoria['id']

        for item in itens_seed:
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
        SELECT {campos_ponto_sem_blobs('p')}, c.nome AS categoria_nome
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


def nome_categoria_por_id(categoria_id):
    """Busca o nome da categoria sem confiar no texto vindo do formulário."""
    if not categoria_id:
        return ''
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT nome FROM categorias WHERE id = %s', (categoria_id,))
    categoria = cursor.fetchone()
    cursor.close()
    conn.close()
    return (categoria or {}).get('nome', '')


def buscar_locais_comida(comida_id):
    """Retorna as sugestões de restaurantes de uma comida na ordem cadastrada."""
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, comida_id, ordem, nome, endereco, latitude, longitude
        FROM locais_comida
        WHERE comida_id = %s
        ORDER BY ordem
        """,
        (comida_id,)
    )
    locais = cursor.fetchall()
    cursor.close()
    conn.close()
    return locais


def ler_locais_comida_formulario():
    """Lê até três restaurantes do formulário e valida suas coordenadas."""
    locais = []

    for ordem in range(1, 4):
        nome = request.form.get(f'restaurante_{ordem}_nome', '').strip()
        endereco = request.form.get(f'restaurante_{ordem}_endereco', '').strip()
        latitude_txt = request.form.get(f'restaurante_{ordem}_latitude', '').strip().replace(',', '.')
        longitude_txt = request.form.get(f'restaurante_{ordem}_longitude', '').strip().replace(',', '.')

        campos = [nome, endereco, latitude_txt, longitude_txt]
        if not any(campos):
            continue

        if not all(campos):
            raise ValueError(
                f'Preencha nome, endereço, latitude e longitude da opção {ordem} de onde comer.'
            )

        try:
            latitude = float(latitude_txt)
            longitude = float(longitude_txt)
        except ValueError:
            raise ValueError(f'As coordenadas do restaurante {ordem} precisam ser números válidos.')

        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            raise ValueError(f'As coordenadas do restaurante {ordem} estão fora do intervalo válido.')

        locais.append({
            'ordem': ordem,
            'nome': nome,
            'endereco': endereco,
            'latitude': latitude,
            'longitude': longitude,
        })

    if not locais:
        raise ValueError('Cadastre pelo menos uma opção de restaurante para a comida.')

    return locais


def salvar_locais_comida(cursor, comida_id, locais):
    """Substitui as sugestões de restaurantes da comida pelas enviadas no formulário."""
    cursor.execute('DELETE FROM locais_comida WHERE comida_id = %s', (comida_id,))
    for local in locais:
        cursor.execute(
            """
            INSERT INTO locais_comida
                (comida_id, ordem, nome, endereco, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                comida_id, local['ordem'], local['nome'], local['endereco'],
                local['latitude'], local['longitude']
            )
        )


def buscar_comidas():
    """Lista apenas pratos cadastrados como Comidas e que possuem receita."""
    garantir_lugares_pesquisados()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        f"""
        SELECT {campos_ponto_sem_blobs('p')}, c.nome AS categoria_nome
        FROM pontos_turisticos p
        LEFT JOIN categorias c ON c.id = p.categoria_id
        WHERE c.nome = 'Comidas'
          AND p.receita IS NOT NULL
          AND TRIM(p.receita) <> ''
        ORDER BY p.id DESC
        """
    )
    comidas = cursor.fetchall()
    cursor.close()
    conn.close()
    return comidas


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


@app.route('/comidas')
@app.route('/gastronomia')
def comidas():
    comidas_banco = buscar_comidas()
    return render_template('comidas.html', comidas_banco=comidas_banco)


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
# IMAGENS DOS LUGARES CADASTRADOS NO MYSQL
# ============================================================

@app.route('/imagem/lugar/<int:lugar_id>/<int:slot>')
def imagem_lugar(lugar_id, slot):
    """Entrega a imagem salva no MySQL. Mantém compatibilidade com registros antigos."""
    campos = {
        1: ('imagem', 'tipo_imagem', 'nome_imagem'),
        2: ('imagem2', 'tipo_imagem2', 'nome_imagem2'),
        3: ('imagem3', 'tipo_imagem3', 'nome_imagem3'),
        4: ('imagem4', 'tipo_imagem4', 'nome_imagem4'),
    }

    if slot not in campos:
        abort(404)

    garantir_estrutura_pontos()
    campo_blob, campo_tipo, campo_nome = campos[slot]
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        f"SELECT {campo_blob} AS dados, {campo_tipo} AS tipo, {campo_nome} AS nome FROM pontos_turisticos WHERE id = %s",
        (lugar_id,)
    )
    imagem = cursor.fetchone()
    cursor.close()
    conn.close()

    if not imagem:
        abort(404)

    if imagem.get('dados'):
        resposta = Response(bytes(imagem['dados']), mimetype=imagem.get('tipo') or 'application/octet-stream')
        resposta.headers['Cache-Control'] = 'public, max-age=86400'
        resposta.headers['X-Content-Type-Options'] = 'nosniff'
        return resposta

    # Compatibilidade com os registros antigos do projeto, que guardavam
    # apenas nome de arquivo/URL em nome_imagem. Novos uploads ficam no MySQL.
    nome = (imagem.get('nome') or '').strip()
    if nome.startswith(('http://', 'https://')):
        return redirect(nome)
    if nome:
        return redirect(url_for('static', filename='img/' + nome))

    abort(404)


@app.errorhandler(413)
def arquivo_grande_demais(_erro):
    flash('As imagens ultrapassaram o limite do envio. Use no máximo 8 MB por foto.', 'danger')
    return redirect('/admin#novo-lugar')


# ============================================================
# PÁGINA AUTOMÁTICA DOS LUGARES CADASTRADOS NO MYSQL
# ============================================================

@app.route('/detalhe/lugar/<int:lugar_id>')
def lugar_dinamico(lugar_id):
    garantir_estrutura_pontos()
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        f"""
        SELECT {campos_ponto_sem_blobs('p')}, c.nome AS categoria_nome
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

    if (lugar.get('categoria_nome') or '').strip().lower() == 'comidas':
        restaurantes = buscar_locais_comida(lugar_id)
        return render_template('detalhes/comida_dinamica.html', lugar=lugar, restaurantes=restaurantes)

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
        f"""
        SELECT {campos_ponto_sem_blobs('p')}, c.nome AS categoria_nome
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
    restaurantes_edicao = []
    if editar_id:
        lugar_edicao = next(
            (lugar for lugar in lugares if lugar.get('id') == editar_id),
            None
        )
        if lugar_edicao is None:
            flash('Lugar não encontrado para edição.', 'danger')
        elif (lugar_edicao.get('categoria_nome') or '').strip().lower() == 'comidas':
            restaurantes_edicao = buscar_locais_comida(editar_id)

    return render_template(
        'admin.html',
        lugares=lugares,
        categorias=categorias,
        sugestoes=sugestoes,
        dashboard=dashboard,
        lugar_edicao=lugar_edicao,
        restaurantes_edicao=restaurantes_edicao
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
    latitude = request.form.get('latitude', '').strip()
    longitude = request.form.get('longitude', '').strip()
    resumo = request.form.get('resumo', '').strip()
    historia = request.form.get('historia', '').strip()
    curiosidades = request.form.get('curiosidades', '').strip()
    receita = request.form.get('receita', '').strip()
    sugestao_lugar = request.form.get('sugestao_lugar', '').strip()
    categoria_nome = nome_categoria_por_id(categoria_id)
    eh_comida = categoria_nome.strip().lower() == 'comidas'

    if not nome or not categoria_id or not resumo or not historia:
        flash('Preencha nome, categoria, resumo e história.', 'danger')
        return redirect('/admin#novo-lugar')

    locais_comida = []
    if eh_comida:
        if not receita:
            flash('Para Comidas, preencha a receita.', 'danger')
            return redirect('/admin#novo-lugar')
        try:
            locais_comida = ler_locais_comida_formulario()
        except ValueError as erro:
            flash(str(erro), 'danger')
            return redirect('/admin#novo-lugar')
        sugestao_lugar = None
        localizacao = ''
        latitude = None
        longitude = None
    else:
        if not localizacao:
            flash('Informe o endereço/localização do lugar.', 'danger')
            return redirect('/admin#novo-lugar')
        if not latitude or not longitude:
            flash('Informe latitude e longitude para cadastrar o local com mapa.', 'danger')
            return redirect('/admin#novo-lugar')
        try:
            latitude = float(latitude.replace(',', '.'))
            longitude = float(longitude.replace(',', '.'))
        except ValueError:
            flash('Latitude e longitude devem ser números válidos, como -6.458123 e -37.097456.', 'danger')
            return redirect('/admin#novo-lugar')
        if not (-90 <= latitude <= 90):
            flash('Latitude inválida. Use um valor entre -90 e 90.', 'danger')
            return redirect('/admin#novo-lugar')
        if not (-180 <= longitude <= 180):
            flash('Longitude inválida. Use um valor entre -180 e 180.', 'danger')
            return redirect('/admin#novo-lugar')

    try:
        uploads = {
            1: ler_imagem_upload('imagem1', obrigatoria=True),
            2: ler_imagem_upload('imagem2'),
            3: ler_imagem_upload('imagem3'),
            4: ler_imagem_upload('imagem4'),
        }
        if eh_comida and any(uploads[slot] is None for slot in (2, 3, 4)):
            flash('Para Comidas, envie as 4 fotos do prato.', 'danger')
            return redirect('/admin#novo-lugar')
    except ValueError as erro:
        flash(str(erro), 'danger')
        return redirect('/admin#novo-lugar')

    descricao = historia
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''
            INSERT INTO pontos_turisticos
            (
                nome, resumo, descricao, historia, curiosidades, receita, sugestao_lugar, localizacao,
                latitude, longitude,
                nome_imagem, nome_imagem2, nome_imagem3, nome_imagem4,
                tipo_imagem, imagem,
                tipo_imagem2, imagem2,
                tipo_imagem3, imagem3,
                tipo_imagem4, imagem4,
                categoria_id
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s,
                %s, %s,
                %s, %s,
                %s, %s,
                %s, %s,
                %s
            )
            ''',
            (
                nome, resumo, descricao, historia, curiosidades or None, receita or None, sugestao_lugar or None, localizacao or None,
                latitude, longitude,
                uploads[1]['nome'],
                uploads[2]['nome'] if uploads[2] else None,
                uploads[3]['nome'] if uploads[3] else None,
                uploads[4]['nome'] if uploads[4] else None,
                uploads[1]['tipo'], uploads[1]['dados'],
                uploads[2]['tipo'] if uploads[2] else None, uploads[2]['dados'] if uploads[2] else None,
                uploads[3]['tipo'] if uploads[3] else None, uploads[3]['dados'] if uploads[3] else None,
                uploads[4]['tipo'] if uploads[4] else None, uploads[4]['dados'] if uploads[4] else None,
                categoria_id
            )
        )
        novo_id = cursor.lastrowid
        if eh_comida:
            salvar_locais_comida(cursor, novo_id, locais_comida)
        conn.commit()
        flash('Cadastro realizado! As informações e imagens foram salvas diretamente no MySQL.', 'success')
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
    """Atualiza o lugar e, quando houver novos arquivos, substitui as imagens no MySQL."""
    garantir_estrutura_pontos()

    nome = request.form.get('nome', '').strip()
    categoria_id = request.form.get('categoria') or None
    localizacao = request.form.get('endereco', '').strip()
    latitude = request.form.get('latitude', '').strip()
    longitude = request.form.get('longitude', '').strip()
    resumo = request.form.get('resumo', '').strip()
    historia = request.form.get('historia', '').strip()
    curiosidades = request.form.get('curiosidades', '').strip()
    receita = request.form.get('receita', '').strip()
    sugestao_lugar = request.form.get('sugestao_lugar', '').strip()
    categoria_nome = nome_categoria_por_id(categoria_id)
    eh_comida = categoria_nome.strip().lower() == 'comidas'

    if not nome or not categoria_id or not resumo or not historia:
        flash('Preencha nome, categoria, resumo e história.', 'danger')
        return redirect(f'/admin?editar={lugar_id}#editar-lugar')

    locais_comida = []
    if eh_comida:
        if not receita:
            flash('Para Comidas, preencha a receita.', 'danger')
            return redirect(f'/admin?editar={lugar_id}#editar-lugar')
        try:
            locais_comida = ler_locais_comida_formulario()
        except ValueError as erro:
            flash(str(erro), 'danger')
            return redirect(f'/admin?editar={lugar_id}#editar-lugar')
        sugestao_lugar = None
        localizacao = ''
        latitude = None
        longitude = None
    else:
        if not localizacao or not latitude or not longitude:
            flash('Informe localização, latitude e longitude para manter o mapa do local.', 'danger')
            return redirect(f'/admin?editar={lugar_id}#editar-lugar')
        try:
            latitude = float(latitude.replace(',', '.'))
            longitude = float(longitude.replace(',', '.'))
        except ValueError:
            flash('Latitude e longitude devem ser números válidos, como -6.458123 e -37.097456.', 'danger')
            return redirect(f'/admin?editar={lugar_id}#editar-lugar')
        if not (-90 <= latitude <= 90):
            flash('Latitude inválida. Use um valor entre -90 e 90.', 'danger')
            return redirect(f'/admin?editar={lugar_id}#editar-lugar')
        if not (-180 <= longitude <= 180):
            flash('Longitude inválida. Use um valor entre -180 e 180.', 'danger')
            return redirect(f'/admin?editar={lugar_id}#editar-lugar')

    try:
        uploads = {slot: ler_imagem_upload(f'imagem{slot}') for slot in range(1, 5)}
    except ValueError as erro:
        flash(str(erro), 'danger')
        return redirect(f'/admin?editar={lugar_id}#editar-lugar')

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute('SELECT id, nome FROM pontos_turisticos WHERE id = %s', (lugar_id,))
        lugar = cursor.fetchone()
        if not lugar:
            flash('Lugar não encontrado ou já removido.', 'danger')
            return redirect('/admin#gerenciar-lugares')

        sets = [
            'nome = %s', 'resumo = %s', 'descricao = %s', 'historia = %s',
            'curiosidades = %s', 'receita = %s', 'sugestao_lugar = %s',
            'localizacao = %s', 'latitude = %s', 'longitude = %s', 'categoria_id = %s'
        ]
        valores = [
            nome, resumo, historia, historia, curiosidades or None, receita or None,
            sugestao_lugar or None, localizacao or None, latitude, longitude, categoria_id
        ]

        campos_imagem = {
            1: ('nome_imagem', 'tipo_imagem', 'imagem'),
            2: ('nome_imagem2', 'tipo_imagem2', 'imagem2'),
            3: ('nome_imagem3', 'tipo_imagem3', 'imagem3'),
            4: ('nome_imagem4', 'tipo_imagem4', 'imagem4'),
        }

        for slot, (campo_nome, campo_tipo, campo_blob) in campos_imagem.items():
            upload = uploads[slot]
            remover = request.form.get(f'remover_imagem{slot}') == '1'

            if upload:
                sets.extend([f'{campo_nome} = %s', f'{campo_tipo} = %s', f'{campo_blob} = %s'])
                valores.extend([upload['nome'], upload['tipo'], upload['dados']])
            elif remover:
                sets.extend([f'{campo_nome} = NULL', f'{campo_tipo} = NULL', f'{campo_blob} = NULL'])

        valores.append(lugar_id)
        cursor.execute(
            f"UPDATE pontos_turisticos SET {', '.join(sets)} WHERE id = %s",
            tuple(valores)
        )
        if eh_comida:
            salvar_locais_comida(cursor, lugar_id, locais_comida)
        else:
            cursor.execute('DELETE FROM locais_comida WHERE comida_id = %s', (lugar_id,))
        conn.commit()
        flash(f'Lugar "{nome}" atualizado com sucesso. As imagens continuam salvas no MySQL.', 'success')
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