import streamlit as st
import cv2
import face_recognition
import numpy as np
from PIL import Image

known_face_encodings = []
known_face_names = []

st.title("Identificação de Pessoas com Mandado de Prisão")
option = st.selectbox("Escolha a entrada", ["Imagem", "Webcam"])

def detect_faces(image):
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)
    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Desconhecido"
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
        top, right, bottom, left = face_location
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    return image

if option == "Imagem":
    uploaded_file = st.file_uploader("Escolha uma imagem", type=["jpg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        img_array = np.array(image)
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        img_processed = detect_faces(img_cv)
        img_rgb = cv2.cvtColor(img_processed, cv2.COLOR_BGR2RGB)
        st.image(img_rgb, caption="Resultado", use_column_width=True)
elif option == "Webcam":
    cap = cv2.VideoCapture(0)
    frame_placeholder = st.empty()
    stop_button = st.button("Parar Captura")
    while cap.isOpened() and not stop_button:
        ret, frame = cap.read()
        if not ret:
            st.write("Erro ao capturar vídeo")
            break
        frame_processed = detect_faces(frame)
        frame_rgb = cv2.cvtColor(frame_processed, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        frame_placeholder.image(frame_pil, caption="Vídeo em Tempo Real")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
cv2.destroyAllWindows()
