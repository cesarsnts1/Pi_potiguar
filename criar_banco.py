import sqlite3

def inicializar_banco():
    # Conecta ao arquivo do banco (se não existir, ele cria automaticamente)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # 1. Cria a tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    ''')

    # Dados dos usuários acadêmicos fornecidos
    usuarios_iniciais = [
        ('20231101110049', 'Lídia Maria de Medeiros Santos', 's.lidia@academico.ifrn.edu.br', 'ifrn2026'),
        ('20231101110015', 'César da Silva Santos', 'santos.cesar1@academico.ifrn.edu.br', 'ifrn2026')
    ]

    # 2. Insere os usuários se eles já não existirem
    for matricula, nome, email, senha in usuarios_iniciais:
        try:
            cursor.execute('''
                INSERT INTO usuarios (matricula, nome, email, senha)
                VALUES (?, ?, ?, ?)
            ''', (matricula, nome, email, senha))
        except sqlite3.IntegrityError:
            # Ignora se o usuário já tiver sido inserido antes
            pass

    conn.commit()
    conn.close()
    print("Banco de dados 'database.db' criado e usuários cadastrados com sucesso!")

if __name__ == '__main__':
    inicializar_banco()