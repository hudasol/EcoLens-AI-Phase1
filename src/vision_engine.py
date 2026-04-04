import cv2
import numpy as np
import tensorflow as tf
import pandas as pd
import hashlib
import os
from datetime import datetime

# --- CONFIG ---
RTSP_URL = "http://192.168.1.213:8080/video" 
MODEL_PATH = "model_unquant.tflite"
LOG_FILE = "ecolens_audit_log.csv"

# --- LOAD ENGINES ---
interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def generate_hash(item, prev_hash):
    data = f"{datetime.now()}-{item}-{prev_hash}"
    return hashlib.sha256(data.encode()).hexdigest()

def get_last_hash():
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        if not df.empty: return df.iloc[-1]['Block_Hash']
    return "GENESIS_2026"

def trigger_sorting_feedback(item_type):
    """Signals for the three-bin physical setup."""
    colors = {
        "PET Bottle": "🔵 BLUE Bin (Plastic)",
        "Can": "🔴 RED Bin (Metal)",
        "General Waste": "⚪ WHITE Bin (General)"
    }
    msg = colors.get(item_type, "⚪ WHITE Bin (General)")
    print(f"[GPIO MOCK] {msg}")

# --- MAIN LOOP ---
cap = cv2.VideoCapture(RTSP_URL)
last_hash = get_last_hash()
session_counter = 0

print("🚀 EcoLens AI: Three-Bin Prototype")
print("👉 INSTRUCTIONS: Press 'SPACE' to Scan | Press 'q' to Quit")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: continue

    display_frame = frame.copy()
    cv2.putText(display_frame, "READY: SPACE TO SCAN", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    
    cv2.imshow("EcoLens Live Feed", display_frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'): break
        
    if key == ord(' '): 
        print("\n📸 Scanning...")
        
        img = cv2.resize(frame, (224, 224))
        img = np.expand_dims(img, axis=0).astype(np.float32)
        img = (img / 127.5) - 1 

        interpreter.set_tensor(input_details[0]['index'], img)
        interpreter.invoke()
        predictions = interpreter.get_tensor(output_details[0]['index'])[0]
        class_idx = np.argmax(predictions)
        confidence = predictions[class_idx]

        # --- THREE-BIN LOGIC ---
        # 0: PET Bottle, 1: Can. Everything else (2, 3, 4, 5) goes to General.
        if confidence > 0.75:
            if class_idx == 0:
                item_name = "PET Bottle"
            elif class_idx == 1:
                item_name = "Can"
            else:
                item_name = "General Waste"
        else:
            # If confidence is low, we don't guess—we send it to General
            item_name = "General Waste"
            confidence = 0.0 # Force confidence to 0 for the log if it was a "fail-safe" move

        session_counter += 1
        trigger_sorting_feedback(item_name)
        new_hash = generate_hash(item_name, last_hash)
        
        # Save Entry
        new_data = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Item": item_name,
            "CO2_Saved": 0.05 if item_name != "General Waste" else 0.0, 
            "Value_AED": 0.02 if item_name != "General Waste" else 0.0,
            "Block_Hash": new_hash
        }])
        new_data.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False)
        last_hash = new_hash
        
        # UI FEEDBACK
        result_text = f"SORTED: {item_name}"
        cv2.rectangle(display_frame, (0, 0), (750, 80), (0, 255, 0), -1)
        cv2.putText(display_frame, result_text, (20, 55), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.imshow("EcoLens Live Feed", display_frame)
        
        print(f"✅ Item classified as: {item_name}")
        cv2.waitKey(2000) 

cap.release()
cv2.destroyAllWindows()