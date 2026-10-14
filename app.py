import streamlit as st
from analyzer import analyze_contract, extract_text_from_upload

st.set_page_config(page_title="Contract Intelligence", page_icon="📄", layout="wide")
st.title("📄 AI-Powered Contract Intelligence & Risk Scoring")
st.caption("Starter MVP • NLP-assisted contract review • Not legal advice")
st.write("Upload a contract to extract key clauses, identify basic entities, and flag wording that may deserve human review.")

uploaded = st.file_uploader("Upload a contract", type=["pdf", "txt", "docx"])
if uploaded:
    try:
        text = extract_text_from_upload(uploaded)
        if not text.strip():
            st.error("No readable text was found. If this is a scanned PDF, OCR support will be added in a later step.")
        else:
            with st.expander("Extracted contract text"):
                st.text_area("Text", text, height=220, label_visibility="collapsed")
            if st.button("Analyze contract", type="primary"):
                result = analyze_contract(text)
                left, middle, right = st.columns(3)
                left.metric("Risk score", f"{result['risk_score']}/100")
                middle.metric("Risk level", result["risk_level"])
                right.metric("Words analyzed", result["word_count"])
                st.subheader("Potential risk flags")
                if result["risk_flags"]:
                    for flag in result["risk_flags"]:
                        st.warning(f"**{flag['category']}** — {flag['reason']}\n\nEvidence: “{flag['evidence']}”")
                else:
                    st.success("No configured risk phrases were detected. This does not guarantee that the contract is safe.")
                st.subheader("Important clauses")
                if result["clauses"]:
                    for clause in result["clauses"]:
                        with st.expander(f"{clause['category']} ({clause['matches']} match(es))"):
                            st.write(clause["evidence"])
                else:
                    st.info("No configured clause headings or phrases were found.")
                
                st.subheader("Basic entities")
                st.json(result["entities"])

                # NEW: NLP insights
                st.subheader("NLP Insights")

                summary = result.get("nlp_summary", {})
                st.caption(
                    f"Language model: {summary.get('model', 'N/A')}"
                )

                entities = summary.get("named_entities", [])
                if entities:
                    st.write("**Named Entities Identified**")
                    st.dataframe(
                        entities,
                        use_container_width=True
                    )
                else:
                    st.info("No named entities were identified.")

                terms = summary.get("frequent_terms", [])
                if terms:
                    st.write("**Frequent Contract Terms**")
                    st.dataframe(
                        terms,
                        use_container_width=True
                    )

                # Download analysis report
                st.download_button(
                    "Download analysis as JSON",
                    data=__import__("json").dumps(
                        result, indent=2
                    ),
                    file_name="contract_analysis.json",
                    mime="application/json"
                )

    except Exception as exc:
        st.error(f"Could not process this file: {exc}")
else:
    st.info("Start with the included sample_contract.txt or upload a PDF, DOCX, or TXT file.")
