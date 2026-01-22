import streamlit as st

# =====================================================
# CONFIGURAÇÃO GLOBAL DO APP
# =====================================================
st.set_page_config(
    page_title="NutriEdu",
    page_icon="🥗",
    layout="wide",
)

# =====================================================
# HOME
# =====================================================
st.title("🥗 NutriEdu")
st.subheader("Plataforma Educacional Inteligente em Nutrição")

st.markdown(
    """
    O **NutriEdu** é uma plataforma educacional que integra:

    - 🧠 **IA Emocional** — análise de estado cognitivo via visão computacional  
    - 🥗 **IA Nutricional** — orientação alimentar personalizada  
    - 📊 **Painel Cognitivo** — acompanhamento de desempenho e foco  
    - 🧑‍🏫 **Painel do Professor** — visão pedagógica e analítica  
    - 🧪 **IA de Avaliação** — apoio em avaliações e aprendizado adaptativo  

    👉 Utilize o **menu lateral** para acessar os módulos.
    """
)

st.divider()

# =====================================================
# STATUS DO AMBIENTE
# =====================================================
with st.expander("ℹ️ Informações do Sistema"):
    st.write("🔹 Execução local recomendada para módulos com webcam")
    st.write("🔹 Streamlit Cloud limita acesso à câmera")
    st.write("🔹 Arquitetura modular baseada em páginas")

st.success("✅ Sistema carregado com sucesso")
