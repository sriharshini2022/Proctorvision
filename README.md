# 🧠 ProctorVision – Real-Time Cheating Detection using YOLOv8 + Streamlit  

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)  
![Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit)  
![YOLOv8](https://img.shields.io/badge/YOLOv8-Object%20Detection-green)  
![Status](https://img.shields.io/badge/Status-Prototype-orange)  

**ProctorVision** is an AI-powered online proctoring system that helps maintain exam integrity by **automatically detecting suspicious behaviors** during online tests.  
Built with **YOLOv8** for real-time object detection and **Streamlit** for an interactive dashboard, it ensures seamless and reliable monitoring.  

---

## ✨ Features
✅ Real-time **webcam monitoring**  
✅ **YOLOv8 object detection** (Nano / Small / Medium)  
✅ Detects common violations:
- 🚫 **No face detected**  
- 👥 **Multiple faces**  
- 👀 **Not looking at screen**  
- 📱 **Phone detected**  
- 🏃 **Person left frame**  
✅ **Audio alert system** (`siren-alert-96052.mp3`)  
✅ **Automatic snapshots** with timestamps  
✅ **Violation logs in CSV** (downloadable)  
✅ **Snapshots ZIP export** for offline review  
✅ **Live FPS chart** (debug mode)  

---

## 📂 Project Structure
```
├── app.py                  # Main Streamlit application
├── README.md               # Documentation
└── siren-alert-96052.mp3   # Alert sound file
```

---

## ⚙️ Installation & Setup  

### 1. Clone the repo  
```bash
git clone https://github.com/your-username/proctorvision.git
cd proctorvision
```

### 2. Create virtual environment & activate  
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies  
```bash
pip install -r requirements.txt
```

### 4. Run the app  
```bash
streamlit run app.py
```

---

## 📊 How It Works  

1. **Start Monitoring** from the sidebar.  
2. YOLOv8 continuously scans the **webcam feed**.  
3. Violations (like multiple faces or phone usage) trigger:  
   - 📸 Snapshot capture  
   - 📝 Log entry with timestamp  
   - 🔊 Audio alert  
4. At the end of session:  
   - Export **CSV reports** of violations  
   - Download **all violation snapshots** as a ZIP  

---

## 🖼️ Dashboard Preview  

| Control Panel | Live Monitoring | Reports |
|---------------|----------------|---------|
| Select YOLO model, set confidence, enable alerts | Real-time webcam with bounding boxes | Export CSV + Snapshots ZIP |

---

## 🔮 Future Enhancements
- 🔐 Candidate **face recognition** for identity verification  
- 🤖 AI-based **anomaly detection** (detect unseen cheating patterns)  
- 📊 **Heatmaps & behavioral summaries** for post-exam review  
- 📚 **LMS integration** (Moodle, Google Classroom)  
- 🌍 Optimized for **low-bandwidth environments**  

---

## 👩‍💻 Author
**V. Sri Harshini**  

---

⚠️ **Note**: This project is a **prototype/demo** (due to GPU limitations) but demonstrates real-time proctoring using **YOLOv8 + Streamlit**.  
