import mysql.connector
from config import HOST, USER, PASSWORD, DATABASE, PORT


def conectar():
    conexao = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )

    return conexao