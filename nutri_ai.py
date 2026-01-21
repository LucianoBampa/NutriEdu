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
    Você é uma IA nutricional para estudantes. Avalie o lanche abaixo:

    LANCHE: "{descricao_lanche}"

    Responda estritamente neste formato:

    Classificação: (Saudável / Moderado / Não recomendado)
    Explicação: (explique em até 3 linhas)
    Sugestão: (melhore o lanche, com opções baratas e acessíveis)
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
