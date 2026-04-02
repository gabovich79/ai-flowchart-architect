"""
AI Flowchart Architect
Transform natural language process descriptions into professional Mermaid.js flowcharts.
"""

import streamlit as st
from dotenv import load_dotenv
import os

from config import UI_TEXT, OPENAI_MODEL
from llm_engine import generate_mermaid, refine_mermaid, validate_logic, rewrite_professional
from mermaid_utils import validate_mermaid, inject_styles, export_diagram, export_to_pptx

load_dotenv(override=True)  # .env file takes priority over system env vars

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="AI Flowchart Architect",
    page_icon="🔀",
    layout="wide",
    initial_sidebar_state="auto",  # Collapsed on mobile, expanded on desktop
)

# ── Load Custom CSS ───────────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Session State Init ────────────────────────────────────────
if "mermaid_code" not in st.session_state:
    st.session_state.mermaid_code = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "language" not in st.session_state:
    st.session_state.language = "en"
st.session_state.provider = "openai"  # Fixed to OpenAI
if "validation_result" not in st.session_state:
    st.session_state.validation_result = None
if "professional_tone" not in st.session_state:
    st.session_state.professional_tone = False

# ── Helper: Get UI text ──────────────────────────────────────
def t(key: str) -> str:
    """Get translated UI text."""
    return UI_TEXT.get(st.session_state.language, UI_TEXT["en"]).get(key, key)


def _get_api_key() -> str:
    """
    Load OpenAI API key from .env file or Streamlit secrets.
    Priority: st.secrets > environment variable (.env)
    Never exposed in the UI.
    """
    key_name = "OPENAI_API_KEY"

    # Try st.secrets first (for Streamlit Cloud deployment)
    try:
        return st.secrets[key_name]
    except (KeyError, FileNotFoundError):
        pass

    # Fall back to .env / environment variable
    return os.getenv(key_name, "")


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ " + t("sidebar_title"))

    # Language toggle
    lang = st.radio(
        t("language_label"),
        options=["English", "עברית"],
        index=0 if st.session_state.language == "en" else 1,
        horizontal=True,
    )
    st.session_state.language = "en" if lang == "English" else "he"

    st.divider()

    # LLM Model info
    st.markdown(
        f"""
        <div style="padding: 8px 12px; border-radius: 8px; background: rgba(108,99,255,0.08);
                    border: 1px solid rgba(108,99,255,0.15); font-size: 0.85em; color: #aaa;">
        🤖 {t("model_label")}: <b style="color: #6C63FF;">{OPENAI_MODEL}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Professional Tone toggle
    st.session_state.professional_tone = st.toggle(
        t("professional_tone"),
        value=st.session_state.professional_tone,
        help=t("professional_tone_help"),
    )

    st.divider()

    # Info box
    tips_dir = "rtl" if st.session_state.language == "he" else "ltr"
    st.markdown(
        f"""
        <div dir="{tips_dir}" style="padding: 12px; border-radius: 8px; background: rgba(108,99,255,0.1);
                    border: 1px solid rgba(108,99,255,0.3); font-size: 0.85em;">
        {t("tips_box")}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── RTL wrapper for Hebrew ────────────────────────────────────
if st.session_state.language == "he":
    st.markdown(
        '<div dir="rtl" style="text-align: right;">',
        unsafe_allow_html=True,
    )

# ── Header ────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="text-align: center; padding: 1rem 0 0.5rem;">
        <h1 style="margin-bottom: 0.2em;">🔀 {t("title")}</h1>
        <p style="color: #888; font-size: 1.1em;">{t("subtitle")}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Main Input Area ───────────────────────────────────────────
description = st.text_area(
    t("input_label"),
    placeholder=t("input_placeholder"),
    height=120,
    key="process_input",
)

col_gen, col_spacer = st.columns([1, 3])
with col_gen:
    generate_clicked = st.button(
        f"⚡ {t('generate_btn')}",
        type="primary",
        use_container_width=True,
    )

# ── Generate Flowchart ────────────────────────────────────────
if generate_clicked:
    api_key = _get_api_key()
    if not api_key:
        st.error("🔑 " + t("error_no_key"))
    elif not description.strip():
        st.warning("✏️ " + t("input_label"))
    else:
        with st.spinner(t("spinner_generating")):
            try:
                code = generate_mermaid(
                    description, st.session_state.provider, api_key
                )
                code = inject_styles(code)
                if validate_mermaid(code):
                    # Professional tone rewrite
                    if st.session_state.professional_tone:
                        with st.spinner(t("rewriting_tone")):
                            try:
                                code = rewrite_professional(
                                    code, st.session_state.provider, api_key
                                )
                                code = inject_styles(code)
                            except Exception:
                                pass  # Keep original if rewrite fails

                    st.session_state.mermaid_code = code
                    st.session_state.chat_history = [
                        {"role": "user", "content": description}
                    ]

                    # Auto-validate logic
                    with st.spinner(t("validation_running")):
                        try:
                            st.session_state.validation_result = validate_logic(
                                code, st.session_state.provider, api_key
                            )
                        except Exception:
                            st.session_state.validation_result = None

                    st.toast(t("toast_ready"), icon="🚀")
                else:
                    st.error("❌ " + t("error_invalid"))
            except Exception as e:
                st.error("❌ " + t("error_api").format(str(e)))

# ── Diagram Display ───────────────────────────────────────────
if st.session_state.mermaid_code:
    st.markdown("---")

    # Render Mermaid diagram
    try:
        from streamlit_mermaid import st_mermaid

        st_mermaid(st.session_state.mermaid_code, height=500)
    except ImportError:
        # Fallback: render via mermaid.ink in an iframe
        import base64

        encoded = base64.urlsafe_b64encode(
            st.session_state.mermaid_code.encode()
        ).decode()
        svg_url = f"https://mermaid.ink/svg/{encoded}"
        st.markdown(
            f'<div style="text-align:center; background:#1a1d24; padding:20px; '
            f'border-radius:12px;">'
            f'<img src="{svg_url}" style="max-width:100%;" alt="Flowchart"/>'
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── Logic Health Check ─────────────────────────────────────
    if st.session_state.validation_result:
        vr = st.session_state.validation_result
        st.markdown(f"#### {t('validation_title')}")
        if vr.get("status") == "green":
            st.success(t("validation_green"))
        else:
            st.warning(t("validation_yellow"))
            for issue in vr.get("issues", []):
                issue_type = issue.get("type", "unknown")
                node = issue.get("node", "?")
                detail = issue.get("detail", "")
                icon = {"orphan_node": "🔘", "infinite_loop": "🔄", "missing_exit": "🚫", "dead_end": "⛔"}.get(issue_type, "⚠️")
                st.markdown(f"&nbsp;&nbsp;{icon} **{issue_type}** (node `{node}`): {detail}")

    # ── Export Buttons ────────────────────────────────────────
    st.markdown("")

    # Code block - full width
    with st.expander(f"📋 {t('copy_btn')} (Mermaid)", expanded=False):
        st.code(st.session_state.mermaid_code, language="mermaid")

    # Download buttons
    col_png, col_svg, col_pptx = st.columns(3)

    with col_png:
        png_data = export_diagram(st.session_state.mermaid_code, "png")
        if png_data:
            st.download_button(
                f"📥 {t('download_png')}",
                data=png_data,
                file_name="flowchart.png",
                mime="image/png",
                use_container_width=True,
            )

    with col_svg:
        svg_data = export_diagram(st.session_state.mermaid_code, "svg")
        if svg_data:
            st.download_button(
                f"📥 {t('download_svg')}",
                data=svg_data,
                file_name="flowchart.svg",
                mime="image/svg+xml",
                use_container_width=True,
            )

    with col_pptx:
        pptx_data = export_to_pptx(st.session_state.mermaid_code)
        if pptx_data:
            st.download_button(
                f"📥 {t('download_pptx')}",
                data=pptx_data,
                file_name="flowchart.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True,
            )

    # ── Refinement Chat ───────────────────────────────────────
    st.markdown("---")
    st.markdown(f"### 💬 {t('refine_label')}")

    # Show chat history
    for msg in st.session_state.chat_history:
        role_icon = "👤" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Refinement input
    refine_input = st.chat_input(t("refine_placeholder"))

    if refine_input:
        api_key = _get_api_key()
        if not api_key:
            st.error("🔑 " + t("error_no_key"))
        else:
            st.session_state.chat_history.append(
                {"role": "user", "content": refine_input}
            )

            with st.spinner(t("spinner_refining")):
                try:
                    updated_code = refine_mermaid(
                        st.session_state.mermaid_code,
                        refine_input,
                        st.session_state.provider,
                        api_key,
                    )
                    updated_code = inject_styles(updated_code)
                    if validate_mermaid(updated_code):
                        st.session_state.mermaid_code = updated_code
                        st.session_state.chat_history.append(
                            {
                                "role": "assistant",
                                "content": "✅ Diagram updated!",
                            }
                        )
                        # Re-validate after refinement
                        try:
                            st.session_state.validation_result = validate_logic(
                                updated_code, st.session_state.provider, api_key
                            )
                        except Exception:
                            pass
                        st.toast(t("toast_updated"), icon="✨")
                    else:
                        st.session_state.chat_history.append(
                            {
                                "role": "assistant",
                                "content": "❌ " + t("error_invalid"),
                            }
                        )
                except Exception as e:
                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": "❌ " + t("error_api").format(str(e)),
                        }
                    )
            st.rerun()

else:
    # Empty state
    st.markdown(
        f"""
        <div style="text-align: center; padding: 4rem 2rem; color: #555;">
            <div style="font-size: 4em; margin-bottom: 0.5em;">🔀</div>
            <p style="font-size: 1.2em;">{t("no_diagram")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Close RTL wrapper
if st.session_state.language == "he":
    st.markdown("</div>", unsafe_allow_html=True)
