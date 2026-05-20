"""
GST Rules knowledge base — 27 rules used by the rule checker.
In production these are embedded in ChromaDB for RAG retrieval.
HSN_RATE_TABLE: HSN code → correct GST rate (%) + source notification
"""

GST_RULES = [
    {
        "id": "R01",
        "category": "Supply type",
        "rule": "Inter-state supply (supplier state ≠ place of supply) must charge IGST only.",
        "section": "IGST Act § 5; CGST Act § 9",
    },
    {
        "id": "R02",
        "category": "Supply type",
        "rule": "Intra-state supply (supplier state = place of supply) must charge CGST + SGST.",
        "section": "CGST Act § 9; SGST Act § 9",
    },
    {
        "id": "R03",
        "category": "Supply type",
        "rule": "CGST rate = SGST rate. CGST + SGST = IGST for same taxable value.",
        "section": "CGST Act § 9",
    },
    {
        "id": "R04",
        "category": "HSN rate",
        "rule": "Every supply must be taxed at the rate notified for its HSN/SAC code.",
        "section": "CGST Rate Notification 1/2017",
    },
    {
        "id": "R05",
        "category": "ITC",
        "rule": "ITC blocked for motor vehicles (HSN 8703) unless used for specified transport/training purposes.",
        "section": "CGST Act § 17(5)(a)",
    },
    {
        "id": "R06",
        "category": "ITC",
        "rule": "ITC blocked for food/beverages, outdoor catering, beauty treatment, health services, cosmetics.",
        "section": "CGST Act § 17(5)(b)",
    },
    {
        "id": "R07",
        "category": "ITC",
        "rule": "ITC blocked for personal consumption goods and supplies exempt from tax.",
        "section": "CGST Act § 17(5)(g)(h)",
    },
    {
        "id": "R08",
        "category": "Invoice format",
        "rule": "Tax invoice must contain: supplier name+address+GSTIN, consignee GSTIN, invoice number, date, HSN/SAC, taxable value, tax rate, tax amount, place of supply.",
        "section": "CGST Rules Rule 46",
    },
    {
        "id": "R09",
        "category": "Invoice format",
        "rule": "Invoice number must be consecutive and unique per financial year.",
        "section": "CGST Rules Rule 46(b)",
    },
    {
        "id": "R10",
        "category": "E-way bill",
        "rule": "E-way bill mandatory when consignment value exceeds ₹50,000 for movement of goods.",
        "section": "CGST Rules Rule 138; Notification 15/2018-CT",
    },
    {
        "id": "R11",
        "category": "E-way bill",
        "rule": "E-way bill must be generated before movement of goods, not post-movement.",
        "section": "CGST Rules Rule 138(1)",
    },
    {
        "id": "R12",
        "category": "Time of supply",
        "rule": "Time of supply for goods = earlier of date of invoice or date of receipt of payment.",
        "section": "CGST Act § 12",
    },
    {
        "id": "R13",
        "category": "Time of supply",
        "rule": "Time of supply for services = date of invoice (if within 30 days of supply) or date of supply.",
        "section": "CGST Act § 13",
    },
    {
        "id": "R14",
        "category": "Reverse charge",
        "rule": "Specified services (legal, GTA, import of services, etc.) attract reverse charge — recipient pays GST.",
        "section": "CGST Act § 9(3); Notification 13/2017-CT(Rate)",
    },
    {
        "id": "R15",
        "category": "Reverse charge",
        "rule": "Purchases from unregistered persons may attract reverse charge under § 9(4).",
        "section": "CGST Act § 9(4)",
    },
    {
        "id": "R16",
        "category": "Credit note",
        "rule": "Credit note must be issued by supplier where tax is overcharged; linked to original invoice.",
        "section": "CGST Act § 34",
    },
    {
        "id": "R17",
        "category": "Credit note",
        "rule": "Credit note cannot be issued after September 30 following the financial year of original invoice.",
        "section": "CGST Act § 34(2)",
    },
    {
        "id": "R18",
        "category": "GSTIN",
        "rule": "GSTIN must be 15 characters: 2-digit state code + 10-char PAN + 1 entity number + Z + checksum.",
        "section": "CGST Act § 25; CGST Rules Rule 8",
    },
    {
        "id": "R19",
        "category": "Place of supply",
        "rule": "POS for B2B supply of goods = location of recipient.",
        "section": "IGST Act § 10(1)(b)",
    },
    {
        "id": "R20",
        "category": "Place of supply",
        "rule": "POS for B2C supply of goods = location where goods are delivered.",
        "section": "IGST Act § 10(1)(a)",
    },
    {
        "id": "R21",
        "category": "HSN disclosure",
        "rule": "Taxpayers with turnover > ₹5 Cr: 6-digit HSN on invoices. ₹1.5 Cr–5 Cr: 4-digit. Below ₹1.5 Cr: optional.",
        "section": "CGST Rules Rule 46(h); Notification 78/2020-CT",
    },
    {
        "id": "R22",
        "category": "Export",
        "rule": "Export of goods/services is zero-rated; IGST paid or LUT/bond for without-payment route.",
        "section": "IGST Act § 16",
    },
    {
        "id": "R23",
        "category": "Composition scheme",
        "rule": "Composition dealers cannot issue tax invoices; must issue bill of supply. No ITC for buyer.",
        "section": "CGST Act § 10; CGST Rules Rule 52",
    },
    {
        "id": "R24",
        "category": "ITC timing",
        "rule": "ITC can be claimed only if supplier has filed GSTR-1 and amount appears in GSTR-2B.",
        "section": "CGST Act § 16(2)(aa); Rule 36(4)",
    },
    {
        "id": "R25",
        "category": "ITC timing",
        "rule": "ITC cannot be claimed if invoice is more than 2 years old (FY + 1 year).",
        "section": "CGST Act § 16(4)",
    },
    {
        "id": "R26",
        "category": "Nil/Exempt supply",
        "rule": "No ITC available on inputs used exclusively for exempt supplies.",
        "section": "CGST Act § 17(2)",
    },
    {
        "id": "R27",
        "category": "Tax arithmetic",
        "rule": "Total tax = taxable value × GST rate / 100. CGST = SGST = GST rate / 2 for intra-state.",
        "section": "CGST Act § 9; Mathematical verification",
    },
]


# HSN code → {rate (%), name, notification}
HSN_RATE_TABLE = {
    # Textiles
    "5208": {"rate": 5,  "name": "Cotton Fabric",        "notification": "CGST Rate Notif. 1/2017 S.No. 227"},
    "5402": {"rate": 5,  "name": "Synthetic Filament Yarn", "notification": "CGST Rate Notif. 1/2017 S.No. 218"},
    "5604": {"rate": 12, "name": "Rubber/Plastic Thread & Cord", "notification": "CGST Rate Notif. 1/2017 S.No. 148"},
    "5209": {"rate": 5,  "name": "Woven Cotton Fabric >200g/m2", "notification": "CGST Rate Notif. 1/2017 S.No. 228"},
    "5512": {"rate": 5,  "name": "Synthetic Woven Fabric", "notification": "CGST Rate Notif. 1/2017 S.No. 232"},

    # Pharma
    "3004": {"rate": 12, "name": "Medicines/Formulations", "notification": "CGST Rate Notif. 1/2017 S.No. 68"},
    "3002": {"rate": 5,  "name": "Vaccines",               "notification": "CGST Rate Notif. 1/2017 S.No. 65"},
    "3006": {"rate": 12, "name": "Pharmaceutical goods",   "notification": "CGST Rate Notif. 1/2017 S.No. 71"},

    # Rubber/plastic
    "4015": {"rate": 12, "name": "Rubber Gloves",          "notification": "CGST Rate Notif. 1/2017 S.No. 116"},
    "3926": {"rate": 18, "name": "Plastic Articles (other)", "notification": "CGST Rate Notif. 1/2017 S.No. 108"},

    # Metal/hardware
    "7323": {"rate": 12, "name": "Stainless Steel Utensils", "notification": "CGST Rate Notif. 1/2017 S.No. 194"},
    "7308": {"rate": 18, "name": "Steel Structures",         "notification": "CGST Rate Notif. 1/2017 S.No. 190"},

    # Electronics
    "8471": {"rate": 18, "name": "Computers/Laptops",       "notification": "CGST Rate Notif. 1/2017 S.No. 370"},
    "8517": {"rate": 18, "name": "Telephones/Smartphones",  "notification": "CGST Rate Notif. 1/2017 S.No. 374"},

    # Food
    "1902": {"rate": 18, "name": "Pasta/Noodles (branded)", "notification": "CGST Rate Notif. 1/2017 S.No. 19"},
    "2202": {"rate": 18, "name": "Aerated/sweetened water", "notification": "CGST Rate Notif. 1/2017 S.No. 52"},
}
