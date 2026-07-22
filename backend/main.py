import sys
import os
import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO
from collections import Counter
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# 1. ENVIRONMENT CONFIGURATION
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
os.environ['YOLO_CONFIG_DIR'] = '/tmp' 

print("--- [SYSTEM] STARTING SANCHAY-AI FASTAPI ENGINE ---", file=sys.stderr)

# Get directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")

# 2. LOAD THE MODEL
try:
    model_path = os.path.join(BASE_DIR, "best.pt")
    model = YOLO(model_path)
    print("--- [SYSTEM] YOLOv10 WEIGHTS LOADED SUCCESSFULLY ---", file=sys.stderr)
except Exception as e:
    print(f"--- [ERROR] Model Load Failed: {e} ---", file=sys.stderr)
    model = None

# Initialize FastAPI app
app = FastAPI(title="Sanchay-AI Backend API")

# Add CORS Middleware to allow requests from any origin (e.g. if loaded via file://)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. CORE LOGIC ENGINE ENDPOINT
@app.post("/audit")
async def audit_coins(
    file: UploadFile = File(...),
    savings_split: float = Form(20.0),
    manual_total: float = Form(0.0)
):
    try:
        # Read uploaded file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image_bgr is None:
            return JSONResponse(status_code=400, content={"error": "Invalid image file format."})
            
        # Convert to RGB for YOLO and consistency
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        if model is None:
            return JSONResponse(status_code=500, content={"error": "YOLO model not loaded."})

        # --- Step A: Precise YOLO Detection ---
        results = model.predict(source=image_rgb, imgsz=640, conf=0.50, iou=0.45)
        detections = results[0].boxes

        # --- Step B: Surface Analysis & Denomination Breakdown ---
        hsv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)
        # Rust/Oxidation range in HSV
        lower_rust = np.array([0, 40, 40]) 
        upper_rust = np.array([18, 255, 140])
        mask = cv2.inRange(hsv, lower_rust, upper_rust)
        
        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        _, binary_mask = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)

        total_rust_pixels = 0
        total_coin_pixels = 0
        # Mapping model class names to numeric values
        rupees_map = {"1": 1, "2": 2, "5": 5, "10": 10, "20": 20}
        ai_total = 0
        denom_counts = Counter()

        if len(detections) > 0:
            for det in detections:
                x1, y1, x2, y2 = map(int, det.xyxy[0])
                
                # Check bounding box bounds to avoid indexing errors
                y1, y2 = max(0, y1), min(binary_mask.shape[0], y2)
                x1, x2 = max(0, x1), min(binary_mask.shape[1], x2)
                
                coin_surface = binary_mask[y1:y2, x1:x2]
                rust_patch = mask[y1:y2, x1:x2]
                
                # Audit only the area where the coin exists
                total_rust_pixels += np.sum((rust_patch > 0) & (coin_surface > 0))
                total_coin_pixels += np.sum(coin_surface > 0)
                
                label_idx = int(det.cls[0])
                label_name = model.names[label_idx]
                
                val = rupees_map.get(label_name, 0)
                denom_counts[val] += 1
                ai_total += val

        # Calculate Audit Results
        rust_percent = (total_rust_pixels / total_coin_pixels * 100) if total_coin_pixels > 0 else 0
        final_amount = manual_total if manual_total > 0 else ai_total

        # --- Step C: NOVELTY - The Micro-Savings Bridge ---
        savings_val = final_amount * (savings_split / 100)
        charity_val = final_amount * 0.05
        upi_val = max(0, final_amount - savings_val - charity_val)
        
        # Mint Condition Bonus (Incentive for clean currency)
        bonus = 0.50 if (rust_percent < 1.0 and final_amount > 0) else 0.0
        net_deposit = final_amount + bonus
        
        audit_status = "FIT ✅" if rust_percent <= 12.0 else "UNFIT ⚠️"

        # Create dual response keys to support both frontend/index.html and frontend/script.js structures
        response_data = {
            # Response structure for index.html inline script:
            "total": final_amount,
            "savings": savings_val,
            "upi_credit": upi_val,
            "count": len(detections),
            
            # Response structure for script.js:
            "summary": {
                "final_amount": final_amount,
                "audit_status": audit_status,
                "oxidation": f"{rust_percent:.1f}%"
            },
            "distribution": {
                "digital_gold": savings_val,
                "net_credit": net_deposit,
                "upi_wallet": upi_val,
                "mint_bonus": bonus,
                "impact_fund": charity_val
            },
            "denominations": {str(k): v for k, v in denom_counts.items()}
        }
        
        print(f"--- [SYSTEM] AUDIT PROCESSED: {len(detections)} coins, total value: ₹{final_amount} ---", file=sys.stderr)
        return response_data
        
    except Exception as e:
        print(f"--- [ERROR] Audit execution failed: {e} ---", file=sys.stderr)
        return JSONResponse(status_code=500, content={"error": str(e)})

# Mount frontend files at root to serve index.html, script.js, etc.
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    print(f"--- [SYSTEM] MOUNTED FRONTEND STATIC FILES FROM: {FRONTEND_DIR} ---", file=sys.stderr)
else:
    print(f"--- [WARNING] Frontend directory not found at: {FRONTEND_DIR} ---", file=sys.stderr)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
