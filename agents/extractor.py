"""
Agent 1 — Document Extractor
Simulates LlamaParse PDF extraction; for demo uses structured dict.
In production: swap extract() to call LlamaParse on uploaded PDF bytes.
"""

import re


# State codes for inter/intra-state detection
STATE_CODES = {
    "01": "Jammu & Kashmir", "02": "Himachal Pradesh", "03": "Punjab",
    "04": "Chandigarh", "05": "Uttarakhand", "06": "Haryana",
    "07": "Delhi", "08": "Rajasthan", "09": "Uttar Pradesh",
    "10": "Bihar", "11": "Sikkim", "12": "Arunachal Pradesh",
    "13": "Nagaland", "14": "Manipur", "15": "Mizoram",
    "16": "Tripura", "17": "Meghalaya", "18": "Assam",
    "19": "West Bengal", "20": "Jharkhand", "21": "Odisha",
    "22": "Chhattisgarh", "23": "Madhya Pradesh", "24": "Gujarat",
    "25": "Daman & Diu", "26": "Dadra & Nagar Haveli", "27": "Maharashtra",
    "28": "Andhra Pradesh", "29": "Karnataka", "30": "Goa",
    "31": "Lakshadweep", "32": "Kerala", "33": "Tamil Nadu",
    "34": "Puducherry", "35": "Andaman & Nicobar", "36": "Telangana",
    "37": "Andhra Pradesh (new)", "38": "Ladakh",
    "97": "Other Territory", "99": "Centre",
}


class DocumentExtractor:
    """
    Extracts and normalises invoice fields.
    In production: replace _parse_from_dict() with LlamaParse PDF call.
    """

    def extract(self, invoice_dict: dict) -> dict:
        """Main entry point. Returns normalised extraction result."""
        return self._parse_from_dict(invoice_dict)

    def _parse_from_dict(self, inv: dict) -> dict:
        gstin_s = inv.get("gstin_supplier", "")
        gstin_r = inv.get("gstin_recipient", "")
        pos_raw = inv.get("pos", "")

        supplier_state_code = gstin_s[:2] if len(gstin_s) >= 2 else "00"
        pos_state_code = self._extract_pos_code(pos_raw)

        is_inter_state = (supplier_state_code != pos_state_code)

        total_taxable = sum(l["taxable"] for l in inv.get("lines", []))
        total_cgst    = sum(l.get("cgst", 0) for l in inv.get("lines", []))
        total_sgst    = sum(l.get("sgst", 0) for l in inv.get("lines", []))
        total_igst    = sum(l.get("igst", 0) for l in inv.get("lines", []))
        total_value   = total_taxable + total_cgst + total_sgst + total_igst

        hsn_codes = []
        for line in inv.get("lines", []):
            desc = line.get("desc", "")
            hsn_match = re.search(r"HSN\s*(\d{4,8})", desc)
            if hsn_match:
                hsn_codes.append(hsn_match.group(1))

        return {
            "invoice_no":          inv.get("invoice_no", ""),
            "supplier":            inv.get("supplier", ""),
            "gstin_supplier":      gstin_s,
            "gstin_recipient":     gstin_r,
            "supplier_state_code": supplier_state_code,
            "supplier_state_name": STATE_CODES.get(supplier_state_code, supplier_state_code),
            "pos_state_code":      pos_state_code,
            "pos_state_name":      STATE_CODES.get(pos_state_code, pos_raw),
            "pos_raw":             pos_raw,
            "supplier_state":      supplier_state_code,
            "pos_state":           pos_state_code,
            "is_inter_state":      is_inter_state,
            "supply_type_resolved": "INTER_STATE" if is_inter_state else "INTRA_STATE",
            "lines":               inv.get("lines", []),
            "line_count":          len(inv.get("lines", [])),
            "hsn_codes":           hsn_codes,
            "total_taxable":       total_taxable,
            "total_cgst":          total_cgst,
            "total_sgst":          total_sgst,
            "total_igst":          total_igst,
            "total_value":         total_value,
            "supply_type_raw":     inv.get("supply_type", ""),
            "date":                inv.get("date", ""),
            "confidence":          0.96,
        }

    def _extract_pos_code(self, pos_raw: str) -> str:
        """Extract 2-digit state code from 'Maharashtra (27)' style string."""
        match = re.search(r"\((\d{2})\)", pos_raw)
        if match:
            return match.group(1)
        # Fallback: first 2 digits found
        digits = re.findall(r"\d+", pos_raw)
        return digits[0][:2] if digits else "00"

    # ── Production extension point ─────────────────────────────────────────
    def extract_from_pdf(self, pdf_bytes: bytes) -> dict:
        """
        Production: call LlamaParse to extract invoice fields from PDF.

        Usage:
            from llama_parse import LlamaParse
            parser = LlamaParse(api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
                                result_type="json")
            documents = parser.load_data_from_bytes(pdf_bytes, extra_info={"file_name": "invoice.pdf"})
            # then map documents[0] fields to the dict format above
        """
        raise NotImplementedError(
            "PDF extraction requires LlamaParse API key. "
            "Set LLAMA_CLOUD_API_KEY in .env and implement this method. "
            "See README.md § Production Setup."
        )
