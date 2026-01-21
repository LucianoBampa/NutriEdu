import os
import streamlit as st
from openai import OpenAI

# Tenta pegar do Streamlit Cloud
api_key = st.secrets.get("OPENAI_API_KEY", None)

# Fallback local (.env)
if api_key is None:
    api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ OPENAI_API_KEY não configurada")

client = OpenAI(api_key=api_key)


def avaliar_lanche(descricao_lanche: str) -> str:
    """
    Envia o lanche para a IA avaliar (saudável / moderado / não recomendado),
    dando explicação simples e sugestões.
    """

    prompt = f"""
    Você é um(a) tutor(a) nutricional amigável para crianças e adolescentes.

    Seu objetivo é ensinar alimentação saudável de forma simples, positiva
    e sem julgamentos.

    Analise o lanche abaixo:

    LANCHE: "{descricao_lanche}"

    Responda exatamente neste formato:

    Classificação: (Saudável / Moderado / Não recomendado)

    Explicação:
    Explique em linguagem simples, como se estivesse falando com um estudante,
    em até 3 linhas.

    Sugestão:
    Dê uma dica prática e acessível para melhorar esse lanche,
    usando alimentos comuns do dia a dia.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    conteudo = response.choices[0].message.content

    if conteudo is None:
        return "⚠️ Não foi possível gerar a avaliação nutricional no momento."

    return conteudo
