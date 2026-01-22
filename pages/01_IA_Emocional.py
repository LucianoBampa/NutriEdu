import streamlit as st
import numpy as np
from PIL import Image
import time

try:
    import cv2
    CAM_AVAILABLE = True
except ModuleNotFoundError:
    cv2 = None
    CAM_AVAILABLE = False


# Imports do MediaPipe corrigidos
try:
    import mediapipe as mp
    mp_face_mesh = mp.solutions.face_mesh  # type: ignore
    mp_drawing = mp.solutions.drawing_utils  # type: ignore
    mp_drawing_styles = mp.solutions.drawing_styles  # type: ignore
except ImportError:
    st.error("MediaPipe não está instalado. Execute: pip install mediapipe")
    st.stop()

# Configuração da página
st.set_page_config(page_title="IA Emocional - NutriEdu", page_icon="🧠", layout="wide")

# Índices dos pontos faciais (corrigido com espaços)
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


def calcular_ear(pontos_olho, landmarks):
    """Calcula Eye Aspect Ratio para detectar piscadas"""
    try:
        # Pontos verticais
        p1 = np.array(
            [
                landmarks[pontos_olho["superior"][2]].x,
                landmarks[pontos_olho["superior"][2]].y,
            ]
        )
        p2 = np.array(
            [
                landmarks[pontos_olho["inferior"][2]].x,
                landmarks[pontos_olho["inferior"][2]].y,
            ]
        )

        # Pontos horizontais
        p3 = np.array(
            [
                landmarks[pontos_olho["canto_externo"][0]].x,
                landmarks[pontos_olho["canto_externo"][0]].y,
            ]
        )
        p4 = np.array(
            [
                landmarks[pontos_olho["canto_interno"][0]].x,
                landmarks[pontos_olho["canto_interno"][0]].y,
            ]
        )

        # Distâncias
        dist_vertical = np.linalg.norm(p1 - p2)
        dist_horizontal = np.linalg.norm(p3 - p4)

        # EAR
        if dist_horizontal > 0:
            ear = dist_vertical / dist_horizontal
        else:
            ear = 0

        return ear
    except Exception as e:
        st.error(f"Erro ao calcular EAR: {e}")
        return 0


def detectar_estado_emocional(ear_medio, num_piscadas):
    """Detecta o estado emocional baseado em EAR e piscadas"""
    if ear_medio < 0.2:
        return "😴 Cansado", "Você parece cansado. Que tal fazer uma pausa?"
    elif num_piscadas > 20:
        return "😵 Distraído", "Muitas piscadas! Tente focar mais."
    elif 0.25 <= ear_medio <= 0.35:
        return "😊 Focado", "Ótimo! Você está bem concentrado!"
    else:
        return "🤔 Normal", "Estado normal. Continue assim!"


def main():
    st.title("🧠 IA Emocional - Detector de Estado Cognitivo")
    # 🚫 BLOQUEIO PARA STREAMLIT CLOUD
    if not CAM_AVAILABLE:
        st.warning(
            "🚫 A funcionalidade de webcam não está disponível no Streamlit Cloud.\n\n"
            "👉 Para usar a IA Emocional, execute o projeto localmente."
        )
        st.stop()
        
    st.markdown(
        """
    Esta ferramenta usa **visão computacional** para detectar seu estado
    emocional em tempo real através da sua webcam.
    """
    )

    # Instruções
    with st.expander("ℹ️ Como funciona?"):
        st.write(
            """
        - A IA analisa seus olhos usando MediaPipe
        - Detecta piscadas e abertura dos olhos
        - Classifica seu estado: Focado, Cansado ou Distraído
        - Dá feedback em tempo real
        """
        )

    # Controles
    col1, col2 = st.columns([3, 1])

    with col2:
        st.subheader("⚙️ Controles")
        iniciar = st.button("▶️ Iniciar Análise", use_container_width=True)
        parar = st.button("⏹️ Parar", use_container_width=True)

        # Configurações
        st.divider()
        limiar_ear = st.slider(
            "Limiar de piscada", 0.1, 0.4, 0.25, help="Menor valor = mais sensível"
        )

    with col1:
        # Placeholder para vídeo e métricas
        video_placeholder = st.empty()
        metricas_placeholder = st.empty()
        estado_placeholder = st.empty()

        if iniciar and not parar:
            # Inicializar câmera
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                st.error("❌ Não foi possível acessar a webcam!")
                return

            # Inicializar Face Mesh
            with mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            ) as face_mesh:

                contador_piscadas = 0
                ear_historico = []
                frame_count = 0

                while cap.isOpened() and not parar:
                    ret, frame = cap.read()
                    if not ret:
                        st.warning("⚠️ Erro ao capturar frame")
                        break

                    # Converter para RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Processar com MediaPipe
                    results = face_mesh.process(frame_rgb)

                    if results.multi_face_landmarks:
                        for face_landmarks in results.multi_face_landmarks:
                            # Desenhar malha facial
                            mp_drawing.draw_landmarks(
                                image=frame_rgb,
                                landmark_list=face_landmarks,
                                connections=mp_face_mesh.FACEMESH_CONTOURS,
                                landmark_drawing_spec=None,
                                connection_drawing_spec=(
                                    mp_drawing_styles.get_default_face_mesh_contours_style()
                                ),
                            )

                            # Calcular EAR
                            ear_esq = calcular_ear(
                                OLHO_ESQUERDO, face_landmarks.landmark
                            )
                            ear_dir = calcular_ear(
                                OLHO_DIREITO, face_landmarks.landmark
                            )
                            ear_medio = (ear_esq + ear_dir) / 2
                            ear_historico.append(ear_medio)

                            # Detectar piscada
                            if ear_medio < limiar_ear:
                                contador_piscadas += 1

                    # Mostrar frame
                    video_placeholder.image(
                        frame_rgb, channels="RGB", use_container_width=True
                    )

                    # Atualizar métricas a cada 30 frames
                    frame_count += 1
                    if frame_count % 30 == 0 and ear_historico:
                        ear_atual = np.mean(ear_historico[-30:])

                        # Detectar estado
                        estado, mensagem = detectar_estado_emocional(
                            ear_atual, contador_piscadas
                        )

                        # Mostrar métricas
                        metricas_placeholder.metric(
                            "EAR Médio", f"{ear_atual:.3f}", help="Eye Aspect Ratio"
                        )

                        # Mostrar estado
                        estado_placeholder.info(f"**{estado}**\n\n{mensagem}")

                    time.sleep(0.03)  # ~30 FPS

            cap.release()


if __name__ == "__main__":
    main()
