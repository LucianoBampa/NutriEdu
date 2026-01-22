import os
import streamlit as st
import numpy as np
import time

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(
    page_title="IA Emocional - NutriEdu",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 IA Emocional - Detector de Estado Cognitivo")

# =====================================================
# DETECÇÃO DE AMBIENTE
# =====================================================
IS_CLOUD = os.getenv("STREAMLIT_SERVER_RUNNING") == "1"

if IS_CLOUD:
    st.warning(
        "🚫 **Funcionalidade indisponível no Streamlit Cloud**\n\n"
        "Esta IA utiliza webcam e MediaPipe, que exigem execução local.\n\n"
        "👉 Clone o projeto e execute localmente para utilizar esta função."
    )
    st.stop()

# =====================================================
# IMPORTS LOCAIS (SÓ EXECUTA LOCAL)
# =====================================================
import cv2
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# =====================================================
# CONSTANTES
# =====================================================
OLHO_ESQUERDO = {
    "superior": [159, 145, 23, 27, 28, 56, 190],
    "inferior": [23, 25, 110, 130, 133, 243, 244],
    "canto_externo": [33, 133],
    "canto_interno": [133, 243, 244, 145],
}

OLHO_DIREITO = {
    "superior": [386, 374, 253, 257, 258, 286, 414],
    "inferior": [253, 255, 339, 359, 362, 463, 464],
    "canto_externo": [263, 362],
    "canto_interno": [362, 463, 464, 374],
}

# =====================================================
# FUNÇÕES
# =====================================================
def calcular_ear(pontos, landmarks):
    try:
        p1 = np.array([landmarks[pontos["superior"][2]].x,
                       landmarks[pontos["superior"][2]].y])
        p2 = np.array([landmarks[pontos["inferior"][2]].x,
                       landmarks[pontos["inferior"][2]].y])
        p3 = np.array([landmarks[pontos["canto_externo"][0]].x,
                       landmarks[pontos["canto_externo"][0]].y])
        p4 = np.array([landmarks[pontos["canto_interno"][0]].x,
                       landmarks[pontos["canto_interno"][0]].y])

        return np.linalg.norm(p1 - p2) / np.linalg.norm(p3 - p4)
    except Exception:
        return 0


def detectar_estado(ear, piscadas):
    if ear < 0.20:
        return "😴 Cansado", "Você parece cansado. Faça uma pausa."
    elif piscadas > 20:
        return "😵 Distraído", "Muitas piscadas detectadas."
    elif 0.25 <= ear <= 0.35:
        return "😊 Focado", "Você está bem concentrado!"
    return "🤔 Normal", "Estado cognitivo normal."

# =====================================================
# MAIN
# =====================================================
def main():
    st.markdown(
        "Esta ferramenta utiliza **Visão Computacional** para detectar "
        "o estado emocional em tempo real."
    )

    col1, col2 = st.columns([3, 1])

    with col2:
        iniciar = st.button("▶️ Iniciar")
        parar = st.button("⏹️ Parar")
        limiar = st.slider("Sensibilidade", 0.1, 0.4, 0.25)

    with col1:
        video = st.empty()
        estado_box = st.empty()

        if iniciar and not parar:
            cap = cv2.VideoCapture(0)

            with mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            ) as face_mesh:

                piscadas = 0
                historico = []

                while cap.isOpened() and not parar:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = face_mesh.process(rgb)

                    if results.multi_face_landmarks:
                        for face in results.multi_face_landmarks:
                            mp_drawing.draw_landmarks(
                                rgb,
                                face,
                                mp_face_mesh.FACEMESH_CONTOURS,
                                None,
                                mp_drawing_styles.get_default_face_mesh_contours_style()
                            )

                            ear = (
                                calcular_ear(OLHO_ESQUERDO, face.landmark)
                                + calcular_ear(OLHO_DIREITO, face.landmark)
                            ) / 2

                            historico.append(ear)
                            if ear < limiar:
                                piscadas += 1

                    video.image(rgb, channels="RGB", use_container_width=True)

                    if len(historico) > 30:
                        ear_m = np.mean(historico[-30:])
                        estado, msg = detectar_estado(ear_m, piscadas)
                        estado_box.info(f"**{estado}**\n\n{msg}")

                    time.sleep(0.03)

            cap.release()


if __name__ == "__main__":
    main()
