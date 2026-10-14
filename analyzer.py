
"""NLP-assisted contract analyzer.
Educational screening only; not legal advice.
"""
import re
from collections import Counter
from io import BytesIO

import spacy

try:
    NLP = spacy.load("en_core_web_sm")
except (OSError, ImportError):
    NLP = spacy.blank("en")

RISK_PATTERNS = {
    "Automatic renewal": [
        r"automatically renew", r"automatic renewal", r"renewal term"
    ],
    "Termination restrictions": [
        r"may not terminate", r"non-cancellable", r"irrevocabl\w*",
        r"without the right to terminate"
    ],
    "Broad liability / indemnity": [
        r"unlimited liability", r"indemnify and hold harmless",
        r"any and all claims", r"consequential damages"
    ],
    "Unilateral changes": [
        r"sole discretion", r"without prior notice",
        r"may modify.{0,80}at any time"
    ],
    "Confidentiality obligations": [
        r"confidential information", r"non-disclosure",
        r"keep.{0,50}confidential"
    ],
    "Payment penalties": [
        r"late fee", r"penalty", r"interest at the rate of",
        r"non-refundable"
    ],
}

CLAUSE_PATTERNS = {
    "Termination": [
        r"termination", r"terminate this agreement", r"notice period"
    ],
    "Confidentiality": [r"confidential", r"non-disclosure"],
    "Indemnification": [r"indemnif\w*", r"hold harmless"],
    "Limitation of liability": [
        r"limitation of liability", r"limited liability",
        r"consequential damages"
    ],
    "Governing law / jurisdiction": [
        r"governing law", r"jurisdiction", r"venue shall"
    ],
    "Renewal": [r"renewal", r"automatically renew", r"renewal term"],
    "Payment": [r"payment terms", r"invoice", r"late fee", r"purchase price"],
}

RISK_WEIGHTS = {
    "Automatic renewal": 12,
    "Termination restrictions": 20,
    "Broad liability / indemnity": 20,
    "Unilateral changes": 20,
    "Confidentiality obligations": 12,
    "Payment penalties": 12,
}


def extract_text_from_upload(uploaded_file):
    name = uploaded_file.name.lower()
    data = uploaded_file.getvalue()

    if name.endswith(".txt"):
        return data.decode("utf-8", errors="replace")

    if name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(data))
        return "\n".join(
            page.extract_text() or "" for page in reader.pages
        )

    if name.endswith(".docx"):
        from docx import Document
        document = Document(BytesIO(data))
        return "\n".join(p.text for p in document.paragraphs)

    raise ValueError("Unsupported file type")


def _matching_sentences(text, patterns):
    """Find distinct sentences containing configured risk or clause phrases."""
    doc = NLP(text)
    sentences = (
        [sent.text.strip() for sent in doc.sents]
        if NLP.has_pipe("parser") or NLP.has_pipe("senter")
        else re.split(r"(?<=[.!?;])\s+|\n+", text)
    )

    matches = []
    for sentence in sentences:
        clean = " ".join(sentence.split())
        if clean and any(
            re.search(pattern, clean, re.IGNORECASE)
            for pattern in patterns
        ):
            if clean not in matches:
                matches.append(clean[:500])

    return matches[:5]


def extract_entities(text):
    # spaCy provides general named-entity recognition, not legal validation.
    doc = NLP(text)

    dates = re.findall(
        r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{1,2},?\s+\d{4})\b",
        text, re.I
    )
    money = re.findall(r"(?:\$|₹|€|£)\s?\d[\d,]*(?:\.\d{2})?", text)
    emails = re.findall(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.I
    )

    organizations = list(dict.fromkeys(
        ent.text for ent in doc.ents if ent.label_ == "ORG"
    ))
    people = list(dict.fromkeys(
        ent.text for ent in doc.ents if ent.label_ == "PERSON"
    ))

    return {
        "dates": list(dict.fromkeys(dates))[:20],
        "monetary_values": list(dict.fromkeys(money))[:20],
        "emails": list(dict.fromkeys(emails))[:20],
        "organizations": organizations[:20],
        "people": people[:20],
    }


def analyze_contract(text):
    risk_flags = []

    for category, patterns in RISK_PATTERNS.items():
        evidence = _matching_sentences(text, patterns)
        if evidence:
            risk_flags.append({
                "category": category,
                "reason": (
                    "Review this wording and its surrounding context "
                    f"({len(evidence)} matching passage(s))."
                ),
                "evidence": evidence[0],
                "weight": RISK_WEIGHTS[category],
                "matching_passages": evidence,
            })

    # Keep the original scoring approach for compatibility.
    score = min(100, sum(flag["weight"] for flag in risk_flags))
    level = "High" if score >= 60 else "Medium" if score >= 25 else "Low"

    clauses = []
    for category, patterns in CLAUSE_PATTERNS.items():
        evidence = _matching_sentences(text, patterns)
        if evidence:
            clauses.append({
                "category": category,
                "matches": len(evidence),
                "evidence": "\n\n".join(evidence),
            })

    doc = NLP(text)
    keywords = [
        token.lemma_.lower()
        for token in doc
        if token.is_alpha
        and not token.is_stop
        and len(token.text) > 2
    ]
    frequent_terms = [
        {"term": word, "count": count}
        for word, count in Counter(keywords).most_common(10)
    ]

    return {
        "risk_score": score,
        "risk_level": level,
        "word_count": len(text.split()),
        "risk_flags": risk_flags,
        "clauses": clauses,
        "entities": extract_entities(text),
        "nlp_summary": {
            "model": (
                "en_core_web_sm"
                if NLP.meta.get("name") == "core_web_sm"
                else "spaCy blank fallback"
            ),
            "named_entities": [
                {"text": ent.text, "type": ent.label_}
                for ent in doc.ents
            ][:50],
            "frequent_terms": frequent_terms,
        },
        "disclaimer": (
            "Rule-based educational screening with spaCy-assisted NLP; "
            "not legal advice. A qualified reviewer should assess the "
            "full contract."
        ),
    }
