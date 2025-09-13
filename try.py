import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import cv2
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time
from ultralytics import YOLO
from PIL import Image
import base64
import io
import zipfile

# === Sound Alert Function ===
def play_sound():
    sound_html = """
        <audio autoplay>
            <source src="data:audio/mp3;base64,{sound_data}" type="audio/mp3">
        </audio>
    """
    with open(r"https://res.cloudinary.com/dzsbxzjqe/video/upload/v1757744930/siren-alert-96052_pkxwxj.mp3", "rb") as f:
        b64_sound = base64.b64encode(f.read()).decode()
        st.markdown(sound_html.format(sound_data=b64_sound), unsafe_allow_html=True)

# === Color Palette ===
PRIMARY_COLOR = "#3B82F6"
SECONDARY_COLOR = "#14B8A6"
ACCENT_COLOR = "#F59E0B"
ERROR_COLOR = "#EF4444"
SUCCESS_COLOR = "#10B981"
BG_COLOR = "#0F172A"
TEXT_COLOR = "#1E293B"

st.set_page_config(layout="wide", page_title="ProctorVision", page_icon="🧠")

st.markdown(f"""
<style>
    .main-header {{ font-size: 2.5rem; color: {PRIMARY_COLOR}; text-align: center; margin-bottom: 1rem; }}
    .violation-alert {{ color: {ERROR_COLOR}; font-weight: bold; }}
    .status-ok {{ color: {SUCCESS_COLOR}; font-weight: bold; }}
    .stApp {{ background-color: {BG_COLOR}; }}
    h1, h2, h3 {{ color: {PRIMARY_COLOR}; }}
    .stButton>button {{ background-color: {PRIMARY_COLOR}; color: white; border-radius: 6px; }}
    .stButton>button:hover {{ background-color: {SECONDARY_COLOR}; }}
    .info-box {{ background-color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); color: #0F172A; }}
    .dashboard-title {{ color: {SECONDARY_COLOR}; font-size: 1.3rem; margin-bottom: 1rem; }}
</style>
""", unsafe_allow_html=True)

st.markdown(f'<h1 class="main-header">🧠 ProctorVision: YOLOv8 Monitoring System</h1>', unsafe_allow_html=True)

# Session State Init
for key, default in {
    "log": [], "run": False, "alert_count": 0, "last_snapshot": None,
    "start_time": None, "total_session_time": 0, "violation_images": []
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# === Sidebar ===
with st.sidebar:
    st.markdown(f"<h2 style='color:{PRIMARY_COLOR};'>ProctorVision Controls</h2>", unsafe_allow_html=True)
    st.divider()
    model_path = {"YOLOv8 Nano": "yolov8n.pt", "YOLOv8 Small": "yolov8s.pt", "YOLOv8 Medium": "yolov8m.pt"}[st.selectbox("Select YOLO Model", ["YOLOv8 Nano", "YOLOv8 Small", "YOLOv8 Medium"])]
    confidence_threshold = st.slider("Detection Confidence", 0.1, 1.0, 0.5, 0.05)
    alert_types = st.multiselect("Enable Alerts For:", ["No Face", "Multiple Faces", "Not Looking at Screen", "Phone Detection", "Person Left Frame"], default=["No Face", "Multiple Faces"])
    auto_snapshot = st.checkbox("Auto-capture violation snapshots", value=True)
    debug = st.checkbox("Show debug information", value=False)

    col1, col2 = st.columns(2)
    if col1.button("▶️ Start", use_container_width=True):
        st.session_state.run = True
        st.session_state.start_time = time.time()
    if col2.button("⏹️ Stop", use_container_width=True):
        if st.session_state.run and st.session_state.start_time:
            st.session_state.total_session_time += time.time() - st.session_state.start_time
        st.session_state.run = False

    # === Export CSV Report ===
    if st.session_state.log:
        csv = pd.DataFrame(st.session_state.log).to_csv(index=False).encode('utf-8')
        st.download_button("📊 Export Violation Report", csv, f'Violation_Report_{datetime.datetime.now().strftime("%Y-%m-%d")}.csv', mime='text/csv', use_container_width=True)

    # === Download Snapshots ZIP ===
    if st.session_state.violation_images:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
            for i, item in enumerate(st.session_state.violation_images):
                image_data = base64.b64decode(item["image"])
                filename = f'{item["time"].replace(":", "-").replace(" ", "_")}_{item["reason"].replace(" ", "_")}.jpg'
                zip_file.writestr(filename, image_data)
        zip_buffer.seek(0)
        st.download_button(
            label="📥 Download Snapshots ZIP",
            data=zip_buffer,
            file_name=f'Violation_Snapshots_{datetime.datetime.now().strftime("%Y-%m-%d")}.zip',
            mime='application/zip',
            use_container_width=True
        )

@st.cache_resource
def load_model(path):
    return YOLO(path)

try:
    model = load_model(model_path)
    st.sidebar.success("✅ Model loaded successfully!")
except Exception as e:
    st.sidebar.error(f"❌ Failed to load model: {str(e)}")
    st.stop()

def log_violation(frame, reason):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    st.session_state.log.append({"Time": timestamp, "Violation": reason})
    if auto_snapshot:
        _, buffer = cv2.imencode('.jpg', frame)
        st.session_state.violation_images.append({
            "time": timestamp,
            "reason": reason,
            "image": base64.b64encode(buffer).decode('utf-8')
        })
    play_sound()
    st.session_state.alert_count += 1
    st.session_state.last_snapshot = frame

def is_looking_at_screen(face_box):
    x1, y1, x2, y2 = face_box
    return not (x2 - x1 < 100 or y2 - y1 < 100 or x1 < 32 or x2 > 608 or y1 < 24 or y2 > 456)

col1, col2 = st.columns([3, 1])

with col2:
    total_time = st.session_state.total_session_time + (time.time() - st.session_state.start_time if st.session_state.run and st.session_state.start_time else 0)
    h, m = divmod(int(total_time), 3600), int(total_time) % 60
    st.markdown(f"""<div class='info-box'><h3 class='dashboard-title'>📝 Session Summary</h3><p><strong>Total Time:</strong> {h[0]:02}:{h[1]:02}:{m:02}</p><p><strong>Violations:</strong> {st.session_state.alert_count}</p></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class='info-box'><h3 class='dashboard-title'>🔍 Current Status</h3><p class='{"status-ok" if st.session_state.run else "violation-alert"}'>{'System Active' if st.session_state.run else 'System Inactive'}</p></div>""", unsafe_allow_html=True)
    if st.session_state.last_snapshot is not None:
        st.markdown(f"<div class='info-box'><h3 class='dashboard-title'>📸 Last Violation</h3>", unsafe_allow_html=True)
        st.image(st.session_state.last_snapshot, channels="BGR")
        st.markdown("</div>", unsafe_allow_html=True)

with col1:
    stframe = st.empty()
    stats_placeholder = st.empty()

if st.session_state.run:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("❌ Webcam not found.")
        st.session_state.run = False
    frame_count = 0
    start_time = time.time()
    fps = 0

    while st.session_state.run:
        ret, frame = cap.read()
        if not ret:
            st.error("❌ Failed to capture frame.")
            break

        frame = cv2.flip(frame, 1)
        display_frame = frame.copy()
        results = model.predict(frame, conf=confidence_threshold, verbose=False)[0]

        face_count, person_count = 0, 0
        phone_detected = False

        for box in results.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if label.lower() == "person":
                face_count += 1
                person_count += 1
                if "Not Looking at Screen" in alert_types and not is_looking_at_screen((x1, y1, x2, y2)):
                    log_violation(frame.copy(), "Not looking at screen")
            elif label.lower() in ["cell phone", "mobile phone"]:
                phone_detected = True

            cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(display_frame, f"{label}: {conf:.2f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

        if "No Face" in alert_types and face_count == 0:
            log_violation(frame.copy(), "No face detected")
        if "Multiple Faces" in alert_types and face_count > 1:
            log_violation(frame.copy(), f"Multiple faces detected ({face_count})")
        if "Phone Detection" in alert_types and phone_detected:
            log_violation(frame.copy(), "Phone detected")
        if "Person Left Frame" in alert_types and person_count == 0:
            log_violation(frame.copy(), "Person left frame")

        frame_count += 1
        if time.time() - start_time > 1:
            fps = frame_count / (time.time() - start_time)
            frame_count = 0
            start_time = time.time()

        if debug:
            if "fps_history" not in st.session_state:
                st.session_state.fps_history = []
            st.session_state.fps_history.append(fps)
            if len(st.session_state.fps_history) > 30:
                st.session_state.fps_history.pop(0)
            stats_placeholder.line_chart(st.session_state.fps_history)

        stframe.image(display_frame, channels="BGR")


    cap.release()
