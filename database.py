import sqlite3


DB = 'nutriedu.db'


def conectar():
    return sqlite3.connect(DB, check_same_thread=False)


def criar_tabelas():
    conn = conectar()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            idade INTEGER,
            turma TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS historico_avaliacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            avaliacao TEXT,
            resposta_ia TEXT,
            emocao_detectada TEXT,
            data TEXT
        )
    ''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    criar_tabelas()
    print('Tabelas criadas.')
