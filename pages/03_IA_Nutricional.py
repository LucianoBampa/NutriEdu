import streamlit as st
import sqlite3
from datetime import datetime
from database import conectar if False else None


st.title('🥗 IA Nutricional')
usuario_id = st.number_input('ID do usuário', min_value=1, step=1)
descricao = st.text_area('Descreva a refeição ou problema:')
last_emotion = st.session_state.get('last_emotion','Neutro')
if st.button('Analisar'):
    # fallback local
    texto = descricao.lower()
    base = 'Sugestão: reduza ultraprocessados; aumente fibras e hidratação.'
    if 'ansiedade' in texto or last_emotion in ('Triste','Bravo'):
        base += ' Priorize lanches ricos em triptofano (iogurte + banana).'
    st.success(base)
    # salvar local (opcional) -- deixei fora por simplicidade