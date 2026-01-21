# =========================
# IMPORTAÇÕES
# =========================
import streamlit as st
from dotenv import load_dotenv

from nutri_ai import avaliar_lanche
# from emocao import executar_emocoes # Desativado para implantação sem webcam

EXECUTAR_EMOCAO = False

try:
    from emocao import executar_emocoes
    EXECUTAR_EMOCAO = True
except Exception:
    EXECUTAR_EMOCAO = False


# =========================
# CONFIGURAÇÃO INICIAL
# =========================
load_dotenv()

st.set_page_config(
    page_title="NutriEdu AI",
    page_icon="🍎",
    layout="wide"
)


# =========================
# ESTADO GLOBAL
# =========================
if "emocao_detectada" not in st.session_state:
    st.session_state.emocao_detectada = None

# =========================
# MAPA EMOÇÃO → NUTRIÇÃO
# =========================
MAPA_EMOCAO_NUTRICAO = {
    "Feliz": "Manter alimentação equilibrada e saudável.",
    "Neutro": "Reforçar hábitos alimentares consistentes.",
    "Triste": "Sugerir alimentos que aumentem energia e bem-estar.",
    "Cansado": "Indicar lanches leves e energéticos.",
    "Estressado": "Priorizar alimentos calmantes e naturais."
}

# =========================
# SIDEBAR
# =========================
st.sidebar.image("images/logo1.png", width=180)
st.sidebar.title("NutriEdu AI")
st.sidebar.markdown(
    """
    Plataforma educacional com:
    - 🧠 Análise emocional
    - 🍎 Avaliação nutricional
    - 📊 Apoio ao aprendizado
    """
)


# =========================
# TÍTULO PRINCIPAL
# =========================
st.title("🍎 NutriEdu AI")
st.subheader("Educação nutricional inteligente para estudantes")


# =========================
# SEÇÃO – EMOÇÃO
# =========================
st.markdown("## 😊 Análise Emocional")

# if st.button("📷 Detectar emoção"):
#     with st.spinner("Analisando emoção..."):
#         emocao = executar_emocoes()
#         st.session_state.emocao_detectada = emocao
# desativado para implantação sem webcam

if st.button("📷 Detectar emoção"):
    if not EXECUTAR_EMOCAO:
        st.warning("⚠️ Análise emocional disponível apenas em execução local.")
    else:
        with st.spinner("Analisando emoção..."):
            emocao = executar_emocoes()
            st.session_state.emocao_detectada = emocao

if st.session_state.emocao_detectada:
    emocao = st.session_state.emocao_detectada
    contexto = MAPA_EMOCAO_NUTRICAO.get(
        emocao,
        "Manter alimentação equilibrada."
    )

    st.success(f"Emoção detectada: **{emocao}**")
    st.info(f"🍽️ Orientação nutricional: {contexto}")

# =========================
# SEÇÃO – NUTRIÇÃO
# =========================
st.markdown("## 🥪 Avaliação Nutricional")

descricao_lanche = st.text_area(
    "Descreva o lanche consumido:",
    placeholder="Ex: pão com manteiga e café com açúcar"
)

if st.button("🍏 Avaliar lanche"):
    if not descricao_lanche.strip():
        st.warning("⚠️ Por favor, descreva o lanche.")
    else:
        with st.spinner("Consultando IA nutricional..."):
            resultado = avaliar_lanche(descricao_lanche)

        st.markdown("### 📋 Resultado da Avaliação")
        st.markdown(resultado)


# =========================
# RODAPÉ
# =========================
st.markdown("---")
st.caption("NutriEdu AI • Projeto educacional com IA • Hackathon")
