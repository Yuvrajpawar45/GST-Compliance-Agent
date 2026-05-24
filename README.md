# GST Compliance Agent

A multi-agent pipeline for automated GST invoice compliance checking. Upload a structured invoice (JSON, CSV, or Excel), run 27 deterministic CGST/IGST rules, calculate ITC at risk in ₹, and get AI-generated remediation steps citing specific CGST Act sections.

Built for Indian SMEs — textile, pharma, and trading — where manual invoice verification is the norm.

---

## What It Does

```
Input:  Invoice (JSON / CSV / Excel)
Output: Compliance report — severity-classified findings, ITC-at-risk (₹), remediation steps
Time:   < 3 seconds end-to-end
```

Three agents run sequentially. Each has a single responsibility:

| Agent | Responsibility |
|---|---|
| **Document Extractor** | Parses GSTIN, HSN codes, taxable values, tax amounts, place of supply, supply type |
| **GST Rule Checker** | Runs 27 rules — inter/intra-state tax type, HSN rate validation, arithmetic, ITC blocks § 17(5), e-way bill threshold, invoice format Rule 46 |
| **Report Generator** | Classifies findings (critical / warning / pass), calculates ITC at risk, cites CGST Act sections, calls Groq LLaMA 3 for remediation |

---

## Architecture

```
Invoice Input  [JSON | CSV | Excel]
      │
      ▼
Agent 1 — Document Extractor
  · Parses supplier / recipient GSTIN
  · Resolves supplier state vs place of supply
  · Extracts HSN codes, taxable values, tax amounts
  · Output: normalised invoice dict + confidence score
      │
      ▼
Agent 2 — GST Rule Checker
  · Inter/intra-state tax type (IGST vs CGST+SGST)
  · HSN rate validation against notification table
  · Tax arithmetic verification (taxable × rate = tax)
  · E-way bill threshold check (₹50,000)
  · Invoice format Rule 46 compliance
  · ITC blocked credits § 17(5)
  · GSTIN format validation
      │
      ▼
Agent 3 — Report Generator
  · Severity classification: critical / warning / pass
  · ITC at risk calculated in ₹
  · CGST Act section citations per finding
  · Groq LLaMA 3 remediation (rule-based fallback if no API key)
  · JSON export
      │
      ▼
Compliance Report + JSON Download
```

### AI Remediation — Design Decision

The LLM receives pre-computed findings, not raw invoice rows. This keeps prompts small, makes remediation auditable, and handles larger invoices without hitting context limits.

```
Findings list (critical + warning)
        │
        ▼
Structured text serialisation
        │
        ▼
Prompt: invoice meta + supply type + ITC risk + issue list
        │
        ▼
Groq API → llama3-8b-8192
        │
        ▼
Numbered remediation steps with CGST Act citations
```

---

## Project Structure

```
gst_compliance_agent/
│
├── app.py                      # Streamlit app — layout, tabs, pipeline trigger
│
├── agents/
│   ├── extractor.py            # Agent 1: Document Extractor
│   ├── rule_checker.py         # Agent 2: GST Rule Checker (27 rules)
│   └── report_generator.py     # Agent 3: Report Generator + Groq integration
│
├── utils/
│   ├── gst_rules.py            # 27 GST rules + HSN rate table
│   └── sample_invoices.py      # 3 demo invoices (textile, pharma, clean)
│
├── data/
│   ├── sample_invoice.csv
│   └── sample_invoice_format.json
│
├── .env.example
├── requirements.txt
└── README.md
```

---

## Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| UI | Streamlit | Rapid deployment, no frontend build step |
| Agent Pipeline | Custom Python classes | Single-responsibility, independently testable, easy to extend |
| Rules Engine | Local GST rule table | Deterministic checks with legal references — no LLM required for compliance logic |
| Data | Pandas | CSV/Excel parsing |
| LLM | Groq API + LLaMA 3-8B | Free tier, fast inference, handles structured remediation prompts reliably |
| Config | python-dotenv | `.env`-based API key management |
| Excel | openpyxl + xlrd | `.xlsx` and `.xls` support |

**Why separate agents over a monolithic function?**
Each agent is independently testable and replaceable. Adding a GSTR-1 reconciliation agent or a batch processing layer does not require rewriting the existing pipeline.

**Why CSV and Excel support alongside JSON?**
Real-world SMEs use Tally, Busy, and Excel-based billing. JSON-only would exclude the majority of the target segment.

---

## Quick Start

**Requirements:** Python 3.10+, Groq API key (optional — fallback works without it)

```bash
# Clone
git clone https://github.com/Yuvrajpawar45/gst_compliance_agent.git
cd gst_compliance_agent

# Virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# .\venv\Scripts\Activate.ps1  # Windows PowerShell

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add: GROQ_API_KEY=gsk_your_key_here

# Run
streamlit run app.py
# Opens at http://localhost:8501
```

---

## Invoice Format

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
      "qty": 200,
      "rate": 450,
      "taxable": 90000,
      "gst_rate": 5,
      "cgst": 2250,
      "sgst": 2250,
      "igst": 0
    }
  ]
}
```

### CSV / Excel

Required columns: `desc`, `qty`, `rate`, `taxable`, `gst_rate`, `cgst`, `sgst`, `igst`

Optional meta (read from first row): `supplier`, `invoice_no`, `date`, `gstin_supplier`, `gstin_recipient`, `pos`, `supply_type`

Sample at `data/sample_invoice.csv`.

---

## Environment Variables

| Variable | Required | Notes |
|---|---|---|
| `GROQ_API_KEY` | No | Free at [console.groq.com](https://console.groq.com). Without it, rule-based fallback generates remediation steps. All 27 compliance checks run without any API key. |

---

## Deployment

**Streamlit Community Cloud** is the recommended option for this stack.

```
1. Push to a public GitHub repo
2. Go to https://share.streamlit.io → sign in with GitHub
3. New app → select repo → set main file: app.py
4. Advanced settings → Secrets → GROQ_API_KEY = "your_key"
5. Deploy — live in ~2 minutes
```

| Service | Cost |
|---|---|
| Streamlit Community Cloud | Free |
| Groq API | Free tier (rate-limited, sufficient for demos) |
| GitHub | Free |

---

## GST Rule Coverage

27 rules across the following categories:

| Category | Legal Reference |
|---|---|
| Tax type: CGST+SGST vs IGST | IGST Act 2017 §§ 5, 10 |
| HSN rate validation | CGST Rate Notification 1/2017 |
| ITC blocked credits | CGST Act § 17(5) |
| E-way bill threshold | CGST Rules Rule 138 |
| Invoice format | CGST Rules Rule 46 |
| Time of supply | CGST Act §§ 12, 13 |
| Reverse charge | CGST Act §§ 9(3), 9(4) |
| GSTIN format | CGST Act § 25 |
| Tax arithmetic | CGST Act §§ 9, 16 |

Full legal references: CGST Act 2017 §§ 9, 12, 13, 16, 17, 25, 31, 34 · IGST Act 2017 §§ 5, 10, 16 · CGST Rules 2017 Rules 8, 36, 46, 52, 138 · CGST Rate Notification 1/2017 · CBIC Circular 98/17/2019

---

## Planned

- PDF invoice parsing
- GSTR-1 vs invoice reconciliation
- Batch invoice processing
- Compliance report PDF export
- HSN code lookup and rate suggestion

---

## License

MIT — free to use, modify, and distribute.

---

Built by [Yuvraj Pawar](https://github.com/Yuvrajpawar45)
