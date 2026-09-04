import mysql.connector
from config import HOST, PORT, USER, PASSWORD, DATABASE


# A conexao inicial nao informa o DATABASE porque este arquivo tambem
# e responsavel por criar o banco caso ele ainda nao exista.
conexao = mysql.connector.connect(
    host=HOST,
    port=PORT,
    user=USER,
    password=PASSWORD
)

cursor = conexao.cursor()


# CRIAR BANCO
# DATABASE vem de config.py, assim senha, porta, usuario e nome do banco
# ficam configurados em um unico lugar.
nome_banco_seguro = DATABASE.replace("`", "``")
cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{nome_banco_seguro}`")
cursor.execute(f"USE `{nome_banco_seguro}`")


# TABELA CATEGORIAS
cursor.execute("""
CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
)
""")


# TABELA PONTOS TURISTICOS
cursor.execute("""
CREATE TABLE IF NOT EXISTS pontos_turisticos (
    id INT AUTO_INCREMENT PRIMARY KEY,

    nome VARCHAR(150) NOT NULL,
    resumo TEXT NULL,
    descricao TEXT NOT NULL,
    historia LONGTEXT NULL,
    curiosidades TEXT NULL,
    localizacao VARCHAR(200),

    nome_imagem VARCHAR(500),
    nome_imagem2 VARCHAR(500),
    nome_imagem3 VARCHAR(500),
    nome_imagem4 VARCHAR(500),
    tipo_imagem VARCHAR(50),
    imagem LONGBLOB,

    categoria_id INT,

    FOREIGN KEY (categoria_id)
    REFERENCES categorias(id)
)
""")


# TABELA DE SUGESTOES ENVIADAS PELOS VISITANTES
cursor.execute("""
CREATE TABLE IF NOT EXISTS sugestoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    categoria_id INT NULL,
    localizacao VARCHAR(200) NOT NULL,
    descricao TEXT NOT NULL,
    imagem VARCHAR(500),
    nome_sugerente VARCHAR(150),
    contato VARCHAR(180),
    status VARCHAR(30) NOT NULL DEFAULT 'Pendente',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
)
""")


# As credenciais do painel ficam em config.py
# (ADMIN_MATRICULAS e ADMIN_SENHA).
 # Mantem os nomes acentuados que o site ja utiliza.
categorias_padrao = [
    "Histórico",
    "Cultural",
    "Gastronômico",
    "Eventos"
]

for categoria in categorias_padrao:
    cursor.execute(
        "SELECT id FROM categorias WHERE nome = %s",
        (categoria,)
    )

    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO categorias (nome) VALUES (%s)",
            (categoria,)
        )


conexao.commit()
cursor.close()
conexao.close()

print(f"Banco '{DATABASE}' criado/verificado com sucesso!")
print(f"MySQL: {USER}@{HOST}:{PORT}")
