"""
Sample invoices for demo — 3 real-world GST scenarios.
These are the exact invoices shown in the live demo tab.
"""

SAMPLE_INVOICES = [
    {
        "label": "Textile export · 2 critical errors",
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
                "error": "WRONG_TAX_TYPE",
            },
            {
                "desc": "Synthetic Yarn (HSN 5402)",
                "qty": 50, "rate": 800, "taxable": 40000,
                "gst_rate": 12, "cgst": 0, "sgst": 0, "igst": 4800,
                "error": "WRONG_GST_RATE",
            },
            {
                "desc": "Embroidery Thread (HSN 5604)",
                "qty": 100, "rate": 120, "taxable": 12000,
                "gst_rate": 12, "cgst": 0, "sgst": 0, "igst": 1440,
                "error": None,
            },
        ],
    },
    {
        "label": "Pharma distributor · 1 warning",
        "supplier": "Riddhi Pharma Distributors",
        "invoice_no": "RPD/24-25/0334",
        "date": "3 Nov 2024",
        "gstin_supplier": "24AAECP8765Q1Z1",
        "gstin_recipient": "24BBFCD4321S1Z9",
        "pos": "Gujarat (24)",
        "supply_type": "B2B — Intra-state",
        "lines": [
            {
                "desc": "Paracetamol 500mg (HSN 3004)",
                "qty": 500, "rate": 12, "taxable": 6000,
                "gst_rate": 12, "cgst": 360, "sgst": 360, "igst": 0,
                "error": None,
            },
            {
                "desc": "Surgical Gloves (HSN 4015)",
                "qty": 200, "rate": 45, "taxable": 9000,
                "gst_rate": 12, "cgst": 540, "sgst": 540, "igst": 0,
                "error": "ITC_BLOCKED",
            },
            {
                "desc": "Antacid Syrup (HSN 3004)",
                "qty": 300, "rate": 30, "taxable": 9000,
                "gst_rate": 12, "cgst": 540, "sgst": 540, "igst": 0,
                "error": None,
            },
        ],
    },
    {
        "label": "Clean invoice · 0 errors",
        "supplier": "Shreeji Trading Co.",
        "invoice_no": "STC/2024-25/0091",
        "date": "18 Nov 2024",
        "gstin_supplier": "24AADFS3456K1Z7",
        "gstin_recipient": "24PQRST7890L1Z3",
        "pos": "Gujarat (24)",
        "supply_type": "B2B — Intra-state",
        "lines": [
            {
                "desc": "Stainless Steel Utensils (HSN 7323)",
                "qty": 100, "rate": 250, "taxable": 25000,
                "gst_rate": 12, "cgst": 1500, "sgst": 1500, "igst": 0,
                "error": None,
            },
            {
                "desc": "Plastic Storage Boxes (HSN 3926)",
                "qty": 50, "rate": 180, "taxable": 9000,
                "gst_rate": 18, "cgst": 810, "sgst": 810, "igst": 0,
                "error": None,
            },
        ],
    },
]
