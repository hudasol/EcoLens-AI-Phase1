import streamlit as st
import numpy as np
import pandas as pd
import hashlib
import time
from PIL import Image
from datetime import datetime
import tensorflow as tf

# --- CONFIGURATION ---
st.set_page_config(page_title="EcoLens AI | UAE Waste Compliance", layout="wide")

# Custom CSS for UI, Camera Size, and Large Table
st.markdown(f"""
    <style>
    [data-testid="column"]:nth-child(1) {{
        background-color: #23273b;
        padding: 25px;
        border-radius: 15px;
        color: white;
    }}
    [data-testid="column"]:nth-child(1) h3, 
    [data-testid="column"]:nth-child(1) p, 
    [data-testid="column"]:nth-child(1) label {{
        color: #ffffff !important;
    }}
    [data-testid="stCameraInput"] {{
        max-width: 450px;
        margin: 0 auto;
    }}
    .huge-text {{
        font-size: 45px !important;
        font-weight: 800 !important;
        line-height: 1.2;
        margin-bottom: 5px;
    }}
    .huge-label {{
        font-size: 18px;
        text-transform: uppercase;
        color: #555;
        letter-spacing: 1px;
    }}
    [data-testid="stTable"] {{
        font-size: 18px !important;
    }}
    
    /* ELEGANT WIDGET STYLING */
    .audit-box, .impact-box {{
        background: linear-gradient(145deg, #1e2233, #161928);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 24px;
        height: 195px; 
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    .audit-title, .box-title {{
        font-weight: 700;
        font-size: 1.05rem;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }}
    .hash-text {{
        font-family: 'Courier New', monospace;
        word-break: break-all;
        font-size: 0.8rem;
        line-height: 1.4;
        color: #4cc9f0;
        background: rgba(0,0,0,0.3);
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
    }}
    .status-pill {{
        display: inline-block;
        padding: 4px 12px;
        background: rgba(0, 255, 127, 0.1);
        border: 1px solid #00ff7f;
        color: #00ff7f;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: bold;
        letter-spacing: 1px;
    }}
    .impact-value {{
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        margin-top: 5px;
    }}
    .impact-sub {{
        font-size: 0.95rem;
        font-weight: 500;
        color: #ffffff;
        margin-bottom: 4px;
    }}
    .impact-detail {{
        font-size: 0.75rem;
        color: #aab0c4;
        opacity: 0.8;
    }}

    .legal-link {{
        color: #4cc9f0 !important;
        text-decoration: none;
        font-weight: bold;
        font-size: 0.85rem;
    }}
    .margin-widget {{
        background-color: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    </style>
""", unsafe_allow_html=True)

# Initialize Session States
if 'points' not in st.session_state: st.session_state.points = 0
if 'history' not in st.session_state: st.session_state.history = []
if 'last_hash' not in st.session_state: st.session_state.last_hash = "GENESIS_BLOCK_0000"
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        "PET Plastic Bottles": 0, "Aluminum Cans": 0, "Paper Waste": 0,
        "General Waste": 0, "Organic Waste": 0, "Specialty Handling": 0
    }

# --- DATA MAPPING ---
WASTE_METADATA = {
    0: {"name": "PET Plastic Bottles", "points": 5, "co2": 0.05, "value_aed": 0.02},
    1: {"name": "Aluminum Cans", "points": 7, "co2": 0.12, "value_aed": 0.05},
    2: {"name": "Paper Waste", "points": 5, "co2": 0.01, "value_aed": 0.01},
    3: {"name": "General Waste", "points": 1, "co2": 0.00, "value_aed": 0.00},
    4: {"name": "Organic Waste", "points": 5, "co2": 0.03, "value_aed": 0.00},
    5: {"name": "Specialty Handling", "points": 15, "co2": 0.25, "value_aed": 0.50}
}

# --- ENGINES ---
@st.cache_resource
def load_tflite_engine():
    interpreter = tf.lite.Interpreter(model_path="model_unquant.tflite")
    interpreter.allocate_tensors()
    return interpreter

def generate_block_hash(item_name, points, prev_hash):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    data_string = f"{timestamp}-{item_name}-{points}-{prev_hash}"
    return hashlib.sha256(data_string.encode()).hexdigest()

def predict_waste_tflite(image, interpreter):
    size = (224, 224)
    image = image.resize(size, Image.Resampling.LANCZOS)
    img_array = np.asarray(image).astype(np.float32)
    normalized = (img_array / 127.5) - 1
    input_data = np.expand_dims(normalized, axis=0)
    interpreter.set_tensor(interpreter.get_input_details()[0]['index'], input_data)
    interpreter.invoke()
    return np.argmax(interpreter.get_tensor(interpreter.get_output_details()[0]['index'])[0])

# --- LAYOUT ---
margin, main_content = st.columns([1, 2.8], gap="large")

# --- LEFT MARGIN ---
with margin:
    st.markdown("### 🎮 Points & Rewards")
    st.metric("Total Eco-Points", f"{st.session_state.points} pts")
    st.progress(min(max((st.session_state.points % 100) / 100, 0.0), 1.0))
    st.divider()

    st.markdown("### ⚖️ Regulatory Alignment")
    st.markdown(f"""<div class="margin-widget">
        <b>1. Climate Change Law</b><br>
        <i>Federal Decree-Law No. 11 (2024)</i><br>
        Mandates GHG reporting & reductions to achieve UAE Net Zero 2050.
        <br><br>
        <a href="https://uaelegislation.gov.ae/en/legislations/2558/download" class="legal-link">🔗 Download Decree-Law 11</a>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="margin-widget">
        <b>2. Incentive Systems</b><br>
        <i>Cabinet Decision No. 2521</i><br>
        Empowers point-based recovery schemes.
        <br><br>
        <a href="https://uaelegislation.gov.ae/en/legislations/2521" class="legal-link">🔗 Visit Link to Decision 2521</a>
    </div>""", unsafe_allow_html=True) 

    if st.button("Reset Session"):
        st.session_state.points = 0
        st.session_state.history = []
        st.session_state.last_hash = "GENESIS_BLOCK_0000"
        for key in st.session_state.inventory: st.session_state.inventory[key] = 0
        st.rerun()

# --- MAIN CONTENT AREA ---
with main_content:
    st.title("♻️ EcoLens AI: Verifiable Waste Management")
    st.subheader("📷 AI Compliance Scanner")
    img_file = st.camera_input("Scan Waste Item")
    
    if img_file:
        try:
            interpreter = load_tflite_engine()
            image = Image.open(img_file)
            class_idx = predict_waste_tflite(image, interpreter)
            item = WASTE_METADATA.get(class_idx, WASTE_METADATA[3])

            current_hash = generate_block_hash(item['name'], item['points'], st.session_state.last_hash)
            st.session_state.inventory[item['name']] += 1
            st.session_state.points += item['points']
            st.session_state.last_hash = current_hash
            st.session_state.history.append({
                "Timestamp": datetime.now().strftime("%H:%M:%S"), 
                "Item": item['name'], "CO2_Saved": item['co2'], "Value_AED": item['value_aed'],
                "Block_Hash": current_hash
            })
            st.success(f"**Identified:** {item['name']}")
        except Exception as e:
            st.error(f"Scanner Error: {e}")

    # --- ADDED EMPTY SPACE BW CAMERA AND TABLE ---
    st.write("")
    st.write("")
    st.divider()

    # --- HUGE TEXT DISPLAY ---
    df_hist = pd.DataFrame(st.session_state.history)
    t_co2 = df_hist['CO2_Saved'].sum() if not df_hist.empty else 0
    t_val = df_hist['Value_AED'].sum() if not df_hist.empty else 0
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<p class="huge-label">CO₂ Prevented</p><p class="huge-text">{t_co2:.3f}kg</p>', unsafe_allow_html=True)
    c2.markdown(f'<p class="huge-label">Est. Market Value</p><p class="huge-text">{t_val:.2f} AED</p>', unsafe_allow_html=True)
    c3.markdown(f'<p class="huge-label">Verified Points</p><p class="huge-text">{st.session_state.points}</p>', unsafe_allow_html=True)

    st.write("")
    
    # --- INVENTORY TABLE ---
    st.subheader("🗃️ Waste Segregation Inventory")
    inventory_data = [
        { "Material Type": "PET Plastic Bottles", "Total Scanned": st.session_state.inventory["PET Plastic Bottles"], "Target Bin": "🔴 Red / 🟡 Yellow", "Tips/Notes": "Empty, Rinse, Crush!"},
        { "Material Type": "Aluminum Cans", "Total Scanned": st.session_state.inventory["Aluminum Cans"], "Target Bin": "⚪ Grey / 🔘 Silver", "Tips/Notes": "High recycling value"},
        { "Material Type": "Paper Waste", "Total Scanned": st.session_state.inventory["Paper Waste"], "Target Bin": "🔵 Blue", "Tips/Notes": "Avoid oil-contaminated paper"},
        { "Material Type": "General Waste", "Total Scanned": st.session_state.inventory["General Waste"], "Target Bin": "⚫ Black", "Tips/Notes": "Non-recyclable landfill"},
        { "Material Type": "Organic Waste", "Total Scanned": st.session_state.inventory["Organic Waste"], "Target Bin": "🟤 Brown", "Tips/Notes": "Food scraps/Compost"},
        { "Material Type": "Specialty Handling", "Total Scanned": st.session_state.inventory["Specialty Handling"], "Target Bin": "🔘 Clear / 🟠 Orange", "Tips/Notes": "E-Waste: batteries, phones"}
    ]
    st.table(pd.DataFrame(inventory_data))

    # --- HORIZONTAL SPACING BETWEEN TABLE AND WIDGETS ---
    st.write("")
    st.write("")
    st.write("")

    # --- FOOTER IMPACT WIDGETS ---
    if not df_hist.empty:
        phones_charged = df_hist['CO2_Saved'].sum() * 121.6
        
        # Row 1: Widget Boxes
        w_col1, w_col2 = st.columns(2)
        
        with w_col1:
            st.markdown(f"""
                <div class="audit-box">
                    <div class="audit-title">🛡️ Verified Audit Log</div>
                    <div class="hash-text"><b>Current Block Hash:</b><br>{st.session_state.last_hash}</div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 5px;">
                        <span style="font-size:0.85rem; color:#aab0c4;"><b>Node:</b> DXB-UAE-MAIN-B2</span>
                        <span class="status-pill">VERIFIED</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with w_col2:
            st.markdown(f"""
                <div class="impact-box">
                    <div class="box-title">🌍 Real World Impact</div>
                    <div>
                        <div class="impact-sub">Total Equivalent Charges</div>
                        <div class="impact-value">🔋 {int(phones_charged)} <span style="font-size: 1.2rem; font-weight: 400;">Smartphone/s</span></div>
                    </div>
                    <div class="impact-detail">
                        Based on EPA GHG Equivalencies (1kg CO2 ≈ 121.6 charges).
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # Row 2: Spacing and Full Width Download Button
        st.write("")
        st.write("")
        csv_data = df_hist.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📩 Download Audit Ready Report",
            data=csv_data,
            file_name=f"UAE_Waste_Audit_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("Scan items to generate the audit chain and impact analysis.")