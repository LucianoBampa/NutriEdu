import streamlit as st
import pandas as pd
import sqlite3  # ADICIONADO - estava faltando

# Configuração da página
st.set_page_config(
    page_title="Painel Cognitivo - NutriEdu", page_icon="📊", layout="wide"
)


def conectar_bd():
    """Conecta ao banco de dados"""
    try:
        conn = sqlite3.connect("nutriedu.db")
        # Criar tabela se não existir
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS desempenho_cognitivo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER,
                nome TEXT,
                idade INTEGER,
                disciplina TEXT,
                nota REAL,
                estado_emocional TEXT,
                data_avaliacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        conn.commit()
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar ao banco: {e}")
        return None


def carregar_dados():
    """Carrega dados do banco"""
    conn = conectar_bd()
    if conn is None:
        return pd.DataFrame()

    try:
        query = """
            SELECT
                nome,
                idade,
                disciplina,
                nota,
                estado_emocional,
                data_avaliacao
            FROM desempenho_cognitivo
            ORDER BY data_avaliacao DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.warning(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()


def inserir_dados_exemplo():
    """Insere dados de exemplo para demonstração"""
    conn = conectar_bd()
    if conn is None:
        return

    try:
        dados_exemplo = [
            (1, "Ana Silva", 10, "Matemática", 8.5, "Focado"),
            (1, "Ana Silva", 10, "Português", 9.0, "Focado"),
            (2, "Bruno Costa", 12, "Matemática", 7.0, "Distraído"),
            (2, "Bruno Costa", 12, "Ciências", 8.0, "Normal"),
            (3, "Carla Santos", 14, "História", 9.5, "Focado"),
            (3, "Carla Santos", 14, "Geografia", 8.8, "Focado"),
        ]

        conn.executemany(
            """
            INSERT INTO desempenho_cognitivo
            (aluno_id, nome, idade, disciplina, nota, estado_emocional)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            dados_exemplo,
        )

        conn.commit()
        conn.close()
        st.success("✅ Dados de exemplo inseridos!")
    except Exception as e:
        st.error(f"Erro ao inserir dados: {e}")


def main():
    st.title("📊 Painel Cognitivo - Desempenho dos Alunos")

    st.markdown(
        """
    Visualize o desempenho acadêmico e estado emocional dos alunos
    em tempo real.
    """
    )

    # Botões de controle
    col1, col2, col3 = st.columns([2, 1, 1])

    with col2:
        if st.button("🔄 Atualizar Dados"):
            st.rerun()

    with col3:
        if st.button("➕ Dados de Exemplo"):
            inserir_dados_exemplo()
            st.rerun()

    # Carregar dados
    df = carregar_dados()

    if df.empty:
        st.info(
            """
        📝 Nenhum dado encontrado.
            Clique em **'Dados de Exemplo'** para ver uma demonstração
            ou comece a usar as outras páginas do sistema.
            """
        )
        return

    # Métricas gerais
    st.subheader("📈 Visão Geral")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total de Alunos", df["nome"].nunique())

    with col2:
        st.metric("Média Geral", f"{df['nota'].mean():.2f}")

    with col3:
        focados = (df["estado_emocional"] == "Focado").sum()
        st.metric("Alunos Focados", focados)

    with col4:
        total_avaliacoes = len(df)
        st.metric("Total de Avaliações", total_avaliacoes)

    # Tabela de dados
    st.divider()
    st.subheader("📋 Dados Detalhados")

    # Filtros
    col1, col2 = st.columns(2)

    with col1:
        alunos = ["Todos"] + sorted(df["nome"].unique().tolist())
        aluno_selecionado = st.selectbox("Filtrar por aluno:", alunos)

    with col2:
        disciplinas = ["Todas"] + sorted(df["disciplina"].unique().tolist())
        disciplina_selecionada = st.selectbox("Filtrar por disciplina:", disciplinas)

    # Aplicar filtros
    df_filtrado = df.copy()

    if aluno_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["nome"] == aluno_selecionado]

    if disciplina_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado["disciplina"] == disciplina_selecionada]

    # Mostrar tabela
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    # Análise por aluno
    if aluno_selecionado != "Todos":
        st.divider()
        st.subheader(f"📊 Análise: {aluno_selecionado}")

        dados_aluno = df[df["nome"] == aluno_selecionado]

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Notas por Disciplina:**")
            for _, row in dados_aluno.iterrows():
                st.write(f"- {row['disciplina']}: {row['nota']}")

        with col2:
            st.write("**Estado Emocional:**")
            estados = dados_aluno["estado_emocional"].value_counts()
            for estado, count in estados.items():
                st.write(f"- {estado}: {count}x")

    # Gráfico simples (opcional)
    if len(df_filtrado) > 0:
        st.divider()
        st.subheader("📊 Visualização")

        # Gráfico de barras usando Streamlit nativo
        st.bar_chart(
            df_filtrado.groupby("disciplina")["nota"].mean(), use_container_width=True
        )

    # Footer
    st.divider()
    st.caption(
        """
    💡 **Dica:** Os dados são atualizados em tempo real conforme
    os alunos usam o sistema.
    """
    )


if __name__ == "__main__":
    main()
