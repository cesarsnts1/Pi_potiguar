from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return redirect(url_for('cadastro'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('cadastro.html')

@app.route('/cultural')
def cultural():
    return render_template('cultural.html')

@app.route('/gastronomia')
def gastronomia():
    return render_template('gastronomia.html')

@app.route('/historia')
def historia():
    return render_template('historia.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/categorias')
def categorias():
    return redirect(url_for('index'))

@app.route('/detalhe/<slug>')
def detalhe(slug):
    return render_template(f'detalhes/{slug}.html')


# ==========================================================================
# NOVAS ROTAS: ADMINISTRAÇÃO (MEMÓRIA POTIGUAR)
# ==========================================================================

@app.route('/admin')
def admin():
    """Exibe o painel administrativo para adicionar novos lugares"""
    return render_template('admin.html')

@app.route('/adicionar-lugar', methods=['POST'])
def adicionar_lugar():
    """Recebe os dados do formulário do admin.html via POST"""
    # Coleta de dados vindos do formulário pelo atributo 'name' do input
    nome = request.form.get('nome')
    categoria = request.form.get('categoria')
    endereco = request.form.get('endereco')
    descricao = request.form.get('descricao')
    imagem = request.form.get('imagem')

    # [Aqui futuramente você adicionará o código para salvar no Banco de Dados]
    print(f"Novo lugar recebido: {nome} | Categoria: {categoria}")

    # Após processar/salvar, redireciona de volta para o painel com sucesso
    # Ou altere para redirect(url_for('index')) se preferir voltar para a Home
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    """Rota para efetuar o logout e limpar a sessão"""
    # [Aqui futuramente você limpará a session do usuário]
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)


    