import streamlit as st
import numpy as np
import time

# =====================================================
# VERIFICAÇÃO DE CÂMERA (STREAMLIT CLOUD vs LOCAL)
# =====================================================
try:
    import cv2
    CAM_AVAILABLE = True
except ModuleNotFoundError:
    cv2 = None
    CAM_AVAILABLE = False

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(
    page_title="IA Emocional - NutriEdu",
    page_icon="🧠",
    layout="wide"
)

# =====================================================
# CONSTANTES DOS OLHOS (FACE MESH)
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
# FUNÇÕES AUXILIARES
# =====================================================
def calcular_ear(pontos_olho, landmarks):
    """Calcula Eye Aspect Ratio (EAR)"""
    try:
        p1 = np.array([
            landmarks[pontos_olho["superior"][2]].x,
            landmarks[pontos_olho["superior"][2]].y,
        ])
        p2 = np.array([
            landmarks[pontos_olho["inferior"][2]].x,
            landmarks[pontos_olho["inferior"][2]].y,
        ])

        p3 = np.array([
            landmarks[pontos_olho["canto_externo"][0]].x,
            landmarks[pontos_olho["canto_externo"][0]].y,
        ])
        p4 = np.array([
            landmarks[pontos_olho["canto_interno"][0]].x,
            landmarks[pontos_olho["canto_interno"][0]].y,
        ])

        dist_vertical = np.linalg.norm(p1 - p2)
        dist_horizontal = np.linalg.norm(p3 - p4)

        return dist_vertical / dist_horizontal if dist_horizontal > 0 else 0
    except Exception:
        return 0


def detectar_estado_emocional(ear_medio, piscadas):
    if ear_medio < 0.20:
        return "😴 Cansado", "Você parece cansado. Que tal fazer uma pausa?"
    elif piscadas > 20:
        return "😵 Distraído", "Muitas piscadas detectadas. Tente focar mais."
    elif 0.25 <= ear_medio <= 0.35:
        return "😊 Focado", "Ótimo! Você está bem concentrado."
    else:
        return "🤔 Normal", "Estado emocional dentro do normal."

# =====================================================
# FUNÇÃO PRINCIPAL
# =====================================================
def main():
    st.title("🧠 IA Emocional - Detector de Estado Cognitivo")

    # 🚫 BLOQUEIO AUTOMÁTICO PARA STREAMLIT CLOUD
    if not CAM_AVAILABLE:
        st.warning(
            "🚫 A webcam não está disponível no Streamlit Cloud.\n\n"
            "👉 Para usar esta funcionalidade, execute o projeto localmente."
        )
        st.stop()

    # ✅ Importar MediaPipe SOMENTE após garantir ambiente local
    try:
        import mediapipe as mp
        mp_face_mesh = mp.solutions.face_mesh
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
    except Exception as e:
        st.error("Erro ao carregar o MediaPipe. Execute localmente.")
        st.exception(e)
        st.stop()

    st.markdown(
        """
        Esta ferramenta utiliza **Visão Computacional** para identificar
        seu estado emocional em tempo real através da webcam.
        """
    )

    with st.expander("ℹ️ Como funciona?"):
        st.write(
            """
            - Analisa os olhos usando MediaPipe Face Mesh  
            - Detecta piscadas e abertura ocular  
            - Classifica o estado cognitivo  
            - Exibe feedback em tempo real
            """
        )

    # =================================================
    # CONTROLES
    # =================================================
    col1, col2 = st.columns([3, 1])

    with col2:
        st.subheader("⚙️ Controles")
        iniciar = st.button("▶️ Iniciar Análise", use_container_width=True)
        parar = st.button("⏹️ Parar", use_container_width=True)

        st.divider()
        limiar_ear = st.slider(
            "Sensibilidade da piscada",
            0.10, 0.40, 0.25
        )

    with col1:
        video_placeholder = st.empty()
        metricas_placeholder = st.empty()
        estado_placeholder = st.empty()

        if iniciar and not parar:
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                st.error("❌ Não foi possível acessar a webcam.")
                return

            with mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            ) as face_mesh:

                piscadas = 0
                ear_historico = []
                frame_count = 0

                while cap.isOpened() and not parar:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = face_mesh.process(frame_rgb)

                    if results.multi_face_landmarks:
                        for face_landmarks in results.multi_face_landmarks:
                            mp_drawing.draw_landmarks(
                                image=frame_rgb,
                                landmark_list=face_landmarks,
                                connections=mp_face_mesh.FACEMESH_CONTOURS,
                                landmark_drawing_spec=None,
                                connection_drawing_spec=(
                                    mp_drawing_styles
                                    .get_default_face_mesh_contours_style()
                                ),
                            )

                            ear_esq = calcular_ear(
                                OLHO_ESQUERDO, face_landmarks.landmark
                            )
                            ear_dir = calcular_ear(
                                OLHO_DIREITO, face_landmarks.landmark
                            )

                            ear_medio = (ear_esq + ear_dir) / 2
                            ear_historico.append(ear_medio)

                            if ear_medio < limiar_ear:
                                piscadas += 1

                    video_placeholder.image(
                        frame_rgb,
                        channels="RGB",
                        use_container_width=True
                    )

                    frame_count += 1
                    if frame_count % 30 == 0 and ear_historico:
                        ear_atual = np.mean(ear_historico[-30:])
                        estado, msg = detectar_estado_emocional(
                            ear_atual, piscadas
                        )

                        metricas_placeholder.metric(
                            "EAR Médio", f"{ear_atual:.3f}"
                        )
                        estado_placeholder.info(
                            f"**{estado}**\n\n{msg}"
                        )

                    time.sleep(0.03)

            cap.release()

# =====================================================
# EXECUÇÃO
# =====================================================
if __name__ == "__main__":
    main()
