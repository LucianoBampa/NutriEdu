import cv2
import mediapipe as mp
import time

mp_face_mesh = mp.solutions.face_mesh # type: ignore
mp_drawing = mp.solutions.drawing_utils # type: ignore


def executar_emocoes(tempo_max=10):
    cap = cv2.VideoCapture(0)
    inicio = time.time()
    rosto_detectado = False

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:

        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break

                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = face_mesh.process(img_rgb)

                if result.multi_face_landmarks:
                    rosto_detectado = True
                    for face in result.multi_face_landmarks:
                        mp_drawing.draw_landmarks(
                            frame,
                            face,
                            mp_face_mesh.FACEMESH_TESSELATION
                        )

                cv2.imshow("IA de Foco e Expressões", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                if time.time() - inicio > tempo_max:
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()

        if rosto_detectado:
            return "Neutro"

        return "Indefinido"
