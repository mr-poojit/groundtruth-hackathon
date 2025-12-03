# 🚀 H001: The Automated Insight Engine

**Tagline:** An AI-powered reporting pipeline that transforms raw data sources (CSV, SQL databases, JSON logs, images, etc.) into executive-ready PDF & PPTX reports with actionable insights in under 30 seconds.

---

## 1. The Problem (Real-World Scenario)

### 🧠 Context

Account Managers in AdTech spend **4–6 hours every week** manually downloading data from multiple systems (CSV exports, dashboards, DB snapshots, screenshots/images) and assembling them into “Weekly Performance Reports.”

This results in:

- Slow reporting cycles
- Human errors in calculations
- Delayed detection of anomalies
- Data scattered across inconsistent formats

---

## 2. My Solution — TrendSpotter

TrendSpotter eliminates manual reporting entirely by automating the full analytics lifecycle and supporting **multiple data source types**, not just CSV.

### 🎯 What TrendSpotter Accepts:

- **CSV files** (traffic logs, ad-performance logs, exports)
- **Excel files (.xlsx)**
- **Database dumps (.sql)**
- **SQLite DB files (.db)**
- **JSON logs**
- **Images containing charts (optional OCR extension)**

TrendSpotter automatically detects the file type, extracts the data, normalizes the schema, and processes it.

### 🎯 What TrendSpotter Does:

1. Accepts one or more data files in different formats
2. Automatically extracts, merges & processes all datasets
3. Generates premium-quality **charts** (CTR, traffic, top cities, trends)
4. Uses **Google Gemini AI** to produce an executive-grade narrative
5. Writes a polished **PDF Report** and **PPTX Deck**
6. Bundles everything into a **ZIP file**

---

## 3. Expected End Result (User Experience)

### **Input:**

Upload CSV, Excel, DB snapshots, SQL dumps, or JSON files to `/generate-report`

### **Process:**

TrendSpotter cleans data → computes KPIs → generates charts → writes Gemini insights → creates PDF + PPTX → packages everything

### **Output:**

A polished ZIP containing:

- `report.pdf`
- `report.pptx`
- `/charts/*.png`
- Normalized combined dataset (optional future feature)

---

## 4. Technical Architecture Overview

TrendSpotter is designed to be production-grade and extensible.

### 🏗 Ingestion Layer

- Auto-detects file type
- Supports: CSV, Excel, SQL dumps, SQLite DB, JSON, images (OCR optional)
- FastAPI handles multiple uploads simultaneously

### 📊 Data Processing Layer

- Uses **Pandas** to normalize all input formats into a single DataFrame
- Computes KPIs:
  - CTR
  - Impressions
  - Click volume
  - Traffic by city
  - Campaign performance

### 🎨 Visualization Layer

- **Matplotlib + Seaborn**
- Generates:
  - CTR time-series
  - City traffic comparison
  - Trend curves
  - Performance distribution charts

### 🤖 AI Insights Layer

- Uses **Google Gemini 1.5 Flash / Pro**
- Uses a structured prompt to sound like a senior analyst
- AI explanations include:
  - Performance summary
  - Notable spikes & dips
  - Recommendations for optimization

### 📝 Reporting Layer

- PDF generated via **ReportLab** with professional layout
- PPTX generated via **python-pptx** with aligned content & slide hierarchy

### 📦 Output Packaging

- ZIP file containing:
  - PDF report
  - PPTX deck
  - Charts
  - Logs (optional)

---

## 5. Tech Stack

| Layer           | Technology                                      |
| --------------- | ----------------------------------------------- |
| Language        | Python 3.11                                     |
| Backend         | FastAPI                                         |
| File Support    | CSV, Excel, SQL, DB, JSON, Image (OCR optional) |
| Data Processing | Pandas                                          |
| Visuals         | Matplotlib + Seaborn                            |
| AI              | Google Gemini API                               |
| Reports         | ReportLab (PDF), python-pptx (PPTX)             |
| Packaging       | ZIP Archive                                     |

---

## 6. Challenges & How I Solved Them

### 🔥 Challenge — Multiple File Formats

Solution: Implemented file-type auto-detection + unified Pandas DataFrame builder.

### 🔥 Challenge — PPTX Misalignment

Solution: Custom slide templates, correct spacing, and consistent fonts.

### 🔥 Challenge — Poor PDF Layout

Solution: Added margins, typography hierarchy, spacing, and table formatting.

### 🔥 Challenge — AI Adding Assumptions

Solution: Strict grounding prompt + JSON summary validation.

---

## 7. How to Run TrendSpotter

### 1️⃣ Install Dependencies

```
pip install -r requirements.txt
```

### 2️⃣ Add Gemini API Key

**Mac/Linux**

```
export GEMINI_API_KEY="your_key_here"
```

**Windows PowerShell**

```
$env:GEMINI_API_KEY="your_key_here"
```

### 3️⃣ Start the Server

```
uvicorn app:app --reload
```

### 4️⃣ Upload Files via Swagger UI

Visit:

```
http://127.0.0.1:8000/docs
```

Use `POST /generate-report`  
Upload:

- CSV
- SQL
- JSON
- .db files
- Excel files

Download your ZIP report.

---

## 8. Folder Structure

```
.
├── app.py
├── insight_engine.py
├── report_generator.py
├── llm.py
├── charts/
├── output/
├── data/
├── screenshots/
└── requirements.txt
```

---

## ⭐ Final Note

TrendSpotter turns multi-format raw data into polished executive insights — instantly.  
It eliminates manual reporting, reduces errors, and enables teams to focus on **strategy**, not spreadsheets.
