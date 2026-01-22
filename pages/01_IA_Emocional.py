import streamlit as st
import sys

st.set_page_config(
    page_title="IA Emocional",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 IA Emocional - Detector de Estado Cognitivo")

# =====================================================
# FUNÇÃO: verifica se está rodando local ou cloud
# =====================================================
def rodando_no_cloud():
    return not sys.platform.startswith("win") and not sys.platform.startswith("darwin")

# =====================================================
# TENTATIVA DE IMPORTAÇÃO (somente local)
# =====================================================
if rodando_no_cloud():
    st.warning("⚠️ Este recurso não é suportado no Streamlit Cloud.")
    st.info(
        """
        🔒 **Limitações do ambiente Cloud**
        - Webcam não disponível
        - MediaPipe não suportado
        
        👉 Execute este módulo **localmente** para usar o detector emocional.
        """
    )

    st.markdown("### 💻 Como executar localmente:")
    st.code(
        "pip install opencv-python mediapipe streamlit\n"
        "streamlit run app.py",
        language="bash"
    )

    st.stop()

# =====================================================
# IMPORTAÇÕES LOCAIS (SÓ EXECUTAM NO PC)
# =====================================================
try:
    import cv2
    import mediapipe as mp
    import numpy as np
except Exception as e:
    st.error("Erro ao carregar bibliotecas locais.")
    st.exception(e)
    st.stop()

# =====================================================
# MEDIA PIPE
# =====================================================
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

# =====================================================
# FUNÇÃO: Classificação simples de estado cognitivo
# =====================================================
def classificar_estado(piscar, abertura_olhos):
    if piscar > 20:
        return "😴 Fadiga"
    elif abertura_olhos < 0.015:
        return "😐 Baixa Atenção"
    else:
        return "🙂 Normal"

# =====================================================
# INTERFACE
# =====================================================
st.success("✅ Ambiente local detectado. Webcam habilitada.")

iniciar = st.button("📷 Iniciar Detecção")

if iniciar:
    cap = cv2.VideoCapture(0)

    stframe = st.empty()
    status = st.empty()

    piscadas = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultado = face_mesh.process(rgb)

        abertura_olhos = 0.02  # valor padrão

        if resultado.multi_face_landmarks:
            landmarks = resultado.multi_face_landmarks[0].landmark

            olho_sup = landmarks[159].y
            olho_inf = landmarks[145].y
            abertura_olhos = abs(olho_sup - olho_inf)

            if abertura_olhos < 0.01:
                piscadas += 1

        estado = classificar_estado(piscadas, abertura_olhos)

        cv2.putText(
            frame,
            f"Estado: {estado}",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        stframe.image(frame, channels="BGR")
        status.markdown(f"### Estado Cognitivo: **{estado}**")

    cap.release()
