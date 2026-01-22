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

st.title("🧠 IA Emocional - Detector de Estado Cognitivo")

# =====================================================
# DETECÇÃO DE AMBIENTE (CLOUD x LOCAL)
# =====================================================
IS_CLOUD = os.getenv("STREAMLIT_SERVER_RUNNING") == "1"

if IS_CLOUD:
    st.warning(
        "🚫 **Funcionalidade indisponível no Streamlit Cloud**\n\n"
        "Esta IA utiliza webcam e MediaPipe, que exigem execução local.\n\n"
        "👉 Clone o projeto e execute localmente."
    )
    st.stop()

# =====================================================
# IMPORTS LOCAIS
# =====================================================
import cv2
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# =====================================================
# CONSTANTES FACIAIS (MediaPipe)
# =====================================================
OLHO_ESQUERDO = [33, 160, 158, 133, 153, 144]
OLHO_DIREITO = [362, 385, 387, 263, 373, 380]

# =====================================================
# FUNÇÕES
# =====================================================
def calcular_ear(landmarks, indices):
    p1 = np.array([landmarks[indices[1]].x, landmarks[indices[1]].y])
    p2 = np.array([landmarks[indices[5]].x, landmarks[indices[5]].y])
    p3 = np.array([landmarks[indices[0]].x, landmarks[indices[0]].y])
    p4 = np.array([landmarks[indices[3]].x, landmarks[indices[3]].y])

    vertical = np.linalg.norm(p1 - p2)
    horizontal = np.linalg.norm(p3 - p4)

    if horizontal == 0:
        return 0.0

    return float(vertical / horizontal)


def classificar_estado(ear_medio, piscadas_min):
    if ear_medio < 0.18:
        return "😴 Cansado", "Sinais de sonolência detectados."
    if piscadas_min > 25:
        return "😵 Distraído", "Piscadas excessivas indicam perda de foco."
    if ear_medio > 0.28:
        return "😊 Focado", "Atenção visual estável."
    return "😐 Neutro", "Estado cognitivo regular."


# =====================================================
# MAIN
# =====================================================
def main():
    st.markdown(
        "Esta ferramenta utiliza **Visão Computacional** para inferir "
        "o estado cognitivo a partir da dinâmica ocular."
    )

    col_cam, col_ctrl = st.columns([3, 1])

    with col_ctrl:
        st.subheader("⚙️ Controles")
        iniciar = st.button("▶️ Iniciar")
        parar = st.button("⏹️ Parar")

        st.divider()

        limiar_ear = st.slider(
            "Sensibilidade EAR",
            0.15,
            0.35,
            0.25,
            step=0.01,
        )

    with col_cam:
        video_box = st.empty()
        estado_box = st.empty()

        if iniciar and not parar:
            cap = cv2.VideoCapture(0)

            with mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.6,
                min_tracking_confidence=0.6,
            ) as face_mesh:

                ear_hist = []
                piscadas = []
                inicio = time.time()

                while cap.isOpened() and not parar:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    frame = cv2.flip(frame, 1)
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = face_mesh.process(rgb)

                    if results.multi_face_landmarks:
                        for face in results.multi_face_landmarks:
                            lm = face.landmark

                            ear_esq = calcular_ear(lm, OLHO_ESQUERDO)
                            ear_dir = calcular_ear(lm, OLHO_DIREITO)
                            ear = (ear_esq + ear_dir) / 2

                            ear_hist.append(ear)

                            if ear < limiar_ear:
                                piscadas.append(time.time())

                            mp_drawing.draw_landmarks(
                                frame,
                                face,
                                mp_face_mesh.FACEMESH_CONTOURS,
                                None,
                                mp_drawing_styles.get_default_face_mesh_contours_style(),
                            )

                    # Remover piscadas antigas (>60s)
                    piscadas = [p for p in piscadas if time.time() - p <= 60]

                    video_box.image(
                        frame,
                        channels="BGR",
                        use_container_width=True,
                    )

                    if len(ear_hist) >= 30:
                        ear_medio = float(np.mean(ear_hist[-30:]))
                        piscadas_min = len(piscadas)

                        estado, msg = classificar_estado(
                            ear_medio,
                            piscadas_min,
                        )

                        estado_box.info(f"**{estado}**\n\n{msg}")

                    time.sleep(0.03)

            cap.release()


if __name__ == "__main__":
    main()
