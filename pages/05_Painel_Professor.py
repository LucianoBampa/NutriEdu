# =====================================================
# PAINEL DO PROFESSOR - NUTRIEDU
# =====================================================

import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(
    page_title="Painel do Professor - NutriEdu",
    page_icon="🧑‍🏫",
    layout="wide"
)

st.title("🧑‍🏫 Painel do Professor")
st.caption("Monitoramento cognitivo e nutricional baseado em IA")

# =====================================================
# SIMULAÇÃO DE DADOS (SUBSTITUÍVEL POR BANCO)
# =====================================================

def carregar_dados():
    data = {
        "Aluno": ["Ana", "Bruno", "Carlos", "Daniela", "Eduardo"],
        "Estado_Cognitivo": ["Focado", "Normal", "Fadiga", "Distraído", "Focado"],
        "Nivel_Foco": [0.78, 0.55, 0.32, 0.40, 0.82],
        "Fadiga": [0.20, 0.40, 0.75, 0.60, 0.18],
        "Alimentacao_Pre_Aula": ["Adequada", "Inadequada", "Inadequada", "Adequada", "Adequada"],
        "Hidratacao": ["Boa", "Baixa", "Baixa", "Boa", "Boa"]
    }
    return pd.DataFrame(data)

df = carregar_dados()

# =====================================================
# DASHBOARD GERAL
# =====================================================
st.subheader("📊 Visão Geral da Turma")

col1, col2, col3, col4 = st.columns(4)

col1.metric("👥 Alunos Ativos", len(df))
col2.metric("😊 Focados", (df["Estado_Cognitivo"] == "Focado").sum())
col3.metric("😴 Em Fadiga", (df["Estado_Cognitivo"] == "Fadiga").sum())
col4.metric("😵 Distraídos", (df["Estado_Cognitivo"] == "Distraído").sum())

# =====================================================
# GRÁFICOS
# =====================================================
st.subheader("📈 Indicadores Cognitivos")

g1, g2 = st.columns(2)

with g1:
    st.bar_chart(df.set_index("Aluno")["Nivel_Foco"])

with g2:
    st.bar_chart(df.set_index("Aluno")["Fadiga"])

# =====================================================
# CORRELAÇÃO NUTRIÇÃO × COGNIÇÃO
# =====================================================
st.subheader("🥗 Correlação Nutricional")

nutricao_map = {"Adequada": 1, "Inadequada": 0}
df["Alimentacao_Num"] = df["Alimentacao_Pre_Aula"].map(nutricao_map)

correlacao = df["Nivel_Foco"].corr(df["Alimentacao_Num"])

st.info(
    f"📌 Correlação entre alimentação adequada e foco cognitivo: **{correlacao:.2f}**"
)

# =====================================================
# MONITORAMENTO INDIVIDUAL
# =====================================================
st.subheader("👤 Monitoramento Individual")

aluno_sel = st.selectbox("Selecione um aluno:", df["Aluno"])

dados_aluno = df[df["Aluno"] == aluno_sel].iloc[0]

c1, c2, c3 = st.columns(3)

c1.metric("🧠 Estado Cognitivo", dados_aluno["Estado_Cognitivo"])
c2.metric("🎯 Nível de Foco", f"{dados_aluno['Nivel_Foco']*100:.0f}%")
c3.metric("😴 Fadiga", f"{dados_aluno['Fadiga']*100:.0f}%")

st.write("🍽️ Alimentação pré-aula:", dados_aluno["Alimentacao_Pre_Aula"])
st.write("💧 Hidratação:", dados_aluno["Hidratacao"])

# =====================================================
# ALERTAS INTELIGENTES (IA HEURÍSTICA)
# =====================================================
st.subheader("🚨 Alertas Inteligentes")

alertas = []

if dados_aluno["Nivel_Foco"] < 0.45:
    alertas.append("⚠️ Baixo nível de foco detectado.")

if dados_aluno["Fadiga"] > 0.65:
    alertas.append("⚠️ Alto nível de fadiga.")

if dados_aluno["Alimentacao_Pre_Aula"] == "Inadequada":
    alertas.append("⚠️ Alimentação inadequada pode impactar o desempenho.")

if alertas:
    for alerta in alertas:
        st.warning(alerta)
else:
    st.success("✅ Nenhum alerta crítico detectado.")

# =====================================================
# SUGESTÕES PEDAGÓGICAS AUTOMÁTICAS
# =====================================================
st.subheader("💡 Sugestões Pedagógicas")

if dados_aluno["Fadiga"] > 0.6:
    st.info("🧠 Sugere-se pausa ativa ou atividade lúdica.")

if dados_aluno["Nivel_Foco"] < 0.4:
    st.info("📚 Recomenda-se revisão do conteúdo ou abordagem multimodal.")

if dados_aluno["Alimentacao_Pre_Aula"] == "Inadequada":
    st.info("🥗 Orientar sobre alimentação antes das aulas.")

# =====================================================
# RELATÓRIOS
# =====================================================
st.subheader("📑 Relatórios")

if st.button("📥 Gerar Relatório da Turma"):
    st.success("Relatório gerado com sucesso!")
    st.dataframe(df)

# =====================================================
# ÉTICA E PRIVACIDADE
# =====================================================
st.divider()
st.caption(
    "🔒 Os dados apresentados são anonimizados e utilizados exclusivamente "
    "para fins educacionais, respeitando princípios éticos e a LGPD."
)
