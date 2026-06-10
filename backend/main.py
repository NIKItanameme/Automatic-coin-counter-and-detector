import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO
from collections import Counter
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import io
import base64
from PIL import Image
import os

app = FastAPI(title="Sanchay-AI Backend")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "best.pt")
try:
    model = YOLO(MODEL_PATH)
    print("--- [SYSTEM] YOLOv10 WEIGHTS LOADED ---")
except Exception as e:
    print(f"--- [ERROR] Model Load Failed: {e} ---")

# Denomination mapping
RUPEES_MAP = {"1": 1, "2": 2, "5": 5, "10": 10, "20": 20}

@app.post("/audit")
async def audit_coins(
    file: UploadFile = File(...),
    upi_id: str = Form("resident@rbi"),
    manual_total: float = Form(0),
    savings_split: float = Form(20)
):
    try:
        # Load Image
        content = await file.read()
        nparr = np.frombuffer(content, np.uint8)
        image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        # 1. YOLO Detection
        results = model.predict(source=image_rgb, imgsz=640, conf=0.50, iou=0.45)
        annotated_img_bgr = results[0].plot()
        annotated_img_rgb = cv2.cvtColor(annotated_img_bgr, cv2.COLOR_BGR2RGB)
        detections = results[0].boxes

        # 2. Surface Analysis (Rust/Oxidation)
        hsv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)
        lower_rust = np.array([0, 40, 40]) 
        upper_rust = np.array([18, 255, 140])
        mask = cv2.inRange(hsv, lower_rust, upper_rust)
        
        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        _, binary_mask = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)

        total_rust_pixels = 0
        total_coin_pixels = 0
        ai_total = 0
        denom_counts = Counter()

        if len(detections) > 0:
            for det in detections:
                x1, y1, x2, y2 = map(int, det.xyxy[0])
                coin_surface = binary_mask[y1:y2, x1:x2]
                rust_patch = mask[y1:y2, x1:x2]
                
                total_rust_pixels += np.sum((rust_patch > 0) & (coin_surface > 0))
                total_coin_pixels += np.sum(coin_surface > 0)
                
                label_idx = int(det.cls[0])
                label_name = model.names[label_idx]
                
                val = RUPEES_MAP.get(label_name, 0)
                denom_counts[val] += 1
                ai_total += val

        # 3. Calculations
        rust_percent = (total_rust_pixels / total_coin_pixels * 100) if total_coin_pixels > 0 else 0
        final_amount = manual_total if manual_total > 0 else ai_total
        
        savings_val = final_amount * (savings_split / 100)
        charity_val = final_amount * 0.05
        upi_val = max(0, final_amount - savings_val - charity_val)
        
        bonus = 0.50 if (rust_percent < 1.0 and final_amount > 0) else 0.0
        net_deposit = final_amount + bonus

        # 4. Prepare Response
        # Convert annotated image to base64
        pil_img = Image.fromarray(annotated_img_rgb)
        buff = io.BytesIO()
        pil_img.save(buff, format="JPEG")
        img_str = base64.b64encode(buff.getvalue()).decode("utf-8")

        # Breakdown Data for Charts
        breakdown = [
            {"name": f"₹{k}", "value": v, "total": k*v} 
            for k, v in sorted(denom_counts.items(), reverse=True)
        ]

        response_data = {
            "summary": {
                "total_coins": len(detections),
                "ai_value": ai_total,
                "final_amount": final_amount,
                "oxidation": f"{rust_percent:.1f}%",
                "audit_status": "FIT ✅" if rust_percent <= 12.0 else "UNFIT ⚠️",
                "mint_bonus": bonus
            },
            "distribution": {
                "upi_wallet": round(upi_val, 2),
                "digital_gold": round(savings_val, 2),
                "charity": round(charity_val, 2),
                "net_credit": round(net_deposit, 2)
            },
            "breakdown": breakdown,
            "image": f"data:image/jpeg;base64,{img_str}"
        }

        return JSONResponse(content=response_data)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Serve Static Frontend
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static/index.html"))

@app.get("/health")
async def health_check():
    return {"status": "online", "model_loaded": model is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
