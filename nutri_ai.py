from openai import OpenAI
import os
from dotenv import load_dotenv

# Carregar chave da API
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError(
        "❌ Erro: A chave OPENAI_API_KEY não está definida no arquivo .env")

client = OpenAI()


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
