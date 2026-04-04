import cv2
import streamlit as st

# Your Amazon IP Camera RTSP URL (Check your camera app for the exact string)
# Format usually: rtsp://admin:password@192.168.1.XX:554/live
RTSP_URL = "rtsp://admin:password@YOUR_CAMERA_IP:554"

st.title("EcoLens Phase 2: IP Camera Feed")
frame_placeholder = st.empty()

cap = cv2.VideoCapture(RTSP_URL)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        st.write("Video stream ended or failed.")
        break

    # Convert BGR (OpenCV) to RGB (Streamlit)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Display the live frame in the placeholder
    frame_placeholder.image(frame, channels="RGB")

cap.release()