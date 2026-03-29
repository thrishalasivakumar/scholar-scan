# ScholarScan

An AI-powered Streamlit application for evaluating research papers using semantic retrieval, transformer-based summarization, and extractive question answering.

## What This Project Does

ScholarScan helps evaluators analyze long research papers quickly:

- **Upload** a research paper in PDF format.
- **Summarize** with a focused evaluation query (objective, methodology, novelty, limitations, outcomes).
- **Ask questions** about the paper in a chat-style interface and receive extractive answers powered by DistilBERT.
- **Review** extracted key points at a glance.
- **Export** results as TXT, DOCX, or PDF.

## Features

| Feature | Description |
|---------|-------------|
| **Semantic Summarization** | Query-driven abstractive summaries using BART, guided by cosine-similarity retrieval over sentence embeddings. |
| **Paper Q\&A (Ask Paper)** | Chat-style interface where users ask free-form questions and receive extractive answers from the paper via DistilBERT. |
| **Per-Chunk QA** | QA runs on each retrieved chunk individually (not concatenated), improving answer accuracy and confidence scores. |
| **Confidence Scoring** | Sigmoid-based confidence metric blended with softmax geometric mean — far more meaningful than raw token-level probabilities. |
| **Multi-Format Export** | Download summaries as plain text, Word (.docx), or PDF. |
| **Re-upload Workflow** | Chat history persists across questions; a dedicated Re-upload button clears state for a new paper. |

## UI Highlights

- Professional multi-page interface: **Home**, **Summarizer**, **About**, and **Ask Paper**.
- Chat-style Q\&A with user/AI message bubbles, timestamps, and visual confidence meters.
- Card-based output with key-point extraction for quick scanning.
- Premium light theme with Outfit/Inter/JetBrains Mono typography, gradient accents, and micro-animations.
- Responsive layout optimized for evaluator presentations.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit (multi-page app) |
| Embeddings | `sentence-transformers/all-mpnet-base-v2` |
| Summarization | `facebook/bart-large-cnn` |
| Question Answering | `distilbert-base-cased-distilled-squad` |
| PDF Parsing | PyMuPDF (`fitz`) |
| Similarity Search | scikit-learn cosine similarity |
| Exports | python-docx, PyMuPDF |
| Styling | Custom CSS (glassmorphism, gradients, animations) |

## Project Structure

```text
ScholarScan/
├── app.py                    # Home page — overview and model loading
├── backend.py                # Core logic: PDF ingestion, summarization, QA
├── requirements.txt          # Python dependencies
├── run.txt                   # Quick-start command reference
├── pages/
│   ├── 1_Summarizer.py       # Summarizer page — upload, query, export
│   ├── 2_About.py            # About page — pipeline and model details
│   └── 3_Ask_Paper.py        # Ask Paper page — chat-style Q&A
├── utils/
│   ├── __init__.py
│   ├── state.py              # Session state and model caching
│   ├── ui_components.py      # Reusable UI components (cards, banners)
│   └── validators.py         # Input validation helpers
├── assets/
│   └── styles.css            # Global premium CSS theme
└── .streamlit/
    └── config.toml           # Streamlit theme configuration
```

## Setup

### 1. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. NLTK data

The app calls `nltk.download("punkt")` automatically on first run.

## Run the App

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501` by default.

## How to Use

### Summarizer

1. Open the **Summarizer** page from the sidebar.
2. Enter a focused evaluation query.
3. Choose summary length (short / medium / long).
4. Upload a PDF (up to 50 MB).
5. Click **🚀 Generate Summary**.
6. Review the summary and key points.
7. Download as TXT, DOCX, or PDF.

### Ask Paper (Q\&A)

1. Open the **Ask Paper** page from the sidebar.
2. Upload a research paper PDF — it is automatically indexed.
3. Type any question about the paper (e.g., *"What datasets were used?"*).
4. Click **🔎 Ask** to get an extractive answer with a confidence score.
5. Continue asking questions — chat history persists.
6. Click **🔄 Re-upload Paper** to clear history and load a new paper.

## Architecture Overview

```
PDF  ──▶  Text Extraction & Cleaning
              │
              ▼
         Chunking (900 tokens, 150 overlap)
              │
              ▼
         Sentence Embedding (all-mpnet-base-v2)
              │
              ├──▶  Cosine Similarity with query
              │         │
              │         ▼
              │    Top-K Chunk Retrieval
              │         │
              │         ├──▶  BART Summarization ──▶ Summary + Key Points
              │         │
              │         └──▶  Per-Chunk DistilBERT QA ──▶ Answer + Confidence
              │
              └──▶  Stored in-memory for session
```

1. PDF text is extracted with PyMuPDF and cleaned.
2. Text is split into overlapping chunks and embedded.
3. Query embedding is matched to chunk embeddings via cosine similarity.
4. Top chunks are passed to BART for abstractive summarization.
5. For Q\&A, DistilBERT runs extractive QA on **each chunk individually** (not concatenated), picking the best answer across all chunks.
6. Key points are extracted from generated summary sentences.
7. Export payload is generated in the requested format.

## Configuration

### Summary Length Presets

Defined in `backend.py`:

| Preset | Max Length | Min Length |
|--------|-----------|-----------|
| Short | 90 | 30 |
| Medium | 200 | 160 |
| Long | 360 | 200 |

### Theme and UI

- `.streamlit/config.toml` — Streamlit-level theme settings.
- `assets/styles.css` — Custom card styling, typography, spacing, animations, and responsive breakpoints.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Slow first run | Model weights are downloaded on first execution; subsequent runs use cache. |
| CUDA not available | The app automatically falls back to CPU. |
| Empty or weak summary | Refine your focus query, try `medium` or `long` length, or ensure the PDF has extractable text. |
| Low QA confidence | Try rephrasing the question to be more specific; the per-chunk approach should yield scores in the 40–80% range. |
| Export errors | Rerun summary generation and retry download. |

## Known Limitations

- Index is in-memory and resets when the app restarts.
- Very large papers increase processing time and memory usage.
- Summary quality depends on the relevance of retrieved chunks to the query.
- DistilBERT performs extractive QA — answers are spans from the paper, not generated text.

## Future Enhancements

- Persistent vector storage per paper across sessions.
- Batch paper comparison mode.
- OCR enhancement for scanned PDFs.
- Citation-aware summarization and section-level insights.
- Generative QA (e.g., FLAN-T5) for more natural answers.

## Quick Demo Checklist (For Evaluators)

1. Upload a sample paper on the **Summarizer** page.
2. Run a query on objective + conclusion.
3. Run a second query on limitations.
4. Export summary as PDF and DOCX.
5. Switch to **Ask Paper** — ask 2–3 questions about the paper.
6. Compare key points with the abstract and conclusion.

## License

Use and adapt this project for educational and internal evaluation purposes.
