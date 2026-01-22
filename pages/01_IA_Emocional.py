import os
import time
import streamlit as st
import numpy as np

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(
    page_title="IA Emocional - NutriEdu",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 IA Emocional — Detector de Estado Cognitivo")

# =====================================================
# DETECÇÃO DE AMBIENTE
# =====================================================
IS_CLOUD = os.getenv("STREAMLIT_SERVER_RUNNING") == "1"

if IS_CLOUD:
    st.warning(
        "🚫 **Módulo indisponível no Streamlit Cloud**\n\n"
        "Este recurso utiliza webcam e visão computacional.\n\n"
        "👉 Execute o projeto localmente para utilizar a IA Emocional."
    )
    st.stop()

# =====================================================
# IMPORTS LOCAIS (EXECUÇÃO LOCAL)
# =====================================================
import cv2
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# =====================================================
# FUNÇÕES MATEMÁTICAS
# =====================================================
def calcular_ear(landmarks, idx):
    p1 = np.array([landmarks[idx[1]].x, landmarks[idx[1]].y])
    p2 = np.array([landmarks[idx[5]].x, landmarks[idx[5]].y])
    p3 = np.array([landmarks[idx[0]].x, landmarks[idx[0]].y])
    p4 = np.array([landmarks[idx[3]].x, landmarks[idx[3]].y])

    vertical = np.linalg.norm(p1 - p2)
    horizontal = np.linalg.norm(p3 - p4)

    if horizontal == 0:
        return 0.0

    return float(vertical / horizontal)


def classificar_estado(ear, pisc_min):
    if ear < 0.18:
        return "😴 Fadiga", "Sinais consistentes de sonolência."
    if pisc_min > 25:
        return "😵 Distração", "Piscadas excessivas detectadas."
    if ear > 0.28:
        return "😊 Foco", "Atenção visual estável."
    return "😐 Neutro", "Estado cognitivo regular."

# =====================================================
# INTERFACE
# =====================================================
st.markdown(
    """
    Esta ferramenta utiliza **Visão Computacional** e **IA Cognitiva**
    para inferir o estado emocional a partir de padrões oculares.
    """
)

col_cam, col_ctrl = st.columns([3, 1])

with col_ctrl:
    st.subheader("⚙️ Controles")

    iniciar = st.button("▶️ Iniciar Análise")
    parar = st.button("⏹️ Parar")

    st.divider()

    ear_limiar = st.slider(
        "Sensibilidade (EAR)",
        0.15,
        0.35,
        0.25,
        step=0.01,
    )

with col_cam:
    video_box = st.empty()
    estado_box = st.empty()
    metric_box = st.empty()

# =====================================================
# LOOP PRINCIPAL
# =====================================================
if iniciar and not parar:
    cap = cv2.VideoCapture(0)

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    ) as face_mesh:

        ear_hist = []
        piscadas = 0
        inicio = time.time()

        while cap.isOpened() and not parar:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = face_mesh.process(rgb)

            if result.multi_face_landmarks:
                for face in result.multi_face_landmarks:
                    lm = face.landmark

                    ear_esq = calcular_ear(
                        lm, [33, 160, 158, 133, 153, 144]
                    )
                    ear_dir = calcular_ear(
                        lm, [362, 385, 387, 263, 373, 380]
                    )

                    ear = (ear_esq + ear_dir) / 2
                    ear_hist.append(ear)

                    if ear < ear_limiar:
                        piscadas += 1

                    mp_drawing.draw_landmarks(
                        frame,
                        face,
                        mp_face_mesh.FACEMESH_CONTOURS,
                    )

            video_box.image(
                frame,
                channels="BGR",
                use_container_width=True,
            )

            if len(ear_hist) >= 30:
                ear_medio = float(np.mean(ear_hist[-30:]))
                pisc_min = int(
                    piscadas / max((time.time() - inicio) / 60, 1)
                )

                estado, msg = classificar_estado(
                    ear_medio,
                    pisc_min,
                )

                st.session_state["estado_cognitivo"] = {
                    "estado": estado,
                    "ear": ear_medio,
                    "piscadas_min": pisc_min,
                    "timestamp": time.time(),
                }

                metric_box.metric(
                    "EAR Médio",
                    f"{ear_medio:.3f}",
                )
                
                estado_box.info(
                    f"**{estado}**\n\n{msg}",
                )

            time.sleep(0.03)

    cap.release()
