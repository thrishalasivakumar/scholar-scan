import streamlit as st

from utils.state import get_models, initialize_state, set_page_config
from utils.ui_components import (
    info_card,
    inject_global_style,
    metric_chip,
    section_title,
    top_brand_banner,
)


set_page_config()
inject_global_style()
initialize_state()


top_brand_banner("AI powered Research Paper Summarizer")

left_col, right_col = st.columns([1.5, 1], gap="large")

with left_col:
    section_title("Why This Application")
    st.markdown(
        """
        This project helps evaluators quickly assess long research papers by:

        - 🔍 Retrieving context that matches a focused evaluation query
        - 📝 Generating concise and readable summaries with transformer models
        - 💬 Answering natural-language questions about the paper using DistilBERT
        - 📊 Presenting key points and downloadable outputs in multiple formats
        """
    )

    section_title("Navigation")
    st.info(
        "Open the **Summarizer** page to upload a PDF and generate summaries. "
        "Use the **Ask Paper** page to chat with your paper and get instant answers. "
        "Visit **About** for model and architecture details."
    )

with right_col:
    info_card(
        title="Model Stack",
        body=(
            "Sentence embeddings for semantic retrieval, BART for abstractive "
            "summarization, and DistilBERT for extractive question answering."
        ),
        tone="neutral"
    )
    metric_chip("Input", "PDF research paper")
    metric_chip("Output", "Summary + key points")
    metric_chip("Exports", "TXT · DOCX · PDF")


with st.spinner("Preparing model resources for this session..."):
    get_models()

st.success("Application is ready. Move to the Summarizer page to begin.")