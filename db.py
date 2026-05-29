import mysql.connector
from config import HOST, USER, PASSWORD, DATABASE


def conectar():
    conexao = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )

    return conexao