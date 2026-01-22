import streamlit as st
import time

# =====================================================
# CONFIGURAÇÃO
# =====================================================
st.set_page_config(
    page_title="IA Nutricional - NutriEdu",
    page_icon="🥗",
    layout="wide",
)

st.title("🥗 IA Nutricional — Recomendações Cognitivas")

# =====================================================
# RECUPERAR ESTADO COGNITIVO
# =====================================================
estado_cognitivo = st.session_state.get("estado_cognitivo")

if not estado_cognitivo:
    st.info(
        "ℹ️ Nenhum estado cognitivo detectado.\n\n"
        "👉 Execute primeiro a **IA Emocional**."
    )
    st.stop()

estado = estado_cognitivo["estado"]
ear = estado_cognitivo.get("ear", 0)
piscadas = estado_cognitivo.get("piscadas_min", 0)
confianca = estado_cognitivo.get("confianca", 1.0)

# =====================================================
# MODELO DE DECISÃO NUTRICIONAL (NÍVEL CIENTÍFICO)
# =====================================================
def recomendacao_nutricional(estado, ear, piscadas):
    if "Fadiga" in estado:
        return {
            "categoria": "🔋 Energia Sustentada",
            "justificativa": (
                "Indicadores de fadiga ocular e redução do EAR "
                "sugerem diminuição do estado de alerta."
            ),
            "alimentos": [
                "Banana com aveia (liberação gradual de glicose)",
                "Castanhas (magnésio e gorduras boas)",
                "Ovos (colina e proteína)",
                "Hidratação adequada",
            ],
        }

    if "Distração" in estado:
        return {
            "categoria": "⚡ Estímulo Cognitivo",
            "justificativa": (
                "Aumento na taxa de piscadas está associado à "
                "perda momentânea de atenção."
            ),
            "alimentos": [
                "Chocolate ≥70% cacau",
                "Café ou chá verde",
                "Oleaginosas",
                "Frutas vermelhas (antioxidantes)",
            ],
        }

    if "Foco" in estado:
        return {
            "categoria": "🎯 Otimização do Desempenho",
            "justificativa": (
                "Parâmetros oculares estáveis indicam estado "
                "de atenção sustentada."
            ),
            "alimentos": [
                "Ômega-3",
                "Abacate",
                "Ovos",
                "Proteína magra",
            ],
        }

    return {
        "categoria": "🥦 Manutenção Cognitiva",
        "justificativa": (
            "Estado cognitivo dentro da normalidade."
        ),
        "alimentos": [
            "Alimentação equilibrada",
            "Hidratação",
            "Vegetais variados",
        ],
    }

# =====================================================
# INTERFACE
# =====================================================
resultado = recomendacao_nutricional(estado, ear, piscadas)

st.subheader("🧠 Estado Cognitivo Atual")
st.success(estado)

st.subheader(f"🥗 Estratégia Nutricional: {resultado['categoria']}")

st.markdown("**Justificativa Cognitiva:**")
st.info(resultado["justificativa"])

st.markdown("**Recomendações Alimentares:**")
for item in resultado["alimentos"]:
    st.markdown(f"- {item}")

# =====================================================
# METADADOS
# =====================================================
st.caption(
    f"⏱️ Última atualização: "
    f"{time.strftime('%H:%M:%S', time.localtime(estado_cognitivo['timestamp']))}"
)
