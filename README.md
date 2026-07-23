# 🪙 Automatic Coin Counter & Detector

An AI-powered web application that detects Indian coins from an uploaded image or live webcam feed using **YOLOv10**, calculates the total monetary value, provides denomination-wise counts, and offers a simple savings distribution summary.

## 🚀 Live Demo

**Railway Deployment:**
https://automatic-coin-counter-and-detector-production.up.railway.app/

## ✨ Features

* 🎯 AI-based Indian coin detection using YOLOv10
* 📷 Upload an image or use your webcam
* 💰 Automatic calculation of the total coin value
* 🔢 Denomination-wise coin count
* 📊 Savings and distribution summary
* ⚡ FastAPI backend with a responsive web interface

## 🛠️ Tech Stack

* Python
* FastAPI
* YOLOv10 (Ultralytics)
* OpenCV
* NumPy
* HTML, CSS & JavaScript
* Docker
* Railway

## 📋 Instructions

### Using an Image

1. Open the application.
2. Upload a clear image containing the coins.
3. Click **Audit/Detect**.
4. View the detected coins, denomination breakdown, and total value.

### Using the Webcam

For the best detection accuracy:

* ✅ Place the coins on a **plain white background**.
* ✅ Ensure the area has **good, even lighting**.
* ✅ Keep the camera steady and avoid blurry images.
* ✅ Position all coins fully inside the camera frame.
* ✅ Avoid shadows or reflections covering the coins.

## 📁 Project Structure

```text
Automatic-coin-counter-and-detector/
├── backend/
│   ├── main.py
│   ├── best.pt
│   └── run.py
├── frontend/
│   ├── index.html
│   └── script.js
├── requirements.txt
├── Dockerfile
└── README.md
```

## ▶️ Run Locally

```bash
git clone https://github.com/NIKItanameme/Automatic-coin-counter-and-detector.git

cd Automatic-coin-counter-and-detector

pip install -r requirements.txt

python backend/run.py
```

Then open:

```text
http://127.0.0.1:8000
```

## 👤 Author

**Nikita R**
