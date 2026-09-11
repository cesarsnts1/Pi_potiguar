import mysql.connector
from config import (
    HOST, USER, PASSWORD, DATABASE, PORT,
    MYSQL_SSL_CA, MYSQL_SSL_VERIFY_CERT
)


def parametros_conexao(incluir_database=True):
    parametros = {
        "host": HOST,
        "port": PORT,
        "user": USER,
        "password": PASSWORD,
    }

    if incluir_database:
        parametros["database"] = DATABASE

    # Compatibilidade com MySQL online que exige conexão criptografada.
    if MYSQL_SSL_CA:
        parametros.update({
            "ssl_ca": MYSQL_SSL_CA,
            "ssl_verify_cert": MYSQL_SSL_VERIFY_CERT,
        })

    return parametros


def conectar():
    return mysql.connector.connect(**parametros_conexao(incluir_database=True))
