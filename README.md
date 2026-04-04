# EcoLens-AI-Phase1




EcoLens-AI-Phase2/
├── 📂 .github/               # CI/CD workflows for ESG compliance auditing
├── 📂 core/                  # [Proprietary] Edge-computing & RTSP stream logic
├── 📂 dashboard/             # [Proprietary] Streamlit Waste Intelligence UI
├── 📂 models/                # [Proprietary] TFLite quantized weights
├── 📄 .gitignore             # Prevents sensitive .csv and .env leaks
├── 📄 LICENSE                # Academic & Commercial usage terms
└── 📄 README.md              # Documentation & Implementation Guide




EcoLens-AI-Phase2/
├── 📄 README.md                # Project overview and setup instructions
├── 📄 requirements.txt         # Dependencies (opencv-python, streamlit, pandas, etc.)
├── 📂 core/
│   ├── 🐍 camera_stream.py      # Script for RTSP IP Camera integration
│   └── 🐍 processor.py          # Log processing and hash generation logic
├── 📂 dashboard/
│   └── 🐍 app.py                # Streamlit UI for the Waste Intelligence Monitor
├── 📂 data/
│   ├── 📄 ecolens_audit_log.csv  # Real-time audit log with block hashes
│   └── 📄 classes.txt            # Waste classification labels (0-5)
└── 📂 models/
    └── 📄 model.tflite           # Edge-optimized AI model[cite: 5]
