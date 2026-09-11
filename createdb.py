import mysql.connector
from config import HOST, PORT, USER, PASSWORD, DATABASE, AUTO_CREATE_DATABASE
from db import parametros_conexao

if AUTO_CREATE_DATABASE:
    conexao = mysql.connector.connect(**parametros_conexao(incluir_database=False))
    cursor = conexao.cursor()
    nome_banco_seguro = DATABASE.replace("`", "``")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{nome_banco_seguro}`")
    cursor.execute(f"USE `{nome_banco_seguro}`")
else:
    conexao = mysql.connector.connect(**parametros_conexao(incluir_database=True))
    cursor = conexao.cursor()


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
    receita LONGTEXT NULL,
    sugestao_lugar TEXT NULL,
    localizacao VARCHAR(200),
    latitude DECIMAL(10,7) NULL,
    longitude DECIMAL(10,7) NULL,

    nome_imagem VARCHAR(500),
    nome_imagem2 VARCHAR(500),
    nome_imagem3 VARCHAR(500),
    nome_imagem4 VARCHAR(500),

    tipo_imagem VARCHAR(50),
    imagem LONGBLOB,
    tipo_imagem2 VARCHAR(50),
    imagem2 LONGBLOB,
    tipo_imagem3 VARCHAR(50),
    imagem3 LONGBLOB,
    tipo_imagem4 VARCHAR(50),
    imagem4 LONGBLOB,

    categoria_id INT,

    FOREIGN KEY (categoria_id)
    REFERENCES categorias(id)
)
""")


# TABELA DE SUGESTOES ENVIADAS PELOS VISITANTES
# Atualiza bancos antigos sem apagar os dados já existentes.
cursor.execute("SHOW COLUMNS FROM pontos_turisticos")
colunas_pontos = {linha[0] for linha in cursor.fetchall()}

alteracoes_pontos = []
if 'resumo' not in colunas_pontos:
    alteracoes_pontos.append("ADD COLUMN resumo TEXT NULL AFTER nome")
if 'historia' not in colunas_pontos:
    alteracoes_pontos.append("ADD COLUMN historia LONGTEXT NULL AFTER descricao")
if 'curiosidades' not in colunas_pontos:
    alteracoes_pontos.append("ADD COLUMN curiosidades TEXT NULL AFTER historia")
if 'receita' not in colunas_pontos:
    alteracoes_pontos.append("ADD COLUMN receita LONGTEXT NULL AFTER curiosidades")
if 'sugestao_lugar' not in colunas_pontos:
    alteracoes_pontos.append("ADD COLUMN sugestao_lugar TEXT NULL AFTER receita")
if 'latitude' not in colunas_pontos:
    alteracoes_pontos.append("ADD COLUMN latitude DECIMAL(10,7) NULL AFTER localizacao")
if 'longitude' not in colunas_pontos:
    alteracoes_pontos.append("ADD COLUMN longitude DECIMAL(10,7) NULL AFTER latitude")
if 'nome_imagem2' not in colunas_pontos:
    alteracoes_pontos.append("ADD COLUMN nome_imagem2 VARCHAR(500) NULL AFTER nome_imagem")
if 'nome_imagem3' not in colunas_pontos:
    alteracoes_pontos.append("ADD COLUMN nome_imagem3 VARCHAR(500) NULL AFTER nome_imagem2")
if 'nome_imagem4' not in colunas_pontos:
    alteracoes_pontos.append("ADD COLUMN nome_imagem4 VARCHAR(500) NULL AFTER nome_imagem3")
if 'tipo_imagem' not in colunas_pontos:
    alteracoes_pontos.append("ADD COLUMN tipo_imagem VARCHAR(50) NULL AFTER nome_imagem4")
if 'imagem' not in colunas_pontos:
    alteracoes_pontos.append("ADD COLUMN imagem LONGBLOB NULL AFTER tipo_imagem")
if 'tipo_imagem2' not in colunas_pontos:
    alteracoes_pontos.append("ADD COLUMN tipo_imagem2 VARCHAR(50) NULL AFTER imagem")
if 'imagem2' not in colunas_pontos:
    alteracoes_pontos.append("ADD COLUMN imagem2 LONGBLOB NULL AFTER tipo_imagem2")
if 'tipo_imagem3' not in colunas_pontos:
    alteracoes_pontos.append("ADD COLUMN tipo_imagem3 VARCHAR(50) NULL AFTER imagem2")
if 'imagem3' not in colunas_pontos:
    alteracoes_pontos.append("ADD COLUMN imagem3 LONGBLOB NULL AFTER tipo_imagem3")
if 'tipo_imagem4' not in colunas_pontos:
    alteracoes_pontos.append("ADD COLUMN tipo_imagem4 VARCHAR(50) NULL AFTER imagem3")
if 'imagem4' not in colunas_pontos:
    alteracoes_pontos.append("ADD COLUMN imagem4 LONGBLOB NULL AFTER tipo_imagem4")

for alteracao in alteracoes_pontos:
    cursor.execute(f"ALTER TABLE pontos_turisticos {alteracao}")


# TABELA DOS LOCAIS ONDE UMA COMIDA PODE SER ENCONTRADA
# Uma comida pode ter até três sugestões cadastradas pelo painel.
cursor.execute("""
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
""")


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
# A antiga categoria gastronômica foi substituída por Comidas.
# Se o banco já existir, preservamos os registros antigos e apenas renomeamos
# a categoria, evitando que seja necessário recriar o banco.
cursor.execute("SELECT id FROM categorias WHERE nome = 'Comidas' ORDER BY id LIMIT 1")
comidas_existente = cursor.fetchone()
cursor.execute("SELECT id FROM categorias WHERE nome IN ('Gastronômico', 'Gastronomico') ORDER BY id LIMIT 1")
gastronomico_antigo = cursor.fetchone()

if gastronomico_antigo and not comidas_existente:
    cursor.execute("UPDATE categorias SET nome = 'Comidas' WHERE id = %s", (gastronomico_antigo[0],))
elif gastronomico_antigo and comidas_existente and gastronomico_antigo[0] != comidas_existente[0]:
    cursor.execute(
        "UPDATE pontos_turisticos SET categoria_id = %s WHERE categoria_id = %s",
        (comidas_existente[0], gastronomico_antigo[0])
    )
    cursor.execute(
        "UPDATE sugestoes SET categoria_id = %s WHERE categoria_id = %s",
        (comidas_existente[0], gastronomico_antigo[0])
    )
    cursor.execute("DELETE FROM categorias WHERE id = %s", (gastronomico_antigo[0],))

categorias_padrao = [
    "Histórico",
    "Cultural",
    "Comidas",
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
