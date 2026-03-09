# -*- coding: utf-8 -*-
"""
core/lexicons.py
Lexical resources and ontology mappings for ESG ABSA Framework.
Includes aspect keywords, tone markers, sentiment indicators,
and canonical ontology paths.
"""

import regex as re

# ==========================================================
# ESG ASPECT LEXICON
# ==========================================================

ASPECT_LEX = {
    # Economic / Operational
    "Supply Chain": [r"rantai pasok", r"supply chain", r"disrupsi", r"logistik"],
    "Integrated Supply Chain": [r"terintegrasi", r"integrated system"],
    "Operational Efficiency": [
        r"efisiensi operasional", r"efisiensi", r"otomatisasi",
        r"digitalisasi", r"productivity", r"automation"
    ],
    "Capacity Expansion": [r"kapasitas produksi", r"kapasitas", r"expanding", r"new facility"],
    "Value Chain": [r"rantai nilai", r"value chain"],
    "Food Security": [r"ketahanan pangan", r"food security", r"protein"],
    "Rural Economy": [r"ekonomi pedesaan", r"rural economy"],
    "Self-sufficiency": [r"kemandirian", r"self-sufficien", r"local sourcing"],

    # Social
    "Local Partnership": [r"petani lokal", r"kemitraan", r"mitra", r"partnership"],
    "Community Welfare": [r"masyarakat", r"community", r"csr", r"kesejahteraan"],
    "Education Support": [r"pendidikan", r"education", r"literasi"],
    "Worker Safety": [r"lingkungan kerja", r"workplace", r"safety", r"pekerja"],

    # Environmental
    "Energy Efficiency": [r"energi", r"efisiensi energi", r"renewable"],
    "Environmental Preservation": [r"lingkungan", r"preservation", r"biodiversity"],
    "Emission Reduction": [r"emisi", r"gas rumah kaca", r"carbon", r"net zero"],

    # Governance
    "Governance/Transparency": [r"transparansi", r"whistleblowing", r"tata kelola", r"ethics"],
    "Compliance": [r"aturan", r"regulasi", r"compliance", r"policy", r"standar"],
    "Sustainability Strategy": [r"strategi keberlanjutan", r"sustainability strategy"],

    # General fallback
    "General": [r"keberlanjutan", r"sustainability", r"strategi", r"program"]
}


# ==========================================================
# CANONICAL ONTOLOGY PATHS
# ==========================================================

CANON_PATHS = {
    "Supply Chain": "Economic → Operational → Supply Chain",
    "Integrated Supply Chain": "Economic → Operational → Integrated Supply Chain",
    "Operational Efficiency": "Economic → Operational → Efficiency",
    "Capacity Expansion": "Economic → Operational → Capacity Expansion",
    "Value Chain": "Economic → Operational → Value Chain",
    "Food Security": "Economic → Food Security",
    "Rural Economy": "Economic → Community → Rural Economy",
    "Self-sufficiency": "Economic → Operational → Integrated Supply Chain",
    "Local Partnership": "Social → Partnership",
    "Community Welfare": "Social → Welfare",
    "Education Support": "Social → Education",
    "Worker Safety": "Social → Worker Safety",
    "Energy Efficiency": "Environmental → Energy Efficiency",
    "Environmental Preservation": "Environmental → Preservation",
    "Emission Reduction": "Environmental → Emission Reduction",
    "Governance/Transparency": "Governance → Transparency",
    "Compliance": "Governance → Compliance",
    "Sustainability Strategy": "Governance → Strategy",
    "General": "General → Misc"
}


# ==========================================================
# SENTIMENT POLARITY KEYWORDS
# ==========================================================

POS_WORDS = [
    r"meningkat", r"berkurang", r"memastikan", r"mampu", r"positif",
    r"improve", r"strengthen", r"boost", r"enhanc", r"achiev",
    r"empower", r"support", r"expand", r"sustain", r"berhasil"
]

NEG_WORDS = [
    r"tantangan", r"gejolak", r"krisis", r"disrupsi", r"turun", r"penurunan",
    r"decline", r"problem", r"constraint", r"slow", r"shortage", r"risiko", r"obstacle"
]


# ==========================================================
# TONE MARKERS
# ==========================================================

COMMITMENT_MARK = [
    r"berkomitmen", r"commitment", r"kami yakin",
    r"will", r"menargetkan", r"target", r"aim to", r"dedicated to"
]

ACTION_MARK = [
    r"melakukan", r"mengadopsi", r"menerapkan", r"implement",
    r"adopt", r"launch", r"conduct", r"initiated"
]

OUTCOME_MARK = [
    r"telah", r"achieved", r"has been", r"successfully",
    r"resulted in", r"delivered", r"obtained", r"tercapai", r"mencapai"
]


# ==========================================================
# HELPER: MATCH FUNCTION
# ==========================================================

def any_match(patterns, text: str) -> bool:
    """Returns True if any regex pattern matches the given text."""
    return any(re.search(p, text.lower()) for p in patterns)
