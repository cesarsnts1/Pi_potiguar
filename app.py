import os
import unicodedata
from functools import wraps
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from config import ADMIN_MATRICULAS, ADMIN_SENHA

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'chave_secreta_potiguar')

PAGINAS_MANUAIS = [
    ('Velha Barra de Santana', '/barra-santana', 'Hist\u00f3ria da antiga comunidade e seu reassentamento.'),
    ('Nova Barra de Santana', '/detalhe/novabarra', 'Conhe\u00e7a a nova comunidade.'),
    ('Casa Forte Cu\u00f3', '/detalhe/casafortecuo', 'Hist\u00f3ria e import\u00e2ncia da Casa Forte Cu\u00f3.'),
    ('Castelo de Engady', '/detalhe/casteloengady', 'Hist\u00f3ria do Castelo de Engady.'),
    ('Museu do Serid\u00f3', '/detalhe/museuserido', 'Hist\u00f3ria e cultura do Serid\u00f3.'),
    ('Catedral de Santana', '/detalhe/catedralsantana', 'Hist\u00f3ria da Catedral de Santana.'),
    ('Casa de Pedra', '/detalhe/casapedra', 'Conhe\u00e7a a hist\u00f3ria da Casa de Pedra.'),
    ('Serra', '/detalhe/serra', 'Conte\u00fado cultural da regi\u00e3o.'),
    ('Mercado P\u00fablico', '/detalhe/mercado_publico', 'Hist\u00f3ria do Mercado P\u00fablico.'),
    ('Festa da Padroeira', '/detalhe/festa_padroeira', 'Festas e tradi\u00e7\u00f5es locais.'),
    ('Festa de Santana', '/detalhe/festasantana', 'Celebra\u00e7\u00e3o tradicional de Santana.'),
    ('Festa do Ros\u00e1rio', '/detalhe/festarosario', 'Tradi\u00e7\u00e3o religiosa e cultural.'),
    ('Recanto Tapera', '/detalhe/recantotapera', 'P\u00e1gina gastron\u00f4mica.'),
    ('Tempero da Terra', '/detalhe/temperoterra', 'P\u00e1gina gastron\u00f4mica.'),
    ('Zorro', '/detalhe/zorro', 'P\u00e1gina gastron\u00f4mica.'),
    ('Doce Tentacao', '/detalhe/docetentacao', 'P\u00e1gina gastron\u00f4mica.'),
    ('Mapa Mina', '/detalhe/mapamina', 'P\u00e1gina gastron\u00f4mica.'),
]


def login_requerido(funcao):
    @wraps(funcao)
    def proteger(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Entre com a conta administrativa para continuar.', 'warning')
            return redirect(url_for('cadastro'))
        return funcao(*args, **kwargs)
    return proteger


@app.route('/')
@app.route('/index')
def index():
    return render_template('detalhes/index.html')


@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


@app.route('/cultural')
def cultural():
    return render_template('cultural.html', lugares_banco=[])


@app.route('/historia')
def historia():
    return render_template('historia.html', lugares_banco=[])


@app.route('/comidas')
@app.route('/gastronomia')
def comidas():
    return render_template('comidas.html', comidas_banco=[])


@app.route('/barra-santana')
def barra_santana():
    return render_template('barra_santana.html')


@app.route('/evento')
def evento():
    return render_template('evento.html', lugares_banco=[])


@app.route('/detalhe/recantotapera')
def recantotapera():
    return render_template('detalhes/gastronomico/recantotapera.html')


@app.route('/detalhe/temperoterra')
def temperoterra():
    return render_template('detalhes/gastronomico/temperoterra.html')


@app.route('/detalhe/zorro')
def zorro():
    return render_template('detalhes/gastronomico/zorro.html')


@app.route('/detalhe/docetentacao')
def docetentacao():
    return render_template('detalhes/gastronomico/docetentacao.html')


@app.route('/detalhe/mapamina')
def mapamina():
    return render_template('detalhes/gastronomico/mapamina.html')


@app.route('/detalhe/casafortecuo')
def casafortecuo():
    return render_template('detalhes/historico/casafortecuo.html')


@app.route('/detalhe/casteloengady')
def casteloengady():
    return render_template('detalhes/historico/casteloengady.html')


@app.route('/detalhe/museuserido')
def museuserido():
    return render_template('detalhes/historico/museuserido.html')


@app.route('/detalhe/catedralsantana')
def catedralsantana():
    return render_template('detalhes/historico/catedralsantana.html')


@app.route('/detalhe/casapedra')
def casapedra():
    return render_template('detalhes/historico/casapedra.html')


@app.route('/detalhe/igrejarosario')
def igrejarosario():
    return render_template('detalhes/historico/igrejarosario.html')


@app.route('/detalhe/serra')
def serra():
    return render_template('detalhes/cultural/serra.html')


@app.route('/detalhe/nova_barra')
@app.route('/detalhe/novabarra')
def nova_barra():
    return render_template('detalhes/cultural/nova_barra.html')


@app.route('/detalhe/mercado_publico')
def mercado_publico():
    return render_template('detalhes/cultural/mercado_publico.html')


@app.route('/detalhe/festa_da_barra')
def festa_da_barra():
    return render_template('detalhes/cultural/festa_da_barra.html')


@app.route('/detalhe/calvagada')
def calvagada():
    return render_template('detalhes/cultural/calvagada.html')


@app.route('/detalhe/barragem')
def barragem():
    return render_template('detalhes/cultural/barragem.html')


@app.route('/detalhe/casacultura')
def casacultura():
    return render_template('detalhes/cultural/casacultura.html')


@app.route('/detalhe/artesanato')
def artesanato():
    return render_template('detalhes/cultural/artesanato.html')


@app.route('/detalhe/arcotriunfo')
def arcotriunfo():
    return render_template('detalhes/cultural/arcotriunfo.html')


@app.route('/detalhe/festa_padroeira')
def festa_padroeira():
    return render_template('detalhes/evento/festapadroeira.html')


@app.route('/detalhe/festasantana')
def festasantana():
    return render_template('detalhes/evento/festasantana.html')


@app.route('/detalhe/festarosario')
def festarosario():
    return render_template('detalhes/evento/festarosario.html')


@app.route('/detalhe/lugar/<int:lugar_id>')
@app.route('/imagem/lugar/<int:lugar_id>/<int:slot>')
def conteudo_dinamico_indisponivel(lugar_id, slot=None):
    abort(404)


@app.route('/buscar')
def buscar():
    termo = request.args.get('q', '').strip()
    termo_normalizado = unicodedata.normalize('NFKD', termo).encode('ascii', 'ignore').decode('ascii').casefold()
    resultados = []
    if termo_normalizado:
        for titulo, url, descricao in PAGINAS_MANUAIS:
            texto = unicodedata.normalize('NFKD', f'{titulo} {descricao}').encode('ascii', 'ignore').decode('ascii').casefold()
            if termo_normalizado in texto:
                resultados.append({'titulo': titulo, 'url': url, 'descricao': descricao})
    return render_template('buscar.html', termo=termo, resultados=resultados)


@app.route('/sugestao', methods=['GET', 'POST'])
def sugestao():
    if request.method == 'POST':
        flash('Sugest\u00f5es est\u00e3o temporariamente em WIP. Fale com a administra\u00e7\u00e3o para incluir conte\u00fado manualmente.', 'warning')
    return render_template('pagina_wip.html', titulo='Sugest\u00f5es em WIP', mensagem='Por enquanto, novos lugares e sugest\u00f5es s\u00e3o publicados manualmente nas p\u00e1ginas do site.')


@app.route('/login')
def login():
    return redirect(url_for('cadastro'))


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        matricula = request.form.get('matricula', '').strip()
        senha = request.form.get('password', '')
        matriculas_validas = {item.strip() for item in ADMIN_MATRICULAS if item and item.strip()}
        if matricula in matriculas_validas and senha == ADMIN_SENHA:
            session['admin_id'] = matricula
            session['admin_matricula'] = matricula
            return redirect(url_for('admin'))
        flash('Matr\u00edcula ou senha incorretas.', 'danger')
    return render_template('cadastro.html')


@app.route('/sair')
def sair():
    session.clear()
    return redirect(url_for('index'))


@app.route('/admin')
@login_requerido
def admin():
    return render_template('admin_manual.html', paginas=PAGINAS_MANUAIS)


@app.route('/adicionar-lugar', methods=['POST'])
@app.route('/admin/lugar/<int:lugar_id>/editar', methods=['POST'])
@app.route('/admin/lugar/<int:lugar_id>/remover', methods=['POST'])
@app.route('/admin/sugestao/<int:sugestao_id>/aprovar', methods=['POST'])
@app.route('/admin/sugestao/<int:sugestao_id>/recusar', methods=['POST'])
def escrita_antiga_indisponivel(lugar_id=None, sugestao_id=None):
    flash('Cadastro dinamico esta em WIP. Os lugares sao mantidos em paginas manuais.', 'warning')
    return redirect(url_for('admin') if 'admin_id' in session else url_for('cadastro'))


if __name__ == '__main__':
    app.run(debug=True)
