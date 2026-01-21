import cv2
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, VideoProcessorBase
import av


# media pipe detect
try:
    import mediapipe as mp
    MEDIAPIPE_DISPONIVEL = True
except Exception:
    MEDIAPIPE_DISPONIVEL = False


st.title('🧠 IA Emocional')


# Initialize face mesh
if MEDIAPIPE_DISPONIVEL:
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True,
    min_detection_confidence=0.5, min_tracking_confidence=0.5)
else:
    face_mesh = None


EMOCOES_CORES = {'Feliz':(0,255,0),'Triste':(255,0,0),'Surpreso':(0,165,255),'Bravo':(0,0,255),'Neutro':(128,128,128)}
EMOCOES_EMOJI = {'Feliz':'😄','Triste':'😢','Surpreso':'😲','Bravo':'😠','Neutro':'😐'}


# função simples de detecção (proporções)
def detectar_emocao_por_landmarks(landmarks):
    if not landmarks or len(landmarks)<468:
        return 'Neutro'
    try:
        # normaliza por distância horizontal entre olhos
        dist = abs(landmarks[33].x - landmarks[263].x)
        if dist==0: return 'Neutro'
        abertura_olhos = (abs(landmarks[159].y-landmarks[145].y)+abs(landmarks[386].y-landmarks[374].y))/2/dist
        abertura_boca = abs(landmarks[13].y-landmarks[14].y)/dist
        largura_boca = abs(landmarks[61].x-landmarks[291].x)/dist
        if abertura_olhos>0.30 and abertura_boca>0.32: return 'Surpreso'
        if largura_boca>0.75 and abertura_boca<0.25: return 'Feliz'
        if abertura_olhos<0.18: return 'Bravo'
        if largura_boca<0.55 and abertura_boca<0.18: return 'Triste'
    except Exception:
        return 'Neutro'
    return 'Neutro'


class EmotionVideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.face_mesh = face_mesh
        self.count = 0

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format='bgr24')
        self.count += 1
        if self.count % 2 != 0:
            return av.VideoFrame.from_ndarray(img, format='bgr24')
        if not MEDIAPIPE_DISPONIVEL or self.face_mesh is None:
            cv2.putText(img,'MediaPipe nao disponivel',(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
            return av.VideoFrame.from_ndarray(img, format='bgr24')
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)
        if results.multi_face_landmarks:
            lm = results.multi_face_landmarks[0]
            emoc = detectar_emocao_por_landmarks(lm.landmark)
            st.session_state['last_emotion'] = emoc
            color = EMOCOES_CORES.get(emoc,(255,255,255))
            emoji = EMOCOES_EMOJI.get(emoc,'😐')
            cv2.rectangle(img,(5,5),(360,70),(0,0,0),-1)
            cv2.putText(img,f"{emoji} {emoc}",(15,45),cv2.FONT_HERSHEY_SIMPLEX,1.1,color,3)
        else:
            cv2.putText(img,'Nenhum rosto detectado',(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
        return av.VideoFrame.from_ndarray(img, format='bgr24')


if 'last_emotion' not in st.session_state:
    st.session_state['last_emotion'] = 'Neutro'


if not MEDIAPIPE_DISPONIVEL:
    st.error('MediaPipe não instalado. pip install mediapipe==0.10.5 (Python 3.9 recomendado)')
else:
    webrtc_streamer(key='emo', mode=WebRtcMode.SENDRECV, video_processor_factory=EmotionVideoProcessor, media_stream_constraints={'video': True, 'audio': False}, async_processing=True)
