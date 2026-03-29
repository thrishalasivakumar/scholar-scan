import streamlit as st

from backend import EMBED_MODEL_NAME, QA_MODEL_NAME, SUMM_MODEL_NAME
from utils.ui_components import info_card, inject_global_style, section_title, top_brand_banner


inject_global_style()

top_brand_banner("Technical details for project evaluation and review")
st.header("About ScholarScan")

section_title("Pipeline")
st.markdown(
    """
**1.** PDF text is extracted and cleaned.

**2.** Content is split into chunks and embedded using Sentence Transformers.

**3.** Query-to-chunk semantic similarity retrieves the most relevant context.

**4.** BART generates an abstractive summary.

**5.** DistilBERT answers free-form questions via extractive QA over the
most relevant chunks from the paper, with confidence scoring.

**6.** Key points are extracted and surfaced for quick review.
    """
)

section_title("Models")
info_card(
    title="Embedding model",
    body=EMBED_MODEL_NAME,
    tone="neutral"
)
info_card(
    title="Summarization model",
    body=SUMM_MODEL_NAME,
    tone="neutral"
)
info_card(
    title="Question answering model",
    body=QA_MODEL_NAME,
    tone="neutral"
)

section_title("Current Limitations")
st.markdown(
    """
- ⏳ In-memory indexing is session scoped and not persistent across restarts.
- 📄 Very large PDFs can increase latency and memory use.
- 🔎 Summaries are generated from top semantic chunks and may miss low-similarity sections.
- 📋 Output quality depends on paper formatting and OCR quality in source PDFs.
    """
)
