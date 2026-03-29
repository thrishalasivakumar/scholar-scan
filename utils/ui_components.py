from pathlib import Path

import streamlit as st


STYLES_PATH = Path(__file__).resolve().parents[1] / "assets" / "styles.css"


def inject_global_style() -> None:
    if STYLES_PATH.exists():
        css = STYLES_PATH.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def section_title(title: str) -> None:
    st.markdown(f"<h3 class='section-title'>{title}</h3>", unsafe_allow_html=True)


def top_brand_banner(subtitle: str = "") -> None:
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        (
            "<div class='top-brand-banner'>"
            "<h1 style='"
            "font-family: Outfit, sans-serif; "
            "font-size: 5.5rem; "
            "font-weight: 900; "
            "letter-spacing: -0.03em; "
            "line-height: 1.1; "
            "margin: 0; padding: 0; "
            "background: linear-gradient(135deg, #5b4cdb 0%, #6c5ce7 40%, #a29bfe 100%); "
            "-webkit-background-clip: text; "
            "-webkit-text-fill-color: transparent; "
            "background-clip: text;"
            "'>ScholarScan</h1>"
            f"{subtitle_html}"
            "</div>"
        ),
        unsafe_allow_html=True
    )


def info_card(title: str, body: str, tone: str = "neutral") -> None:
    icon_map = {"neutral": "💡", "success": "✅", "warning": "⚠️"}
    icon = icon_map.get(tone, "")
    st.markdown(
        (
            f"<div class='info-card info-card-{tone}'>"
            f"<h4>{icon}&ensp;{title}</h4>"
            f"<p>{body}</p>"
            "</div>"
        ),
        unsafe_allow_html=True
    )


def metric_chip(label: str, value: str) -> None:
    st.markdown(
        f"<div class='metric-chip'><span>{label}</span><strong>{value}</strong></div>",
        unsafe_allow_html=True
    )


def key_point_card(index: int, text: str) -> None:
    st.markdown(
        (
            "<div class='keypoint-card'>"
            f"<div class='keypoint-index'>{index}</div>"
            f"<div class='keypoint-text'>{text}</div>"
            "</div>"
        ),
        unsafe_allow_html=True
    )
