import tempfile
from datetime import datetime

import streamlit as st

from backend import answer_question, ingest_pdf
from utils.state import get_models, initialize_state
from utils.ui_components import (
    inject_global_style,
    section_title,
    top_brand_banner,
)
from utils.validators import validate_uploaded_pdf


inject_global_style()
initialize_state()

# ------------------------------------------------------------------
# Page-level session defaults
# ------------------------------------------------------------------
if "qa_chat_history" not in st.session_state:
    st.session_state["qa_chat_history"] = []
if "qa_paper_uploaded" not in st.session_state:
    st.session_state["qa_paper_uploaded"] = False

# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------
top_brand_banner("Ask questions about your research paper and get instant answers")
st.header("📖 Ask Your Paper")

# ------------------------------------------------------------------
# Sidebar — workflow + suggested questions
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🧠 Paper Q&A Guide")
    st.markdown("**1.** Upload a PDF below")
    st.markdown("**2.** Type any question")
    st.markdown("**3.** Get DistilBERT answers")
    st.markdown("---")
    st.markdown("#### 💡 Try asking")
    sample_questions = [
        "What is the main contribution of this paper?",
        "What datasets were used in the experiments?",
        "What is the proposed methodology?",
        "What are the limitations mentioned?",
        "What were the key results?",
        "Who are the authors of this paper?",
    ]
    for sq in sample_questions:
        st.markdown(f"- *{sq}*")

# ------------------------------------------------------------------
# Inject chat-specific CSS
# ------------------------------------------------------------------
st.markdown("""
<style>
/* ---------- Chat Container ---------- */
.qa-chat-container {
    max-height: 520px;
    overflow-y: auto;
    padding: 1rem 0.5rem;
    margin-bottom: 1rem;
}

/* ---------- Chat Message Bubble ---------- */
.chat-message {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 1rem;
    animation: fadeInUp 0.35s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.chat-message.user-msg {
    flex-direction: row-reverse;
}

.chat-avatar {
    width: 2.4rem;
    height: 2.4rem;
    min-width: 2.4rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    font-weight: 700;
    flex-shrink: 0;
}

.chat-avatar.user-avatar {
    background: linear-gradient(135deg, #5b4cdb, #a29bfe);
    color: rgba(255, 255, 255, 0.85);
}

.chat-avatar.bot-avatar {
    background: linear-gradient(135deg, #00b894, #55efc4);
    color: rgba(255, 255, 255, 0.85);
}

.chat-bubble {
    max-width: 78%;
    padding: 0.9rem 1.15rem;
    border-radius: 16px;
    font-size: 0.94rem;
    line-height: 1.65;
    position: relative;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.chat-bubble.user-bubble {
    background: linear-gradient(135deg, #5b4cdb 0%, #6c5ce7 100%);
    color: rgba(255, 255, 255, 0.85) !important;
    border-bottom-right-radius: 4px;
}

.chat-bubble.user-bubble p,
.chat-bubble.user-bubble .answer-text,
.chat-bubble.user-bubble span {
    color: rgba(255, 255, 255, 0.85) !important;
}

.chat-bubble.bot-bubble {
    background: #ffffff;
    color: #1a1a2e;
    border: 1px solid rgba(0,0,0,0.07);
    border-bottom-left-radius: 4px;
}

.chat-bubble .answer-text {
    margin: 0;
    font-weight: 500;
}

/* ---------- Confidence Meter ---------- */
.confidence-row {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-top: 0.65rem;
    padding-top: 0.55rem;
    border-top: 1px solid rgba(0,0,0,0.06);
}

.confidence-label {
    font-size: 0.76rem;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.confidence-bar-bg {
    flex: 1;
    height: 6px;
    background: #eef1f6;
    border-radius: 999px;
    overflow: hidden;
}

.confidence-bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.confidence-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 600;
    min-width: 3.2rem;
    text-align: right;
}

/* ---------- No-answer state ---------- */
.no-answer-notice {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.65rem 0.9rem;
    margin-top: 0.45rem;
    background: rgba(243, 156, 18, 0.08);
    border: 1px solid rgba(243, 156, 18, 0.2);
    border-radius: 10px;
    font-size: 0.84rem;
    color: #b37400;
    font-weight: 500;
}

/* ---------- Upload prompt card ---------- */
.upload-prompt-card {
    text-align: center;
    padding: 2.5rem 2rem;
    background: linear-gradient(145deg, #ffffff 0%, #f8f9fc 100%);
    border: 2px dashed rgba(91, 76, 219, 0.2);
    border-radius: 20px;
    margin: 1.5rem 0;
}

.upload-prompt-card .icon {
    font-size: 3rem;
    margin-bottom: 0.6rem;
}

.upload-prompt-card h3 {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    color: #1a1a2e;
    margin: 0 0 0.4rem;
}

.upload-prompt-card p {
    color: #4a5568;
    font-size: 0.94rem;
    margin: 0;
}

/* ---------- Chat timestamp ---------- */
.chat-timestamp {
    font-size: 0.7rem;
    color: #94a3b8;
    margin-top: 0.3rem;
    font-family: 'JetBrains Mono', monospace;
}

.user-msg .chat-timestamp {
    text-align: right;
}

/* ---------- Empty-state illustration ---------- */
.empty-chat {
    text-align: center;
    padding: 3rem 1.5rem;
    color: #94a3b8;
}

.empty-chat .icon {
    font-size: 3.5rem;
    margin-bottom: 0.8rem;
    opacity: 0.6;
}

.empty-chat p {
    font-size: 1rem;
    color: #94a3b8;
    margin: 0;
}

/* ---------- Loaded paper card ---------- */
.loaded-paper-card {
    background: linear-gradient(145deg, #ffffff 0%, #f0eeff 100%);
    border: 1px solid rgba(91, 76, 219, 0.15);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 2px 12px rgba(91, 76, 219, 0.08);
    animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.loaded-paper-card .paper-icon {
    width: 3rem;
    height: 3rem;
    min-width: 3rem;
    border-radius: 12px;
    background: linear-gradient(135deg, #5b4cdb 0%, #a29bfe 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    color: rgba(255, 255, 255, 0.85);
}

.loaded-paper-card .paper-info {
    flex: 1;
}

.loaded-paper-card .paper-info h4 {
    margin: 0;
    font-family: 'Outfit', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    color: #1a1a2e;
}

.loaded-paper-card .paper-info p {
    margin: 0.15rem 0 0;
    font-size: 0.84rem;
    color: #4a5568;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Ensure uploader key exists (used to reset the uploader widget)
# ------------------------------------------------------------------
if "qa_uploader_key" not in st.session_state:
    st.session_state["qa_uploader_key"] = "qa_pdf_uploader_v0"

# ------------------------------------------------------------------
# PDF Upload / Paper Status Section
# ------------------------------------------------------------------
indexed_name = st.session_state.get("indexed_paper_name")

if indexed_name:
    # ---- Paper already loaded — show status + Re-upload button ----
    section_title("Paper Loaded")

    card_col, btn_col = st.columns([3, 1], gap="large")

    with card_col:
        st.markdown(
            f"""<div class='loaded-paper-card'>
                <div class='paper-icon'>📄</div>
                <div class='paper-info'>
                    <h4>{indexed_name}</h4>
                    <p>Indexed and ready — ask any question below</p>
                </div>
            </div>""",
            unsafe_allow_html=True
        )

    with btn_col:
        st.markdown("<div style='margin-top: 0.6rem;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Re-upload Paper", use_container_width=True, key="qa_reupload_btn"):
            # Clear all Q&A state
            st.session_state["qa_chat_history"] = []
            st.session_state["indexed_paper_name"] = None
            st.session_state["qa_paper_uploaded"] = False
            st.session_state["qa_response"] = None
            # Bump the uploader key so Streamlit creates a fresh widget
            import random
            st.session_state["qa_uploader_key"] = f"qa_pdf_uploader_v{random.randint(1, 999999)}"
            st.rerun()

else:
    # ---- No paper loaded — show uploader ----
    upload_col, info_col = st.columns([2, 1], gap="large")

    with upload_col:
        section_title("Upload Paper")
        qa_uploaded_file = st.file_uploader(
            "Upload a research paper PDF",
            type=["pdf"],
            key=st.session_state["qa_uploader_key"],
            help="Upload the paper you want to ask questions about."
        )

    with info_col:
        section_title("Status")
        st.markdown(
            """<div class='info-card info-card-neutral'>
                <h4>💡&ensp;No paper loaded</h4>
                <p>Upload a PDF on the left to start asking questions.</p>
            </div>""",
            unsafe_allow_html=True
        )

    # ---- Index the paper when uploaded ----
    if qa_uploaded_file is not None:
        file_error = validate_uploaded_pdf(qa_uploaded_file.name, qa_uploaded_file.size)
        if file_error:
            st.error(file_error)
        else:
            embed_model, _tok, _mdl, _qa = get_models()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(qa_uploaded_file.getvalue())
                pdf_path = tmp.name

            with st.spinner("🔍 Building semantic index for your paper..."):
                ingest_pdf(pdf_path, "uploaded_paper", embed_model)
                st.session_state["indexed_paper_name"] = qa_uploaded_file.name
                st.session_state["qa_paper_uploaded"] = True

            st.success(f"✅ **{qa_uploaded_file.name}** indexed successfully!")
            st.rerun()

# ------------------------------------------------------------------
# Chat history rendering
# ------------------------------------------------------------------
section_title("Conversation")

chat_history = st.session_state.get("qa_chat_history", [])

if not chat_history:
    if st.session_state.get("indexed_paper_name"):
        st.markdown(
            """<div class='empty-chat'>
                <div class='icon'>💬</div>
                <p>Your paper is ready. Type a question below to start!</p>
            </div>""",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """<div class='upload-prompt-card'>
                <div class='icon'>📄</div>
                <h3>Upload a Paper First</h3>
                <p>Once you upload a research paper PDF, you can ask any question about it and get instant answers powered by DistilBERT.</p>
            </div>""",
            unsafe_allow_html=True
        )
else:
    # Render chat messages
    for entry in chat_history:
        role = entry["role"]
        timestamp = entry.get("timestamp", "")

        if role == "user":
            content = entry.get("content", "")
            st.markdown(
                f"""<div class='chat-message user-msg'>
                    <div class='chat-avatar user-avatar'>You</div>
                    <div>
                        <div class='chat-bubble user-bubble'>
                            <p class='answer-text'>{content}</p>
                        </div>
                        <div class='chat-timestamp'>{timestamp}</div>
                    </div>
                </div>""",
                unsafe_allow_html=True
            )
        else:
            # Bot answer
            answer_text = entry.get("answer", "")
            confidence = entry.get("confidence", 0.0)
            has_answer = entry.get("has_answer", False)

            conf_pct = f"{confidence:.1%}"
            if confidence >= 0.5:
                bar_color = "#00b894"
                conf_text_color = "#00b894"
            elif confidence >= 0.2:
                bar_color = "#f39c12"
                conf_text_color = "#f39c12"
            else:
                bar_color = "#d63031"
                conf_text_color = "#d63031"

            bar_width = f"{min(confidence * 100, 100):.0f}%"

            if has_answer and answer_text:
                st.markdown(
                    f"""<div class='chat-message'>
                        <div class='chat-avatar bot-avatar'>AI</div>
                        <div>
                            <div class='chat-bubble bot-bubble'>
                                <p class='answer-text'>{answer_text}</p>
                                <div class='confidence-row'>
                                    <span class='confidence-label'>Confidence</span>
                                    <div class='confidence-bar-bg'>
                                        <div class='confidence-bar-fill' style='width: {bar_width}; background: {bar_color};'></div>
                                    </div>
                                    <span class='confidence-value' style='color: {conf_text_color};'>{conf_pct}</span>
                                </div>
                            </div>
                            <div class='chat-timestamp'>{timestamp}</div>
                        </div>
                    </div>""",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""<div class='chat-message'>
                        <div class='chat-avatar bot-avatar'>AI</div>
                        <div>
                            <div class='chat-bubble bot-bubble'>
                                <div class='no-answer-notice'>
                                    ⚠️ I couldn't find a confident answer for this in the paper. Try rephrasing or asking a more specific question.
                                </div>
                            </div>
                            <div class='chat-timestamp'>{timestamp}</div>
                        </div>
                    </div>""",
                    unsafe_allow_html=True
                )

# ------------------------------------------------------------------
# Question input
# ------------------------------------------------------------------
st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

question_col, btn_col = st.columns([5, 1], gap="small")

with question_col:
    user_question = st.text_input(
        "Your question",
        placeholder="e.g. What methodology did the authors use?",
        key="qa_question_input",
        label_visibility="collapsed",
    )

with btn_col:
    ask_clicked = st.button("🔎 Ask", use_container_width=True, key="qa_ask_btn")

# ------------------------------------------------------------------
# Handle question submission
# ------------------------------------------------------------------
if ask_clicked:
    if not user_question.strip():
        st.error("Please type a question before clicking Ask.")
    elif not st.session_state.get("indexed_paper_name"):
        st.error("Please upload a research paper PDF first.")
    else:
        now = datetime.now().strftime("%I:%M %p")

        # Add user message to history
        st.session_state["qa_chat_history"].append({
            "role": "user",
            "content": user_question.strip(),
            "timestamp": now,
        })

        # Run QA
        try:
            embed_model, _tok, _mdl, qa_assets = get_models()

            with st.spinner("🧠 DistilBERT is analyzing the paper..."):
                qa_result = answer_question(
                    question=user_question.strip(),
                    embed_model=embed_model,
                    qa_assets=qa_assets,
                    top_k=5,
                )

            # Add bot response to history
            st.session_state["qa_chat_history"].append({
                "role": "assistant",
                "answer": qa_result.get("answer", ""),
                "confidence": qa_result.get("confidence", 0.0),
                "has_answer": qa_result.get("has_answer", False),
                "timestamp": now,
            })

            st.rerun()

        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Unable to process question: {e}")

# ------------------------------------------------------------------
# Clear chat button
# ------------------------------------------------------------------
if chat_history:
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    col_spacer, col_clear = st.columns([4, 1])
    with col_clear:
        if st.button("🗑️ Clear Chat", use_container_width=True, key="qa_clear_btn"):
            st.session_state["qa_chat_history"] = []
            st.rerun()
