# AI-Powered Contract Intelligence & Risk Scoring

## Overview
A Python-based application that analyzes contract documents, identifies important clauses, extracts basic entities, and flags potentially risky wording for human review.

## Features
- Upload PDF, DOCX, and TXT contracts.
- Extract contract text.
- Detect potential risks using configurable phrase-matching rules.
- Identify important clauses such as termination, renewal, payment, and confidentiality.
- Extract dates, monetary values, and email addresses.
- Use spaCy NLP for named-entity recognition and frequent-term analysis.
- Display a risk score and risk level.
- Export analysis results as JSON.

## Technologies
- Python
- Streamlit
- spaCy and English language model
- PyPDF
- python-docx
- pytest

## Installation and Execution
1. Install Python and Git.
2. Open the project folder in the terminal.
3. Create a virtual environment:

   `py -m venv .venv`

4. Activate it:

   `.\.venv\Scripts\Activate.ps1`

5. Install dependencies:

   `pip install -r requirements.txt`

6. Install spaCy and its English model if needed:

   `pip install spacy`

   `python -m spacy download en_core_web_sm`

7. Run the application:

   `python -m streamlit run app.py`

8. Open the local URL shown in the terminal.

## Testing
Run `python -m pytest -q`.

## Limitations
Risk detection uses transparent rule-based patterns and is not a trained legal risk model. Results are for educational screening only and are not legal advice. Scanned PDFs may require OCR.

## Future Scope
- Train and evaluate a contract-clause classification model.
- Add OCR for scanned contracts.
- Improve legal entity extraction.
- Add clause-level explanations and comparison.
- Evaluate precision, recall, and F1-score on an appropriately licensed dataset.
- Add a FastAPI backend and secure document handling.
