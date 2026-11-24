# 🛡️ LogWeaver-AI-SOC

**Behavioral Analysis of Security Logs and Autonomous Response System Using Large Language Models (LLMs)**

> *Developed as part of the TÜBİTAK 2209-A Research Project: "Büyük Dil Modelleri (LLM) ile Güvenlik loglarının Davranışsal Analizi ve Otonom Yanıt Sistemi".*

---

## 📌 Overview

**LogWeaver-AI-SOC** is a containerized, microservices-based defensive security (Blue Team) system designed to reduce **alert fatigue** and **Mean Time to Respond (MTTR)** in Security Operations Centers (SOC). LogWeaver combines **Regex-based log preprocessing**, **OpenAI GPT-4o** behavioral analysis, **n8n** workflow automation, a **Flask mock firewall**, and a **Streamlit + Altair** dashboard.

---

## ⚙️ How It Works & Key Capabilities

- **Synthetic Log & Attack Simulation (`simulator.py`):** Generates realistic Snort-style alert logs using templates, random IPv4/ephemeral port generators, and weighted random scenario selection.
- **Regex Preprocessing & Normalization:** Extracts structured fields (alert message, classification, priority, protocol, source/destination IP and port) from raw log lines before LLM evaluation, reducing noise and token overhead.
- **Behavioral LLM Analysis (OpenAI GPT-4o):** Analyzes log context and multi-event patterns with a security analyst system prompt and enforced JSON output (`response_format={"type": "json_object"}`), classifying events as **True Positive** or **False Positive** with confidence/severity scores and reasoning.
- **n8n Automation & Response (`soar_handler.py` & n8n Workflow):** Filters for **True Positive** detections and sends JSON payloads via HTTP POST / Webhook to **n8n**, which routes threats based on `log_type` (e.g., Web vs. Network/Snort), triggers IP blocking, and sends email alerts.
- **Mock Firewall Service (`mock_firewall.py`):** Flask-based REST service exposing `/api/block_ip` (`POST`) to simulate IP blacklisting in an isolated Docker network.
- **Real-Time SOC Dashboard (`dashboard.py` / `ui.py`):** Reads append-only **JSON-Lines (JSONL)** records (`dashboard-data.json`) line-by-line into Pandas DataFrames and visualizes KPI cards, an **Altair** time-series area chart (*Attack Traffic / Cyber Pulse*), a **True vs. False Positive** donut chart, incident details/reasoning, and conditional links to n8n execution history for True Positives.
- **Containerized Microservices (`Dockerfile`, `docker-compose.yml`):** Orchestrates services (`snort_simulator`, `n8n_soar`, `mock_firewall`, and application components) over a dedicated Docker bridge network (`security_net`).

---

## 🧪 Tested Threat Scenarios

- **False Positive Filtering:** Distinguishes benign queries containing HTML/script or SQL-like strings (e.g., search/error text) from actual attacks, avoiding unnecessary blocks.
- **Webshell Upload & RCE:** Detects sequential activity such as probing `/uploads/`, uploading a `.php` file, and executing commands (`?cmd=whoami`) as a high-severity True Positive, triggering automated IP blocking and alert email.
- **Post-Exploitation & C2 Correlation:** Correlates prior Trojan/exploit indicators with suspicious outbound/DNS activity (such as a `.su` domain query) to identify potential Command & Control (C2) behavior and trigger containment.

---

## Repository Structure

```text
LogWeaver-AI-SOC/
├── logs/                       # Log files and runtime log outputs
├── .dockerignore               # Files excluded from Docker build context
├── .gitignore                  # Files ignored by Git
├── Dockerfile                  # Container image build instructions
├── docker-compose.yml          # Multi-service orchestration (simulator, n8n, firewall, etc.)
├── requirements.txt            # Python package dependencies
├── main.py                     # Main application entry point
├── simulator.py                # Template-based synthetic Snort log & attack generator
├── log_processor.py            # Log reading, parsing, and normalization utilities
├── analyzer.py                 # Core log analysis and alert orchestration
├── ai_agent.py                 # LLM prompt & analysis logic
├── batch_analyzer.py           # Batch log processing mode
├── realtime_analyzer.py        # Real-time log stream monitoring mode
├── web_log_analyzer.py         # Web log analysis logic
├── soar_handler.py             # Webhook / automation payload dispatch logic
├── mock_firewall.py            # Flask mock firewall API (/api/block_ip)
├── dashboard.py                # Streamlit + Altair SOC dashboard
├── ui.py                       # UI / interface module
├── config_batch_test.yaml      # Configuration for batch testing
├── config_realtime_lab.yaml    # Configuration for real-time lab runs
└── config_web.yaml             # Configuration for web log scenarios
```

---

## Getting Started

This project uses a **hybrid setup**: background services (`n8n_soar`, `mock_firewall`, and `snort_simulator`) run in **Docker**, while the main analysis CLI (`main.py`) and SOC dashboard (`dashboard.py`) run locally in **VS Code** inside a Python virtual environment (`.venv`).

### 1. Local Environment Setup (VS Code)
Create and activate a virtual environment, then install dependencies:

```bash
git clone [https://github.com/beyzaavcii/LogWeaver-AI-SOC.git](https://github.com/beyzaavcii/LogWeaver-AI-SOC.git)
cd LogWeaver-AI-SOC
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

*(Set your OpenAI API key via environment variables / `.env` rather than hardcoding it into source files.)*

---

### 2. Real-Time Analysis (`snort-realtime`)
1. Reset existing containers and start `n8n_soar`:
```bash
docker compose down
docker compose up --build -d n8n_soar
```
2. Open the n8n interface, then start the real-time analyzer in VS Code (waiting on the target log file):
```bash
python main.py snort-realtime logs/alert_fast
```
3. Start the remaining Docker services (`snort_simulator` and `mock_firewall`):
```bash
docker compose up -d snort_simulator mock_firewall
```
4. *(Optional)* Follow live simulator container logs in a separate terminal:
```bash
docker logs -f snort_simulator
```

---

### 3. Batch Analysis (`web-batch` & `snort-batch`)
Start `n8n_soar` and `mock_firewall` first and open the n8n interface:
```bash
docker compose up -d n8n_soar mock_firewall
```

- **Web Logs Batch Analysis:**
```bash
python main.py web-batch logs/access.log
```

- **Snort Logs Batch Analysis:**
```bash
python main.py snort-batch logs/test_alerts.log
```
*(You can also point `snort-batch` to a populated log file such as `logs/alert_fast`.)*

---

### 4. Launch the SOC Dashboard
In your active `.venv` terminal, start the Streamlit dashboard (`http://localhost:8501`):
```bash
streamlit run dashboard.py
```
