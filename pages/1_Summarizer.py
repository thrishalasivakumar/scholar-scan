import tempfile
from datetime import datetime
from pathlib import Path

import streamlit as st

from backend import answer_question, build_download_payload, ingest_pdf, smart_summarize
from utils.state import get_models, initialize_state
from utils.ui_components import (
    info_card,
    inject_global_style,
    key_point_card,
    metric_chip,
    section_title,
    top_brand_banner,
)
from utils.validators import validate_query, validate_uploaded_pdf


inject_global_style()
initialize_state()

top_brand_banner("Upload a paper, specify evaluation focus, and generate concise insights")
st.header("Summarizer")

with st.sidebar:
    st.markdown("### 🧭 ScholarScan Workflow")
    st.markdown("**1.** Upload a PDF")
    st.markdown("**2.** Add focus query")
    st.markdown("**3.** Generate summary")
    st.markdown("**4.** Export result")

control_col, status_col = st.columns([2.1, 1], gap="large")

with control_col:
    section_title("Input")

    query = st.text_input(
        "Summary focus",
        value="What is the main objective and conclusion of this paper?",
        help="Use an evaluator-style query such as methodology, novelty, results, or limitations."
    )

    summary_length = st.select_slider(
        "Summary length",
        options=["short", "medium", "long"],
        value="medium"
    )

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    generate_clicked = st.button("🚀 Generate Summary")

with status_col:
    section_title("Session")
    metric_chip("Length", summary_length.title())
    metric_chip("File limit", "50 MB")

    info_card(
        title="Tip",
        body=(
            "Ask one focused question at a time for stronger summaries, then run additional "
            "queries to evaluate separate dimensions."
        ),
        tone="success"
    )

if generate_clicked:
    if uploaded_file is None:
        st.error("Please upload a PDF before generating a summary.")
    else:
        file_error = validate_uploaded_pdf(uploaded_file.name, uploaded_file.size)
        query_error = validate_query(query)

        if file_error:
            st.error(file_error)
        elif query_error:
            st.error(query_error)
        else:
            embed_model, tokenizer, model, _qa_assets = get_models()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                pdf_path = tmp.name

            st.session_state["source_pdf_name"] = Path(uploaded_file.name).stem

            with st.spinner("Building semantic index and generating summary..."):
                ingest_pdf(pdf_path, "uploaded_paper", embed_model)
                st.session_state["indexed_paper_name"] = uploaded_file.name
                summary = smart_summarize(
                    query=query,
                    embed_model=embed_model,
                    tokenizer=tokenizer,
                    model=model,
                    summary_length=summary_length,
                )
                st.session_state["summary_data"] = summary

            st.success("Summary generated successfully.")

section_title("Ask Questions About This Paper")
question_text = st.text_input(
    "Question for DistilBERT QA",
    placeholder="Example: What dataset did the authors evaluate on?"
)
qa_clicked = st.button("Ask ScholarScan QA")

if qa_clicked:
    if not question_text.strip():
        st.error("Please enter a question before running QA.")
    elif uploaded_file is None:
        st.error("Please upload a PDF so ScholarScan QA can read the paper.")
    else:
        try:
            embed_model, _tokenizer, _model, qa_assets = get_models()

            if st.session_state.get("indexed_paper_name") != uploaded_file.name:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    pdf_path = tmp.name

                with st.spinner("Indexing submitted paper for question answering..."):
                    ingest_pdf(pdf_path, "uploaded_paper", embed_model)
                    st.session_state["indexed_paper_name"] = uploaded_file.name

            qa_result = answer_question(
                question=question_text,
                embed_model=embed_model,
                qa_assets=qa_assets,
                top_k=4,
            )
            st.session_state["qa_response"] = qa_result
        except ValueError as qa_error:
            st.error(str(qa_error))
        except Exception as qa_error:
            st.error(f"Unable to answer question: {qa_error}")

qa_payload = st.session_state.get("qa_response")
if qa_payload:
    answer_text = qa_payload.get("answer", "").strip()
    confidence = qa_payload.get("confidence", 0.0)
    has_answer = qa_payload.get("has_answer", False)

    if has_answer and answer_text:
        info_card(
            title="DistilBERT Answer",
            body=answer_text,
            tone="neutral"
        )
        st.caption(f"Confidence: {confidence:.2%}")
    else:
        st.info("The QA model could not find a confident answer in the indexed context.")

summary_payload = st.session_state.get("summary_data")

if summary_payload:
    section_title("Generated Summary")
    summary_text = summary_payload.get("summary", "")
    key_points = summary_payload.get("key_points", [])

    st.markdown(summary_text)

    section_title("Key Points")
    if key_points:
        for idx, point in enumerate(key_points, start=1):
            key_point_card(idx, point)
    else:
        st.info("No key points could be extracted from this generation.")

    section_title("Export")

    format_options = {
        "TXT (.txt)": "txt",
        "Word (.docx)": "word",
        "PDF (.pdf)": "pdf",
    }

    selected_label = st.selectbox("Choose format", list(format_options.keys()))
    selected_format = format_options[selected_label]

    try:
        file_data, mime_type, extension = build_download_payload(
            summary_text,
            key_points,
            selected_format,
        )

        safe_name = st.session_state.get("source_pdf_name", "paper")
        stamp = datetime.now().strftime("%Y%m%d_%H%M")

        st.download_button(
            label=f"⬇ Download as {selected_label}",
            data=file_data,
            file_name=f"{safe_name}_summary_{stamp}.{extension}",
            mime=mime_type,
        )
    except Exception as export_error:
        st.error(f"Unable to generate the selected file format: {export_error}")
