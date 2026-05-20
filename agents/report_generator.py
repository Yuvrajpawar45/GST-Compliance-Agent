"""
Agent 3 — Report Generator
Uses Groq API (LLaMA 3) to generate natural-language remediation advice.
Falls back to rule-based generation if no API key is set.
"""

import os
from datetime import datetime


class ReportGenerator:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model   = "llama3-8b-8192"

    def generate(self, raw_invoice: dict, extracted: dict, findings: list) -> dict:
        critical = [f for f in findings if f["severity"] == "critical"]
        warnings = [f for f in findings if f["severity"] == "warning"]
        passed   = [f for f in findings if f["severity"] == "ok"]
        itc_at_risk = sum(f.get("itc_risk", 0) for f in findings)

        overall_status = (
            "NON_COMPLIANT"   if critical else
            "REVIEW_REQUIRED" if warnings else
            "COMPLIANT"
        )

        if self.api_key and (critical or warnings):
            actions = self._groq_actions(raw_invoice, extracted, critical, warnings)
        else:
            actions = self._rule_based_actions(critical, warnings)

        return {
            "report_generated_at": datetime.now().isoformat(),
            "invoice_no":          raw_invoice.get("invoice_no"),
            "supplier":            raw_invoice.get("supplier"),
            "overall_status":      overall_status,
            "summary": {
                "critical_count": len(critical),
                "warning_count":  len(warnings),
                "passed_count":   len(passed),
                "total_checks":   len(findings),
            },
            "itc_at_risk":         round(itc_at_risk, 2),
            "findings":            findings,
            "recommended_actions": actions,
            "ai_powered":          bool(self.api_key),
            "act_references": [
                "CGST Act 2017", "IGST Act 2017",
                "CGST Rules 2017 (Rule 46, Rule 138)",
                "CGST Rate Notification 1/2017",
                "CBIC Circular 98/17/2019",
            ],
        }

    def _groq_actions(self, invoice, extracted, critical, warnings):
        try:
            from groq import Groq
        except ImportError:
            return self._rule_based_actions(critical, warnings)

        issues_text = "\n".join(
            f"- [{f['severity'].upper()}] {f['title']}: {f['body']}"
            for f in (critical + warnings)
        )
        itc_risk = sum(f.get("itc_risk", 0) for f in critical + warnings)

        prompt = f"""You are a senior GST consultant in India. A compliance check found these issues:

Invoice: {invoice.get('invoice_no')} | Supplier: {invoice.get('supplier')}
Supply type: {extracted.get('supply_type_resolved')} ({extracted.get('supplier_state_name')} to {extracted.get('pos_state_name')})
ITC at risk: Rs {itc_risk:,}

Issues:
{issues_text}

Give exactly 3-5 concise actionable remediation steps for a CA or business owner.
Each step must cite the specific CGST Act section or rule number.
Plain numbered list only. No preamble. No markdown headers."""

        try:
            client = Groq(api_key=self.api_key)
            resp = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=500,
            )
            raw = resp.choices[0].message.content.strip()
            lines = [
                line.lstrip("0123456789. ").strip()
                for line in raw.split("\n")
                if line.strip() and line.strip()[0].isdigit()
            ]
            return lines if lines else [raw]
        except Exception as e:
            return self._rule_based_actions(critical, warnings) + [f"(Groq error: {e})"]

    def _rule_based_actions(self, critical, warnings):
        actions = []
        titles = " ".join(f["title"].lower() for f in critical + warnings)

        if "inter-state" in titles or "intra-state" in titles:
            actions.append("Issue a revised invoice with correct tax type (IGST for inter-state, CGST+SGST for intra-state). Cancel original — CGST Act § 34.")
        if "wrong gst rate" in titles:
            actions.append("Issue a credit note for overcharged GST or supplementary invoice for undercharged GST within same FY — CGST Act § 34(2).")
        if "itc" in titles:
            actions.append("Verify ITC eligibility under § 17(5) before filing GSTR-3B. Reverse ineligible ITC if already claimed.")
        if "e-way" in titles:
            actions.append("Generate e-way bill on ewaybillgst.gov.in before dispatch. Penalty: Rs 10,000 or tax amount (higher) — Rule 138.")
        if "arithmetic" in titles or "format" in titles or "gstin" in titles:
            actions.append("Correct invoice and re-issue. Ensure all mandatory fields per Rule 46 are present.")
        if not actions:
            actions.append("No immediate action required. Retain records for GSTR-1/GSTR-3B reconciliation.")
        return actions
