import streamlit as st
from openai import OpenAI


st.title('👩‍🏫 IA Tutora')
pergunta = st.text_area('Pergunta para a tutora:')


USE_OPENAI = 'OPENAI_API_KEY' in st.secrets
if USE_OPENAI:
    client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])


def gerar_resposta_local(q):
    return 'Expliquei em linguagem simples: (versão local) ' + q[:200]


if st.button('Perguntar'):
    if not pergunta.strip():
        st.warning('Digite uma pergunta')
    else:
        if USE_OPENAI:
            resp = client.chat.completions.create(model='gpt-4o-mini', messages=[{'role':'system','content':'Você é uma tutora pedagógica clara.'},{'role':'user','content':pergunta}])
            resposta = resp.choices[0].message.content
        else:
            resposta = gerar_resposta_local(pergunta)
        st.success(resposta)