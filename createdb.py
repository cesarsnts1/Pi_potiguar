import mysql.connector
from werkzeug.security import generate_password_hash

senha = generate_password_hash("281207")

HOST = "localhost"
PORT = 3307
USER = "root"
PASSWORD = ""


conexao = mysql.connector.connect(
    host=HOST,
    port=PORT,
    user=USER,
    password=PASSWORD
)

cursor = conexao.cursor()


# CRIAR BANCO
cursor.execute("CREATE DATABASE IF NOT EXISTS pi_potiguar")

cursor.execute("USE pi_potiguar")


# TABELA CATEGORIAS
cursor.execute("""
CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
)
""")


# TABELA PONTOS TURISTICOS
cursor.execute("""
CREATE TABLE IF NOT EXISTS pontos_turisticos (
    id INT AUTO_INCREMENT PRIMARY KEY,

    nome VARCHAR(150) NOT NULL,
    descricao TEXT NOT NULL,
    localizacao VARCHAR(200),

    nome_imagem VARCHAR(150),
    tipo_imagem VARCHAR(50),
    imagem LONGBLOB,

    categoria_id INT,

    FOREIGN KEY (categoria_id)
    REFERENCES categorias(id)
)
""")


# TABELA ADMINISTRADORES
cursor.execute("""
CREATE TABLE IF NOT EXISTS administradores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(100) NOT NULL,
    senha VARCHAR(255) NOT NULL
)
""")


# SENHA HASH
senha_hash = generate_password_hash("281207")


# INSERT ADMIN
cursor.execute("""
INSERT INTO administradores (usuario, senha)
VALUES (%s, %s)
""", (
    "icaro.e@escolar.ifrn.edu.br",
    "scrypt:32768:8:1$t57B6qMJ9d8IpOJm$07c05063f538f16fe85da54bd37d99667386d8443e6f1d0f3756a5c6168ab13ab04eaf9cbe7045a1a5c100b895484d922e80d01a6c6ad20a4dfbb831f8f3537b"
))


# INSERT CATEGORIA
cursor.execute("""
INSERT INTO categorias (nome)
VALUES (%s)
""", (
    "",
))


# INSERT PONTOS TURISTICOS
cursor.execute("""
INSERT INTO pontos_turisticos
(
    nome,
    descricao,
    localizacao,
    nome_imagem,
    tipo_imagem,
    imagem,
    categoria_id
)
VALUES
(%s, %s, %s, %s, %s, %s, %s)
""", (
    "",
    "",
    "",
    "",
    "",
    None,
    1
))


conexao.commit()

print("Banco de dados criado com sucesso!")