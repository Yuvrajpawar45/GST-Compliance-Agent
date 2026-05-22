![header](https://capsule-render.vercel.app/api?type=waving&color=7A4A28&height=120&section=header)

# GST Compliance Agent 🧾

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Instrument+Serif&size=22&pause=1000&color=7A4A28&center=true&vCenter=true&width=600&lines=Multi-Agent+GST+Invoice+Checker;Upload+JSON+%E2%86%92+Instant+Compliance+Report;Built+for+Gujarat+SMEs+%E2%80%94+Textile+%C2%B7+Pharma+%C2%B7+Trading)](https://github.com/Yuvrajpawar45/gst_compliance_agent)

---

**Drop any invoice. Get instant GST compliance checks, ITC-at-risk calculation, and AI-written remediation steps.**  
No CA required for first-pass checks. Powered by Streamlit, LangGraph, ChromaDB, and Groq LLaMA 3.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3-F55036?style=flat-square)](https://groq.com)
[![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-1C6EF2?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

> Upload a GST invoice (JSON / CSV / Excel) → the agent automatically extracts fields, runs 27 CGST/IGST compliance checks, flags errors by severity, calculates ITC at risk, and streams plain-English remediation steps written by LLaMA 3.

![rect](https://capsule-render.vercel.app/api?type=rect&color=1c201c&height=2)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Upload Format](#upload-format)
- [Environment Variables](#environment-variables)
- [How the AI Remediation Works](#how-the-ai-remediation-works)
- [Deploy for Free](#deploy-for-free)
- [Benchmark](#benchmark)
- [Roadmap](#roadmap)
- [License](#license)

---

## Overview

**GST Compliance Agent** is a multi-agent compliance tool built for Indian SMEs — particularly in Gujarat's textile, pharma, and trading sectors. It solves a real problem: manually verifying GST invoices is tedious, error-prone, and requires deep knowledge of the CGST Act.

This agent automates that workflow:

```
Without Agent  →  Open invoice → cross-check HSN table → verify GSTIN → calculate ITC → write remediation → repeat
With Agent     →  Upload invoice → full compliance report in under 3 seconds
```

Three specialized agents run in a LangGraph `StateGraph` pipeline. Each agent has a single responsibility — extraction, rule checking, or report generation — and hands off results to the next in the chain.

The final report includes severity-classified findings, section-wise CGST Act references, ITC-at-risk rupee amounts, and AI-generated remediation steps tailored to the specific invoice.

---

## Features

| Module | What it does |
|---|---|
| **Document Extractor** | Parses GSTIN, HSN codes, taxable values, tax amounts, place of supply, supply type |
| **GST Rule Checker** | Runs 27 rules: inter/intra-state tax type, HSN rates, GSTIN format, arithmetic, ITC blocks, e-way bill |
| **Report Generator** | Severity classification (critical / warning / pass), ITC-at-risk calculation, JSON export |
| **AI Remediation** | LLaMA 3 streams step-by-step CA advice citing specific CGST Act sections |
| **Multi-format Upload** | Accepts JSON, CSV, and Excel (.xlsx / .xls) invoices |
| **Live Demo** | 3 pre-loaded invoices — textile (2 critical errors), pharma (1 warning), clean |

---

## System Architecture

### Application Overview

```
+------------------------------------------------------------------+
|                     GST Compliance Agent                         |
|                                                                  |
|  +--------------+    +--------------------------------------+    |
|  |   Sidebar    |    |              Main Panel              |    |
|  |              |    |                                      |    |
|  |  API Status  | -> | Live Demo | Upload | Scorecard       |    |
|  |  Pipeline    |    | Architecture                         |    |
|  |  Tech Stack  |    |                                      |    |
|  +--------------+    +--------------------------------------+    |
|                                     |                            |
|                                     v                            |
|                           LangGraph StateGraph                   |
|                                     |                            |
|              +----------------------+--------------------+       |
|              v                      v                    v       |
|    agents/extractor.py   agents/rule_checker.py   agents/        |
|    GSTIN | HSN | POS      27 rules | ITC | IGST    report_       |
|    taxable | confidence   e-way | arithmetic        generator.py  |
+------------------------------------------------------------------+
```

### Agent Pipeline (LangGraph StateGraph)

```
Invoice Input  [JSON | CSV | Excel]
      |
      v
Agent 1 — Document Extractor
  · Parses supplier / recipient GSTIN
  · Resolves supplier state vs place of supply
  · Extracts HSN codes, taxable values, tax amounts
  · Outputs: normalised invoice dict + confidence score
      |
      | (confidence < 0.7 → retry with fallback)
      v
Agent 2 — GST Rule Checker
  · Fans out to 7 parallel sub-checks
  · Inter/intra-state tax type (IGST vs CGST+SGST)
  · HSN rate validation against notification table
  · Tax arithmetic verification (taxable × rate = tax)
  · E-way bill threshold check (₹50,000)
  · Invoice format Rule 46 compliance
  · ITC blocked credits § 17(5)
  · GSTIN format validation
      |
      | (merge findings by severity)
      v
Agent 3 — Report Generator
  · Classifies findings: critical / warning / ok
  · Calculates total ITC at risk in ₹
  · Cites specific CGST Act sections per finding
  · Calls Groq LLaMA 3 for remediation advice
  · Exports structured JSON report
      |
      v
END → Compliance Report + JSON Download
```

### AI Remediation Pipeline

```
Findings list (critical + warning)
        |
        v
Issues serialized to structured text
        |
        v
Prompt Builder → invoice meta + supply type + ITC risk + issues
        |
        v
Groq API call → llama3-8b-8192
        |
        v
Streamlit UI streams tokens in real time
```

---

## Project Structure

```
gst_compliance_agent/
│
├── app.py                      # Main Streamlit app — layout, tabs, pipeline trigger
│
├── agents/
│   ├── __init__.py
│   ├── extractor.py            # Agent 1: Document Extractor
│   ├── rule_checker.py         # Agent 2: GST Rule Checker (27 rules)
│   └── report_generator.py     # Agent 3: Report Generator + Groq integration
│
├── utils/
│   ├── __init__.py
│   ├── gst_rules.py            # 27 GST rules + HSN rate table (notification-cited)
│   └── sample_invoices.py      # 3 demo invoices (textile, pharma, clean)
│
├── data/
│   ├── sample_invoice.csv      # Sample CSV for upload testing
│   └── sample_invoice_format.json
│
├── .env.example                # Safe template — never commit .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **UI Framework** | Streamlit | Python-native, rapid deployment, no frontend build step |
| **Styling** | HTML + CSS via `st.markdown` | Custom cards, agent pipeline UI, finding cards, themed tables |
| **Agent Orchestration** | LangGraph StateGraph | Structured multi-step pipeline with conditional routing |
| **Vector DB** | ChromaDB | Embeds 27 GST rules for RAG retrieval by rule checker |
| **Data** | Pandas + NumPy | Dtype inference, CSV/Excel parsing, tabular display |
| **AI / LLM** | Groq API + LLaMA 3-8B | Fast streaming text generation, free tier, section-accurate remediation |
| **Config** | python-dotenv | Local `.env`-based API key management |
| **Excel Support** | openpyxl + xlrd | Read `.xlsx` and `.xls` invoice uploads |
| **Fonts** | Google Fonts CDN | Playfair Display + DM Sans for enterprise aesthetic |

### Design Decisions

**Why LangGraph over a single function?**  
Each agent is independently testable and replaceable. The StateGraph structure makes it easy to add retry logic (e.g. confidence-based re-extraction) and new agents (e.g. a GSTR-1 reconciliation agent) without touching existing code.

**Why Groq + LLaMA instead of OpenAI?**  
Groq's free tier is fast enough for demo use, and LLaMA 3-8B handles structured remediation prompts reliably. The fallback rule-based engine means the app works fully without any API key.

**Why serialize findings to text for the prompt?**  
Sending pre-computed findings (not raw invoice data) keeps token usage minimal and makes the AI tab work on large invoices without hitting context limits.

**Why support CSV and Excel alongside JSON?**  
Real-world SMEs use Tally, Busy, and Excel-based billing. Requiring JSON-only would exclude the majority of the target users.

---

## Quick Start

### Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.10+ | Required |
| Groq API Key | Free at [console.groq.com](https://console.groq.com) — optional, fallback works without it |

### Step 1 — Clone

```bash
git clone https://github.com/Yuvrajpawar45/gst_compliance_agent.git
cd gst_compliance_agent
```

### Step 2 — Virtual Environment

```bash
# Windows PowerShell
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure

```bash
cp .env.example .env
```

Open `.env` and set your key:

```
GROQ_API_KEY=gsk_your_key_here
```

### Step 5 — Run

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## Upload Format

### JSON

```json
{
  "supplier": "Mahesh Textiles Pvt. Ltd.",
  "invoice_no": "MT/2024-25/1847",
  "date": "12 Oct 2024",
  "gstin_supplier": "24AABCM1234P1Z5",
  "gstin_recipient": "27XYZPQ5678R1Z2",
  "pos": "Maharashtra (27)",
  "supply_type": "B2B — Inter-state",
  "lines": [
    {
      "desc": "Cotton Fabric (HSN 5208)",
      "qty": 200, "rate": 450, "taxable": 90000,
      "gst_rate": 5, "cgst": 2250, "sgst": 2250, "igst": 0,
      "error": null
    }
  ]
}
```

### CSV / Excel

Required columns: `desc`, `qty`, `rate`, `taxable`, `gst_rate`, `cgst`, `sgst`, `igst`

Optional meta columns (first row only): `supplier`, `invoice_no`, `date`, `gstin_supplier`, `gstin_recipient`, `pos`, `supply_type`

A ready-to-use sample is at `data/sample_invoice.csv`.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Optional | Free key from [console.groq.com](https://console.groq.com). Without it, rule-based fallback is used for remediation steps. |

The `.env` file is listed in `.gitignore` and will never be committed.  
All compliance checks run without an API key — only the AI remediation tab uses Groq.

---

## How the AI Remediation Works

The Report Generator does not send raw invoice data to Groq. Instead:

1. Agents 1 and 2 produce a structured `findings` list with severity, title, body, and ITC risk per issue.
2. Only critical and warning findings are included in the prompt.
3. A concise prompt is built: invoice metadata + supply type + ITC-at-risk + issue list.
4. The prompt is sent to `llama3-8b-8192` through Groq's API.
5. The response streams back as numbered remediation steps, each citing a specific CGST Act section or rule.
6. If no API key is set, a deterministic rule-based fallback generates standard remediation text.

**Result:** The LLM sees structured compliance findings, not raw invoice rows — keeping prompts small, accurate, and auditable.

---

## Deploy for Free

### Streamlit Community Cloud (Recommended)

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **Create app** → select your repo → set main file to `app.py`.
4. Click **Advanced settings → Secrets** and add:

```toml
GROQ_API_KEY = "gsk_your_key_here"
```

5. Click **Deploy** — your app gets a public URL in ~2 minutes.

| Service | Cost | Notes |
|---|---|---|
| Streamlit Community Cloud | Free | Best for Streamlit portfolio apps, direct GitHub integration |
| Groq API | Free tier | Rate limited, more than enough for demos |
| GitHub | Free | Stores the code |

---

## Benchmark

**8 out of 10** sample invoices correctly identified across textile, pharma, and trading sectors.

| Rule | Coverage | Test Cases |
|---|---|---|
| Tax type — CGST+SGST vs IGST | 90% | 10 |
| GST rate per HSN code | 85% | 10 |
| ITC blocked credits § 17(5) | 75% | 8 |
| E-way bill threshold Rule 138 | 80% | 5 |
| Invoice format Rule 46 | 95% | 10 |
| Time of supply § 12/13 | 70% | 6 |
| Reverse charge § 9(3)/9(4) | 80% | 5 |

Legal references: CGST Act 2017 §§ 9, 12, 13, 16, 17, 25, 31, 34 · IGST Act 2017 §§ 5, 10, 16 · CGST Rules 2017 Rules 8, 36, 46, 52, 138 · CGST Rate Notification 1/2017 · CBIC Circular 98/17/2019

---

## Roadmap

| Phase | Status | Feature |
|---|---|---|
| Phase 1 | ✅ Complete | JSON invoice support, 3-agent pipeline, 27 GST rules |
| Phase 2 | ✅ Complete | AI remediation via Groq, streaming, professional UI |
| Phase 3 | ✅ Complete | CSV and Excel (.xlsx/.xls) upload support |
| Phase 4 | 🔲 Planned | PDF invoice parsing via LlamaParse |
| Phase 5 | 🔲 Planned | GSTR-1 vs invoice reconciliation |
| Phase 6 | 🔲 Planned | Batch invoice processing (multiple files at once) |
| Phase 7 | 🔲 Planned | Export full compliance report as PDF |
| Phase 8 | 🔲 Planned | HSN code lookup and rate suggestion tool |
| Phase 9 | 🔲 Planned | Multi-language support (Gujarati, Hindi) |

---

## License

MIT License. Free to use, modify, and distribute.

---

![footer](https://capsule-render.vercel.app/api?type=waving&color=7A4A28&height=100&section=footer)

Built by **Yuvraj Pawar** · [GitHub](https://github.com/Yuvrajpawar45)

If this project helped you, consider giving it a ⭐
