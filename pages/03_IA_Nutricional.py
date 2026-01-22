import streamlit as st
from openai import OpenAI
from openai.errors import RateLimitError
import os

# Import corrigido
try:
    from database import conectar
except ImportError:
    st.warning("Módulo database não encontrado. Rodando sem persistência.")
    conectar = None

# Configuração da página
st.set_page_config(
    page_title="IA Nutricional - NutriEdu", page_icon="🥗", layout="wide"
)


def obter_cliente_openai():
    """Inicializa cliente OpenAI"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Tentar pegar do Streamlit secrets
        try:
            api_key = st.secrets.get("OPENAI_API_KEY")
        except Exception:
            pass

    if not api_key:
        st.error("❌ OPENAI_API_KEY não configurada!")
        st.info(
            """
        Configure a chave da API:
        1. Crie um arquivo `.env` com: OPENAI_API_KEY=sua_chave
        2. Ou adicione em `.streamlit/secrets.toml`
        """
        )
        st.stop()

    return OpenAI(api_key=api_key)


# Exemplo de cache simples para não gastar créditos desnecessariamente
cache_alimentos = {}


def analisar_alimento(alimento, idade):
    """Analisa um alimento usando IA com tratamento de quota e cache."""
    
    # Primeiro, checa se já analisou antes
    key = f"{alimento}_{idade}"
    if key in cache_alimentos:
        return cache_alimentos[key]

    client = obter_cliente_openai()  # sua função que retorna o client OpenAI

    # Adaptar prompt de acordo com a idade
    if idade < 6:
        nivel = "educação infantil"
        linguagem = "muito simples e lúdica"
    elif idade < 12:
        nivel = "ensino fundamental I"
        linguagem = "simples e educativa"
    elif idade < 15:
        nivel = "ensino fundamental II"
        linguagem = "clara e informativa"
    else:
        nivel = "ensino médio"
        linguagem = "detalhada e científica"

    prompt = f"""
Você é um nutricionista educacional para crianças e adolescentes.

Analise o seguinte alimento: {alimento}
Idade do aluno: {idade} anos ({nivel})

Forneça:
1. Classificação: Saudável ✅ / Moderado ⚠️ / Não recomendado ❌
2. Explicação em linguagem {linguagem}
3. Principais nutrientes (se aplicável)
4. Sugestão de melhoria ou alternativa mais saudável

Seja educativo, positivo e incentive hábitos saudáveis!
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um nutricionista educacional especializado em crianças e adolescentes.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )

        resultado = response.choices[0].message.content
        cache_alimentos[key] = resultado  # salva no cache
        return resultado

    except RateLimitError:
        st.warning("Quota da API da OpenAI esgotada. Tente novamente mais tarde.")
        return "Não foi possível analisar o alimento agora. 😔"

    except Exception as e:
        st.error(f"Erro inesperado ao analisar alimento: {e}")
        return None


def salvar_analise(alimento, idade, resultado):
    """Salva análise no banco de dados"""
    if conectar is None:
        return

    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO analises_nutricionais 
            (alimento, idade, resultado, data_analise)
            VALUES (?, ?, ?, datetime('now'))
        """,
            (alimento, idade, resultado),
        )

        conn.commit()
        conn.close()
    except Exception as e:
        st.warning(f"Não foi possível salvar: {e}")


def main():
    st.title("🥗 IA Nutricional - Avaliador de Alimentos")

    st.markdown(
        """
    Digite um alimento ou lanche e nossa IA irá avaliar se é saudável,
    explicar os nutrientes e sugerir alternativas melhores!
    """
    )

    # Layout em colunas
    col1, col2 = st.columns([2, 1])

    with col2:
        st.subheader("👤 Sobre você")
        idade = st.number_input(
            "Sua idade:",
            min_value=3,
            max_value=18,
            value=10,
            help="Ajudamos a explicação de acordo com sua idade",
        )

        # Mostrar faixa etária
        if idade < 6:
            st.info("🎨 Educação Infantil")
        elif idade < 12:
            st.info("📚 Ensino Fundamental I")
        elif idade < 15:
            st.info("📖 Ensino Fundamental II")
        else:
            st.info("🎓 Ensino Médio")

    with col1:
        st.subheader("🍎 Qual alimento você quer analisar?")

        # Input do alimento
        alimento = st.text_input(
            "Digite o nome do alimento ou lanche:",
            placeholder="Ex: chocolate, maçã, hambúrguer, suco de laranja...",
            help="Pode ser uma fruta, lanche, bebida, doce, etc.",
        )

        # Exemplos rápidos
        st.caption("💡 Exemplos rápidos:")
        col_ex1, col_ex2, col_ex3, col_ex4 = st.columns(4)

        with col_ex1:
            if st.button("🍎 Maçã"):
                alimento = "maçã"
        with col_ex2:
            if st.button("🍫 Chocolate"):
                alimento = "chocolate"
        with col_ex3:
            if st.button("🍕 Pizza"):
                alimento = "pizza"
        with col_ex4:
            if st.button("🥤 Refrigerante"):
                alimento = "refrigerante"

        # Botão de análise
        analisar = st.button(
            "🔍 Analisar Alimento",
            type="primary",
            use_container_width=True,
            disabled=not alimento,
        )

    # Análise
    if analisar and alimento:
        with st.spinner(f"🤖 Analisando {alimento}..."):
            resultado = analisar_alimento(alimento, idade)

            if resultado:
                # Mostrar resultado em um card
                st.divider()
                st.subheader(f"📊 Análise: {alimento.title()}")

                # Card com resultado
                st.markdown(
                    f"""
                <div style="
                    background-color: #f0f2f6;
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 5px solid #1f77b4;
                ">
                {resultado}
                </div>
                """,
                    unsafe_allow_html=True,
                )

                # Salvar no banco
                salvar_analise(alimento, idade, resultado)

                # Botão para nova análise
                st.divider()
                if st.button("🔄 Fazer nova análise"):
                    st.rerun()

    # Histórico (se disponível)
    if conectar is not None:
        with st.expander("📜 Ver histórico de análises"):
            try:
                conn = conectar()
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT alimento, idade, data_analise 
                    FROM analises_nutricionais 
                    ORDER BY data_analise DESC 
                    LIMIT 10
                """
                )

                historico = cursor.fetchall()
                conn.close()

                if historico:
                    st.write("**Últimas 10 análises:**")
                    for i, (alim, idad, data) in enumerate(historico, 1):
                        st.write(f"{i}. {alim} - Idade: {idad} - {data}")
                else:
                    st.info("Nenhuma análise anterior encontrada.")

            except Exception as e:
                st.warning(f"Erro ao carregar histórico: {e}")

    # Footer
    st.divider()
    st.caption(
        """
    💡 **Dica:** Esta é uma ferramenta educacional.
    Para orientação nutricional profissional, consulte um nutricionista.
    """
    )


if __name__ == "__main__":
    main()
