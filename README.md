# 🌍 EcoLens AI: Phase 1 (Edge-Computing & ESG Compliance)

**EcoLens AI** is a decentralized, edge-computing framework designed for verifiable source-segregation and real-time carbon accounting. This repository focuses on the implementation of the **Waste Intelligence Monitor**, integrating RTSP IP camera streams with a blockchain-inspired audit log for ESG (Environmental, Social and Governance) reporting.

---

## 📂 Repository Structure

```text
EcoLens-AI-Phase2/
├── 📂 .github/               # CI/CD workflows for ESG compliance auditing
├── 📂 core/                  # [Proprietary] Edge-computing & RTSP stream logic
│   ├── 🐍 camera_stream.py   # RTSP IP Camera integration (OpenCV/BGR-to-RGB)
│   └── 🐍 processor.py       # Log processing and SHA-256 hash generation
├── 📂 dashboard/             # [Proprietary] Streamlit Waste Intelligence UI
│   └── 🐍 app.py             # Main UI for real-time monitoring & KPIs
├── 📂 data/                  # Audit logs and metadata
│   ├── 📄 ecolens_audit_log.csv # Blockchain-verified event log
│   └── 📄 classes.txt        # Classification labels (PET, Alum, etc.)
├── 📂 models/                # [Proprietary] TFLite quantized weights
│   └── 📄 model.tflite       # Edge-optimized inference model
├── 📄 .gitignore             # Prevents sensitive .csv and .env leaks
├── 📄 LICENSE                # Academic & Commercial usage terms
├── 📄 README.md              # Documentation & Implementation Guide
└── 📄 requirements.txt       # Dependencies (OpenCV, Streamlit, Pandas)
