import streamlit as st
import pandas as pd
from database import conectar


st.title('📊 Painel Cognitivo')
usuario_id = st.number_input('ID do aluno', min_value=1, step=1)
if usuario_id:
    conn = sqlite3.connect('nutriedu.db')
    df = pd.DataFrame(conn.execute('SELECT avaliacao,resposta_ia,data FROM historico_avaliacoes WHERE usuario_id=?', (usuario_id,)).fetchall(), columns=['Pergunta','Resposta','Data'])
    if df.empty:
        st.info('Sem histórico')
    else:
        st.dataframe(df)
