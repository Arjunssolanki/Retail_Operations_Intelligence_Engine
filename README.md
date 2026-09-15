# 🏭 Retail Operations Intelligence Engine

A production-grade, cloud-native **Agentic Big Data Analytics Pipeline** that converts natural language business queries into executable Python data manipulation code. Built with **LangGraph, Google Gemini (via native Google GenAI SDK), AWS S3, ChromaDB, and MLflow**, this system implements an autonomous, stateful self-correction architecture to query relational enterprise datasets containing over **500,000 transaction records** in real time.

---

## 🏗️ System Architecture & MLOps Strategy

Traditional Text RAG pipelines break paragraphs into arbitrary chunks, which destroys tabular structures, column data types, and foreign key relationships. To handle enterprise analytics efficiently without crashing memory bounds or leaking tokens, this engine utilizes a **Hybrid Two-Track MLOps Architecture**:

## System Architecture & MLOps Strategy

![System Architecture Diagram](./architecture.jpg)

1. **Semantic Vector Track:** Master dimension profiles (`products.csv` and a structural blueprint sample of `customers.csv`) are mapped into conversational sentences, embedded locally via an open-source sentence transformer model (`all-MiniLM-L6-v2`), and stored in **ChromaDB**. This allows the AI agent to look up specific product IDs and metadata contexts semantically.
2. **Deterministic Code Execution Track:** The heavy transaction ledger (`sales.csv`, holding **500,000 rows**) is stored natively in system memory as a cached Pandas DataFrame. The agent uses structural schemas to write optimized, vectorized Python code. The engine then runs code sandboxes over all half-million entries in milliseconds.

## LangGraph Agentic Lifecycle & Self-Correction Pipeline
   ![Agent Flowchart](./agent_flowchart.jpeg)

### 📊 Ingested Data Warehouse Profile

- **`products.csv`**: `(8, 4)` — 8 operational SKUs with distinct category boundaries.
- **`customers.csv`**: `(10000, 4)` — 10,000 unique member and normal profiles across metropolitan cities.
- **`sales.csv`**: `(500000, 8)` — 500,000 historical rows mapping transaction keys, payments, and ratings.

---

## 📂 Project Structure

```text
Retail_Operations_Engine/
│
├── .env                     # Hidden file containing localized credentials tokens
├── .gitignore               # Excludes sensitive environment configurations from version tracking
├── app.py                   # High-performance interactive Streamlit dashboard frontend UI
├── config.py                # System properties manager parsing the active .env profile
├── data_processor.py        # Maps tabular formats to semantic documents and extracts schema templates
├── generate_and_upload_data.py # Generates 500,000 relational database rows and provisions AWS S3
├── graph_engine.py          # Assembles the core LangGraph state node logic with Gemini & MLflow
├── graph_state.py           # Declares strict TypedDict dictionary schemas for shared memory
├── logger_config.py         # Standardizes runtime file logs for production tracking
├── setup_infrastructure.py  # Runs verification connection smoke checks against AWS S3
├── vector_store.py          # Initialises ChromaDB with local sentence transformers
└── logs/
    └── pipeline.log         # Real-time application trace log file
````

---

## 🚀 Terminal Execution Guide

### 📋 1. Install Dependencies

Open your workspace terminal and install the required library ecosystem packages:

```bash
pip install streamlit pandas google-genai langgraph chromadb sentence-transformers torchvision torch mlflow boto3 python-dotenv grandalf
```

### 📁 2. Workspace Storage Space Setup

Create the physical storage containers required for runtime logs and MLflow experiment runs:

```bash
mkdir logs mlruns
```

### 🔒 3. Configure Local Credentials

Create a completely plain text file named exactly `.env` in your root folder and populate it with your active variables:

```text
GEMINI_API_KEY=AIzaSyYourActualGoogleGeminiAPIKey
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=ap-south-1
S3_BUCKET_NAME=retail-operations-intelligence-engine-lake
```

### ☁️ 4. Cloud Data Lake Infrastructure Initialization

Run the AWS S3 verification gatekeeper script to test security clearance:

```bash
python setup_infrastructure.py
```

Generate the 500,000-row relational retail data sets and synchronize them to your live S3 bucket:

```bash
python generate_and_upload_data.py
```

### 📈 5. Activate the MLOps MLflow Server

Open a dedicated, independent terminal window to track pipeline telemetry and launch the metrics UI:

```bash
mlflow ui
```

The interface dashboard will boot up immediately at `http://127.0.0.1:5000`.

### 🖥️ 6. Launch the Streamlit Portal Space

In your main terminal workspace, trigger the graphical dashboard panel:

```bash
streamlit run app.py
```

The interface control room web application will display on screen at `http://localhost:8501`.

---

## 🛠️ Operating Dashboard Workflows

1. **Ingest Cloud Datasets:** Click the **`📡 Sync & Ingest from AWS S3`** button on the left sidebar. This downloads the half-million transaction records out of S3 directly into cached local system memory.
2. **Align Vector Spaces:** Click **`🏗️ Build Hybrid Semantic Vector Space`** to load your product and sample customer layout templates into ChromaDB.
3. **Query the Analyst Agent:** Input your natural language question or pick a template example. Press **`🚀 Execute Agent Analysis`**.

---

## 🔍 Self-Correction Capabilities Demonstration

If the underlying LLM attempts to query data from a non-existent local file path or introduces a syntax edge-case, the system automatically uses its self-correcting logic:

```python
# System-generated Pandas execution trace capturing dynamic context re-routing
import pandas as pd

try:
    sales_df = sales  # Intercepted from active session variables mapping
except NameError:
    sales_df = pd.read_csv("sales.csv") # Autonomous error boundary recovery layout

result = sales_df["Total_Revenue"].sum()
```

The runtime error trace is piped straight back into Gemini. The agent reviews the crash log, fixes the code snippet, and re-executes the data query loop completely in the background—providing the end-user with clean insights and calculated metrics without a single application crash. All code execution attempts, retries, and processing latencies are securely logged to the **MLflow Dashboard**.
