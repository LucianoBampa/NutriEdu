# pages/7_Avaliacao_IA.py
import streamlit as st
import sqlite3
from datetime import datetime
import cv2
import numpy as np
import av

# try imports for mediapipe and webrtc
try:
    import mediapipe as mp

    MEDIAPIPE_DISPONIVEL = True
except Exception:
    MEDIAPIPE_DISPONIVEL = False

try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode, VideoProcessorBase

    WEBRTC_DISPONIVEL = True
except Exception:
    WEBRTC_DISPONIVEL = False

st.set_page_config(page_title="Avaliação IA - EduNutri", layout="wide")

st.title("📝 Avaliação Inteligente (Perguntas + Detecção Facial)")
st.markdown(
    "O aluno responde perguntas enquanto a webcam registra emoções. "
    "Ao final, salvamos as respostas + emoção predominante por pergunta."
)

# -------------------------
# Perguntas (5 acadêmicas + 5 nutricionais)
# -------------------------
QUESTOES = [
    "1. O que você entendeu sobre o tema apresentado hoje?",
    "2. Quais partes você achou mais difíceis?",
    "3. Como você avaliaria seu nível de atenção durante a aula?",
    "4. Você se sente confiante para responder exercícios sobre esse assunto?",
    "5. O que poderia facilitar seu aprendizado?",
    "6. O que você costuma comer no café da manhã?",
    "7. Quantas vezes por dia você consome frutas?",
    "8. Você bebe água com frequência?",
    "9. Você costuma comer durante os estudos?",
    "10. Como você se sente fisicamente durante as aulas?",
]

DB_PATH = "nutriedu.db"


# ---------- DB helpers ----------
def conectar():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def criar_tabelas():
    conn = conectar()
    c = conn.cursor()
    # tabela de avaliações por pergunta
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS avaliacoes_pergunta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            pergunta_index INTEGER,
            pergunta TEXT,
            resposta TEXT,
            emocao_detectada TEXT,
            timestamp TEXT
        )
    """
    )
    conn.commit()
    conn.close()


criar_tabelas()

# -------------------------
# Detector de emoção (simplificado; usa landmarks do MediaPipe)
# -------------------------
EMOCOES_EMOJI = {
    "Feliz": "😄",
    "Triste": "😢",
    "Surpreso": "😲",
    "Bravo": "😠",
    "Neutro": "😐",
}
EMOCOES_CORES = {
    "Feliz": (0, 255, 0),
    "Triste": (255, 0, 0),
    "Surpreso": (0, 165, 255),
    "Bravo": (0, 0, 255),
    "Neutro": (128, 128, 128),
}


def detectar_emocao_por_landmarks(landmarks):
    try:
        if not landmarks or len(landmarks) < 468:
            return "Neutro"
        olho_esq_top = landmarks[159]
        olho_esq_bot = landmarks[145]
        olho_dir_top = landmarks[386]
        olho_dir_bot = landmarks[374]
        boca_top = landmarks[13]
        boca_bot = landmarks[14]
        boca_esq = landmarks[61]
        boca_dir = landmarks[291]
        sobr_esq = landmarks[70]
        sobr_dir = landmarks[300]
        dist_entre_olhos = abs(landmarks[33].x - landmarks[263].x)
        if dist_entre_olhos == 0:
            return "Neutro"
        abertura_olhos = (
            (
                abs(olho_esq_top.y - olho_esq_bot.y)
                + abs(olho_dir_top.y - olho_dir_bot.y)
            )
            / 2
            / dist_entre_olhos
        )
        abertura_boca = abs(boca_top.y - boca_bot.y) / dist_entre_olhos
        largura_boca = abs(boca_esq.x - boca_dir.x) / dist_entre_olhos
        sobr_diff = (sobr_esq.y + sobr_dir.y) / 2
        # regras simples (mesmas do protótipo)
        if abertura_olhos > 0.30 and abertura_boca > 0.32:
            return "Surpreso"
        if largura_boca > 0.75 and abertura_boca < 0.25:
            return "Feliz"
        if abertura_olhos < 0.18 and sobr_diff < 0.38:
            return "Bravo"
        if largura_boca < 0.55 and abertura_boca < 0.18:
            return "Triste"
        return "Neutro"
    except Exception:
        return "Neutro"


# -------------------------
# Video processor que atualiza st.session_state["last_emotion"]
# -------------------------
if MEDIAPIPE_DISPONIVEL:
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    # instância única (opcional)
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
else:
    face_mesh = None


class AvaliacaoVideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.frame_count = 0

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        self.frame_count += 1
        # atualiza a cada 5 frames para não sobrecarregar
        if not MEDIAPIPE_DISPONIVEL or face_mesh is None:
            # escreve aviso no frame
            cv2.putText(
                img,
                "MediaPipe nao disponivel",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )
            last = st.session_state.get("last_emotion", "Neutro")
            st.session_state["last_emotion"] = last
            return av.VideoFrame.from_ndarray(img, format="bgr24")
        if self.frame_count % 5 != 0:
            return av.VideoFrame.from_ndarray(img, format="bgr24")
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)
        if results and getattr(results, "multi_face_landmarks", None):
            face_landmarks = results.multi_face_landmarks[0]
            emocao = detectar_emocao_por_landmarks(face_landmarks.landmark)
            st.session_state["last_emotion"] = emocao
            # desenha label (fundo + texto)
            cor = EMOCOES_CORES.get(emocao, (255, 255, 255))
            emoji = EMOCOES_EMOJI.get(emocao, "")
            cv2.rectangle(img, (5, 5), (360, 70), (0, 0, 0), -1)
            cv2.rectangle(img, (5, 5), (360, 70), cor, 2)
            cv2.putText(
                img,
                f"{emoji} {emocao}",
                (15, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                cor,
                3,
                cv2.LINE_AA,
            )
        else:
            st.session_state["last_emotion"] = st.session_state.get(
                "last_emotion", "Neutro"
            )
        return av.VideoFrame.from_ndarray(img, format="bgr24")


# -------------------------
# Estado da avaliação
# -------------------------
if "avaliacao_index" not in st.session_state:
    st.session_state.avaliacao_index = 0
if "avaliacao_respostas" not in st.session_state:
    st.session_state.avaliacao_respostas = []  # lista de dicts por pergunta
if "last_emotion" not in st.session_state:
    st.session_state.last_emotion = "Neutro"

# -------------------------
# Layout: usuário e webcam
# -------------------------
with st.sidebar:
    st.header("Instruções")
    st.info(
        "1) Clique em START na câmera\n2) Responda a pergunta na caixa\n3) Clique em Próxima para salvar e ir à próxima\n4) Ao final, envie/registre a avaliação."
    )
    st.markdown("---")
    usuario_id = st.number_input("ID do usuário", min_value=1, step=1, value=1)

col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("📹 Webcam")
    if WEBRTC_DISPONIVEL:
        webrtc_ctx = webrtc_streamer(
            key="avaliacao_ia_camera",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=AvaliacaoVideoProcessor,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )
    else:
        st.error("streamlit-webrtc não disponível no ambiente.")

    st.markdown(
        "**Emoção atual:** "
        + EMOCOES_EMOJI.get(st.session_state.get("last_emotion", "Neutro"), "")
        + " "
        + st.session_state.get("last_emotion", "Neutro")
    )

with col2:
    st.subheader("✍️ Pergunta e Resposta")
    idx = st.session_state.avaliacao_index
    st.markdown(f"**Pergunta {idx+1}/{len(QUESTOES)}**")
    st.markdown(QUESTOES[idx])
    resposta = st.text_area("Sua resposta:", height=160, key=f"resposta_{idx}")

    cols = st.columns([1, 1, 1])
    if cols[0].button("◀️ Anterior") and st.session_state.avaliacao_index > 0:
        # volta sem salvar alterações atuais (o texto fica guardado no text_area key)
        st.session_state.avaliacao_index -= 1
        st.experimental_rerun()

    if cols[1].button("Próxima ▶️"):
        # salva resposta atual
        emocao = st.session_state.get("last_emotion", "Neutro")
        timestamp = datetime.now().isoformat()
        registro = {
            "usuario_id": usuario_id,
            "pergunta_index": idx,
            "pergunta": QUESTOES[idx],
            "resposta": resposta.strip(),
            "emocao": emocao,
            "timestamp": timestamp,
        }
        # atualiza lista (se já tinha resposta para esse idx, substitui)
        found = False
        for i, r in enumerate(st.session_state.avaliacao_respostas):
            if r["pergunta_index"] == idx:
                st.session_state.avaliacao_respostas[i] = registro
                found = True
                break
        if not found:
            st.session_state.avaliacao_respostas.append(registro)
        # ir para próxima pergunta se existir
        if st.session_state.avaliacao_index < len(QUESTOES) - 1:
            st.session_state.avaliacao_index += 1
            st.experimental_rerun()
        else:
            st.success(
                "Você chegou à última pergunta. Clique em 'Finalizar e Salvar' para registrar."
            )
            st.experimental_rerun()

    if cols[2].button("Finalizar e Salvar"):
        # salva todas respostas no DB
        conn = conectar()
        c = conn.cursor()
        for r in st.session_state.avaliacao_respostas:
            c.execute(
                """
                INSERT INTO avaliacoes_pergunta
                (usuario_id, pergunta_index, pergunta, resposta, emocao_detectada, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    r["usuario_id"],
                    r["pergunta_index"],
                    r["pergunta"],
                    r["resposta"],
                    r["emocao"],
                    r["timestamp"],
                ),
            )
        conn.commit()
        conn.close()
        st.success("Avaliação salva localmente no banco (nutriedu.db).")
        # mostrar resumo
        st.balloons()
        st.session_state.avaliacao_index = 0
        st.session_state.avaliacao_respostas = []
        st.experimental_rerun()

# -------------------------
# Visualização de histórico rápido
# -------------------------
st.markdown("---")
st.subheader("📚 Histórico rápido (últimas 20 respostas salvas)")
if st.button("Carregar histórico local"):
    conn = conectar()
    rows = conn.execute(
        """
        SELECT usuario_id, pergunta_index, pergunta, resposta, emocao_detectada, timestamp
        FROM avaliacoes_pergunta
        ORDER BY id DESC LIMIT 20
    """
    ).fetchall()
    conn.close()
    if rows:
        import pandas as pd

        df = pd.DataFrame(
            rows,
            columns=[
                "usuario_id",
                "pergunta_index",
                "pergunta",
                "resposta",
                "emocao",
                "timestamp",
            ],
        )
        st.dataframe(df)
    else:
        st.info("Nenhuma avaliação registrada ainda.")

# -------------------------
# Nota sobre privacidade
# -------------------------
st.markdown("---")
st.info(
    "🔒 Privacidade: processamento local. Nenhum vídeo é enviado para servidores. Só armazenamos texto + rótulo da emoção."
)
