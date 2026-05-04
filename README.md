# 🧾 Intelligent Invoice Automation Platform

Enterprise invoice processing automation platform integrating **Azure Document Intelligence**, **UiPath RPA**, **Microsoft Power Automate**, and **Microsoft Copilot Studio** — built as a freelance portfolio project demonstrating production-grade intelligent automation architecture.

**Live Demo:** https://intelligent-automation-platform-satvik.streamlit.app
**API Docs:** https://intelligent-automation-platform.onrender.com/docs

---

## 🏗️ Architecture

[Invoice Upload]
│
▼
[Azure Document Intelligence]

Prebuilt Invoice Model
100% confidence extraction
Vendor, amounts, line items, PO numbers
│
▼
[Power Automate — Orchestration Layer]
Confidence-based routing
≥80% confidence → Approved queue
<80% confidence → Human review alert
Webhook callback to FastAPI
│
▼
[UiPath RPA — ERP Integration Layer]
Reads from Orchestrator queue
Attended robot enters data into target system
Audit trail logging
Webhook callback to FastAPI
│
▼
[Microsoft Copilot Studio — Conversational AI]
Natural language invoice queries
Pipeline status reporting
Running on Claude Sonnet 4.6
Environment: InvoiceAutomation (Dataverse-backed)

### ABBYY Vantage — Enterprise IDP
In the client production environment, **ABBYY Vantage** handles document extraction using its pre-trained Invoice Skill with spatial NLP and neural document classification. For this public portfolio demo, **Azure Document Intelligence** replicates the same architectural role since the client's enterprise ABBYY tenant cannot be exposed publicly. The architecture, routing logic, and integration patterns are identical.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Document Intelligence | Azure Document Intelligence (prebuilt-invoice) |
| Enterprise IDP (client) | ABBYY Vantage |
| Orchestration | Microsoft Power Automate |
| RPA | UiPath Studio Community 2026 + Cloud Orchestrator |
| Conversational AI | Microsoft Copilot Studio (Claude Sonnet 4.6) |
| Backend API | FastAPI + Uvicorn (Python 3.11) |
| Dashboard | Streamlit |
| API Deployment | Render |
| Dashboard Deployment | Streamlit Cloud |
| Identity | Microsoft Entra ID |

---

## 🚀 Features

- **Real invoice extraction** — upload any invoice PDF or image and get structured JSON output
- **Confidence-based routing** — ≥80% confidence auto-approves, below routes to human review
- **Full pipeline tracking** — each stage (Azure DI, Power Automate, UiPath, Copilot Studio) tracked per invoice
- **Conversational AI agent** — ask the Invoice Assistant questions in natural language
- **Live REST API** — fully documented with Swagger UI
- **End-to-end demo** — complete pipeline executes on every upload

---

## 📁 Project Structure

intelligent-automation-platform/
├── src/
│   ├── api/
│   │   └── main.py           # FastAPI backend
│   ├── dashboard/
│   │   └── app.py            # Streamlit dashboard
│   └── document_processing/
│       └── extractor.py      # Azure DI extractor
├── sample_invoices/
│   └── sample-invoice.pdf
├── requirements.txt
├── Procfile
└── runtime.txt

---

## 🔧 Local Setup

`ash
git clone https://github.com/SatvikSPandey/intelligent-automation-platform.git
cd intelligent-automation-platform
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
`

Create .env file:

AZURE_DOC_INTEL_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOC_INTEL_KEY=your_key_here

Run API:
`ash
uvicorn src.api.main:app --reload --port 8000
`

Run Dashboard:
`ash
streamlit run src/dashboard/app.py
`

---

## 👤 Author

**Satvik Pandey**
- GitHub: [github.com/SatvikSPandey](https://github.com/SatvikSPandey)
- LinkedIn: [linkedin.com/in/satvikpandey-433555365](https://linkedin.com/in/satvikpandey-433555365)
- Portfolio: [satvikspandey.netlify.app](https://satvikspandey.netlify.app)
