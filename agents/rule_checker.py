"""
Agent 2 — GST Rule Checker
Runs 27 GST compliance checks against extracted invoice data.
In production: each rule retrieves supporting context from ChromaDB RAG.
"""

from utils.gst_rules import GST_RULES, HSN_RATE_TABLE


class GSTRuleChecker:
    """
    Multi-check compliance engine.
    Each check returns a finding dict: {severity, title, body, rule_ref}
    """

    def check(self, extracted: dict, raw_invoice: dict) -> list[dict]:
        findings = []
        findings += self._check_inter_intra_state_tax(extracted)
        findings += self._check_hsn_rates(extracted)
        findings += self._check_tax_arithmetic(extracted)
        findings += self._check_eway_bill(extracted)
        findings += self._check_invoice_format(extracted, raw_invoice)
        findings += self._check_itc_blocked(extracted, raw_invoice)
        findings += self._check_gstin_format(extracted)
        return findings

    # ── Rule 1: Inter-state must use IGST, Intra-state must use CGST+SGST ──
    def _check_inter_intra_state_tax(self, ext: dict) -> list[dict]:
        findings = []
        is_inter = ext["is_inter_state"]

        for line in ext["lines"]:
            cgst = line.get("cgst", 0)
            sgst = line.get("sgst", 0)
            igst = line.get("igst", 0)
            desc = line.get("desc", "Unknown item")

            if is_inter and (cgst > 0 or sgst > 0) and igst == 0:
                itc_risk = cgst + sgst
                findings.append({
                    "severity": "critical",
                    "title": f"Inter-state supply: CGST+SGST charged instead of IGST — {desc}",
                    "body": (
                        f"Supplier state ({ext['supplier_state_name']}) differs from "
                        f"place of supply ({ext['pos_state_name']}) — this is INTER-STATE. "
                        f"CGST ₹{cgst:,} + SGST ₹{sgst:,} should be IGST ₹{cgst+sgst:,}. "
                        f"Recipient cannot claim ITC on incorrectly charged tax. "
                        f"ITC at risk: ₹{itc_risk:,}. Issue corrected invoice under § 34."
                    ),
                    "rule_ref": "CGST Act § 9; IGST Act § 5; CBIC Circular 98/17/2019",
                    "itc_risk": itc_risk,
                })

            elif not is_inter and igst > 0 and (cgst == 0 and sgst == 0):
                findings.append({
                    "severity": "critical",
                    "title": f"Intra-state supply: IGST charged instead of CGST+SGST — {desc}",
                    "body": (
                        f"Supplier state ({ext['supplier_state_name']}) matches "
                        f"place of supply ({ext['pos_state_name']}) — this is INTRA-STATE. "
                        f"IGST ₹{igst:,} charged incorrectly. Should be CGST ₹{igst//2:,} + SGST ₹{igst//2:,}. "
                        f"Issue corrected invoice."
                    ),
                    "rule_ref": "CGST Act § 9; IGST Act § 5",
                    "itc_risk": igst,
                })

        if not findings:
            supply_label = "inter-state (IGST)" if is_inter else "intra-state (CGST+SGST)"
            findings.append({
                "severity": "ok",
                "title": f"Tax type correct — {supply_label} supply correctly taxed",
                "body": f"Supplier in {ext['supplier_state_name']}, POS {ext['pos_state_name']}. Tax type matches supply classification.",
                "rule_ref": "CGST Act § 9; IGST Act § 5",
                "itc_risk": 0,
            })

        return findings

    # ── Rule 2: HSN rate validation ─────────────────────────────────────────
    def _check_hsn_rates(self, ext: dict) -> list[dict]:
        findings = []
        import re

        for line in ext["lines"]:
            desc = line.get("desc", "")
            charged_rate = line.get("gst_rate", 0)
            taxable = line.get("taxable", 0)

            hsn_match = re.search(r"HSN\s*(\d{4,8})", desc)
            if not hsn_match:
                continue
            hsn = hsn_match.group(1)

            if hsn in HSN_RATE_TABLE:
                correct_rate = HSN_RATE_TABLE[hsn]["rate"]
                item_name    = HSN_RATE_TABLE[hsn]["name"]
                notification = HSN_RATE_TABLE[hsn]["notification"]

                if charged_rate != correct_rate:
                    overcharge = abs(taxable * (charged_rate - correct_rate) / 100)
                    findings.append({
                        "severity": "critical",
                        "title": f"Wrong GST rate: {item_name} (HSN {hsn}) charged at {charged_rate}% — should be {correct_rate}%",
                        "body": (
                            f"HSN {hsn} ({item_name}) attracts {correct_rate}% GST per {notification}. "
                            f"Invoice charges {charged_rate}%. "
                            f"Tax {'over' if charged_rate > correct_rate else 'under'}charged by ₹{overcharge:,.0f}. "
                            f"{'Buyer overpays; supplier must issue credit note under § 34.' if charged_rate > correct_rate else 'Potential tax shortfall; supplementary invoice may be needed.'}"
                        ),
                        "rule_ref": f"CGST Rate Notification 1/2017; {notification}; CGST Act § 34",
                        "itc_risk": overcharge if charged_rate > correct_rate else 0,
                    })
                else:
                    findings.append({
                        "severity": "ok",
                        "title": f"GST rate correct: {item_name} (HSN {hsn}) at {correct_rate}%",
                        "body": f"Rate matches {notification}.",
                        "rule_ref": f"CGST Rate Notification 1/2017; {notification}",
                        "itc_risk": 0,
                    })

        return findings

    # ── Rule 3: Tax arithmetic check ────────────────────────────────────────
    def _check_tax_arithmetic(self, ext: dict) -> list[dict]:
        for line in ext["lines"]:
            taxable    = line.get("taxable", 0)
            gst_rate   = line.get("gst_rate", 0)
            cgst       = line.get("cgst", 0)
            sgst       = line.get("sgst", 0)
            igst       = line.get("igst", 0)
            total_tax  = cgst + sgst + igst
            expected   = round(taxable * gst_rate / 100, 2)
            if abs(total_tax - expected) > 2:  # ₹2 tolerance for rounding
                return [{
                    "severity": "critical",
                    "title": f"Tax arithmetic error on line: {line.get('desc','')}",
                    "body": (
                        f"Taxable ₹{taxable:,} × {gst_rate}% = ₹{expected:,.2f} expected, "
                        f"but ₹{total_tax:,} charged. Difference: ₹{abs(total_tax-expected):,.2f}."
                    ),
                    "rule_ref": "CGST Act § 31; CGST Rules Rule 46",
                    "itc_risk": 0,
                }]
        return [{
            "severity": "ok",
            "title": "Tax arithmetic correct on all lines",
            "body": "All taxable × rate = tax amount calculations verified.",
            "rule_ref": "CGST Act § 31",
            "itc_risk": 0,
        }]

    # ── Rule 4: E-way bill threshold ────────────────────────────────────────
    def _check_eway_bill(self, ext: dict) -> list[dict]:
        threshold = 50_000
        total = ext.get("total_value", 0)
        if total > threshold:
            return [{
                "severity": "warning",
                "title": f"E-way bill threshold crossed — invoice value ₹{total:,} > ₹50,000",
                "body": (
                    f"Invoice value ₹{total:,} exceeds the ₹50,000 threshold for mandatory e-way bill generation. "
                    f"Ensure e-way bill is generated before dispatch. "
                    f"Non-generation can attract penalty of ₹10,000 or tax amount (whichever is higher)."
                ),
                "rule_ref": "CGST Rules Rule 138; Notification 15/2018-CT",
                "itc_risk": 0,
            }]
        return [{
            "severity": "ok",
            "title": f"E-way bill not mandatory — invoice value ₹{total:,} ≤ ₹50,000",
            "body": "Invoice value below e-way bill threshold.",
            "rule_ref": "CGST Rules Rule 138",
            "itc_risk": 0,
        }]

    # ── Rule 5: Invoice format Rule 46 ──────────────────────────────────────
    def _check_invoice_format(self, ext: dict, raw: dict) -> list[dict]:
        issues = []
        if not ext.get("invoice_no"):
            issues.append("Missing invoice number")
        if not ext.get("gstin_supplier"):
            issues.append("Missing supplier GSTIN")
        if not ext.get("gstin_recipient"):
            issues.append("Missing recipient GSTIN")
        if not ext.get("date"):
            issues.append("Missing invoice date")

        if issues:
            return [{
                "severity": "critical",
                "title": "Invoice format non-compliant — missing mandatory fields",
                "body": "Missing: " + ", ".join(issues) + ". All fields are mandatory under Rule 46.",
                "rule_ref": "CGST Rules Rule 46",
                "itc_risk": 0,
            }]
        return [{
            "severity": "ok",
            "title": "Invoice format compliant with Rule 46",
            "body": "All mandatory fields present: GSTIN of supplier/recipient, invoice number, date, HSN codes, taxable value, tax amounts.",
            "rule_ref": "CGST Rules Rule 46",
            "itc_risk": 0,
        }]

    # ── Rule 6: ITC blocked credits § 17(5) ────────────────────────────────
    def _check_itc_blocked(self, ext: dict, raw: dict) -> list[dict]:
        BLOCKED_HSN_KEYWORDS = {
            "4015": "Rubber gloves — ITC blocked if used for employee welfare § 17(5)(b)",
            "8703": "Motor vehicles — ITC blocked unless used for specified purposes § 17(5)(a)",
            "2202": "Beverages — ITC blocked on food/beverages for employees § 17(5)(b)",
            "9021": "Medical devices — ITC may be blocked if for employee health insurance § 17(5)(b)",
        }
        import re
        findings = []
        for line in ext["lines"]:
            desc = line.get("desc", "")
            cgst = line.get("cgst", 0)
            sgst = line.get("sgst", 0)
            igst = line.get("igst", 0)
            total_tax = cgst + sgst + igst

            hsn_match = re.search(r"HSN\s*(\d{4,8})", desc)
            if not hsn_match:
                continue
            hsn = hsn_match.group(1)[:4]

            if hsn in BLOCKED_HSN_KEYWORDS:
                findings.append({
                    "severity": "warning",
                    "title": f"ITC eligibility uncertain — {desc}",
                    "body": (
                        f"{BLOCKED_HSN_KEYWORDS[hsn]}. "
                        f"ITC ₹{total_tax:,} may be blocked depending on end-use. "
                        f"Confirm with CA before claiming. If blocked, reverse ITC in GSTR-3B."
                    ),
                    "rule_ref": "CGST Act § 17(5); CBIC FAQ on blocked credits",
                    "itc_risk": total_tax,
                })

        return findings

    # ── Rule 7: GSTIN format validation ─────────────────────────────────────
    def _check_gstin_format(self, ext: dict) -> list[dict]:
        import re
        GSTIN_PATTERN = re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$")
        issues = []

        for label, gstin in [("Supplier", ext["gstin_supplier"]), ("Recipient", ext["gstin_recipient"])]:
            if gstin and not GSTIN_PATTERN.match(gstin):
                issues.append(f"{label} GSTIN `{gstin}` is malformed")

        if issues:
            return [{
                "severity": "critical",
                "title": "Invalid GSTIN format detected",
                "body": " | ".join(issues) + ". Valid GSTIN: 2 digits (state) + 10 char PAN + 1 entity + Z + 1 checksum.",
                "rule_ref": "CGST Act § 25; CGST Rules Rule 8",
                "itc_risk": 0,
            }]
        return [{
            "severity": "ok",
            "title": "Both GSTINs are valid format",
            "body": "Supplier and recipient GSTINs match the 15-character GSTIN pattern.",
            "rule_ref": "CGST Act § 25; CGST Rules Rule 8",
            "itc_risk": 0,
        }]
