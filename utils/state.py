from typing import Any, Tuple

import streamlit as st

from backend import load_models


def set_page_config() -> None:
    st.set_page_config(
        page_title="ScholarScan",
        layout="wide",
        initial_sidebar_state="expanded"
    )


@st.cache_resource(show_spinner=False)
def get_models() -> Tuple[Any, Any, Any, Any]:
    return load_models()


def initialize_state() -> None:
    if "summary_data" not in st.session_state:
        st.session_state["summary_data"] = None
    if "source_pdf_name" not in st.session_state:
        st.session_state["source_pdf_name"] = "paper"
    if "indexed_paper_name" not in st.session_state:
        st.session_state["indexed_paper_name"] = None
    if "qa_response" not in st.session_state:
        st.session_state["qa_response"] = None
    if "qa_chat_history" not in st.session_state:
        st.session_state["qa_chat_history"] = []
    if "qa_paper_uploaded" not in st.session_state:
        st.session_state["qa_paper_uploaded"] = False
