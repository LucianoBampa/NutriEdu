st.title("🧑‍🏫 Painel Professor")
st.markdown(
    "Acesse dados dos alunos e crie usuários (em versão hackathon, mantenha simples)."
)
if st.button("Criar usuário demo"):
    import sqlite3

    conn = sqlite3.connect("nutriedu.db")
    conn.execute(
        "INSERT INTO usuarios (nome,idade,turma) VALUES (?,?,?)",
        ("Aluno Demo", 15, "9A"),
    )
    conn.commit()
    conn.close()
    st.success("Usuário demo criado")
