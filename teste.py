from db import conectar

conn = conectar()
cursor = conn.cursor()

cursor.execute("SELECT * FROM administradores")

for linha in cursor.fetchall():
    print(linha)

conn.close()