from db import conectar

try:
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE()")
    banco = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pontos_turisticos")
    total = cursor.fetchone()[0]
    print("Conexão com o MySQL: OK")
    print(f"Banco atual: {banco}")
    print(f"Pontos/comidas cadastrados: {total}")
    cursor.close()
    conn.close()
except Exception as erro:
    print("Falha ao conectar ao MySQL compartilhado:")
    print(erro)
