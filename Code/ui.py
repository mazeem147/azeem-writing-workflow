import html
import streamlit as st

PALETTE = {
    "ink":       "#0d0c14",
    "ink_light": "#1a1826",
    "ink_mid":   "#2a2838",
    "gold":      "#c9a96e",
    "gold_dim":  "#8a6e42",
    "text":      "#e8e4dc",
    "muted":     "#9b9690",
    "done":      "#4a9e6b",
    "border":    "#2e2c3a",
    "error":     "#e05252",
}

_p = PALETTE  # alias for brevity in the CSS block below

_CSS = (
    "<style>"
    "html,body,[data-testid='stAppViewContainer']{"
      "background-color:" + _p["ink"] + " !important;"
      "color:" + _p["text"] + ";"
      "font-family:system-ui,-apple-system,sans-serif;}"
    "#MainMenu,footer{visibility:hidden;}"
    "header{background:transparent !important;}"
    "[data-testid='stBaseButton-header'],[data-testid='stStatusWidget']{display:none !important;}"
    "[data-testid='stToolbar']{background:transparent !important;}"
    "[data-testid='stExpandSidebarButton']{"
      "background:" + _p["ink_light"] + " !important;"
      "border:1px solid " + _p["border"] + " !important;"
      "border-radius:6px !important;"
      "color:" + _p["gold"] + " !important;"
      "cursor:pointer !important;}"
    "[data-testid='stExpandSidebarButton'] *{"
      "color:" + _p["gold"] + " !important;}"
    "[data-testid='stSidebar']{"
      "background-color:" + _p["ink_light"] + " !important;"
      "border-right:1px solid " + _p["border"] + ";}"
    "[data-testid='stSidebar'] *{color:" + _p["text"] + " !important;}"
    "[data-testid='stSidebar'] a{text-decoration:none !important;}"
    ".block-container{padding-top:2rem !important;max-width:780px;}"
    "h1,h2,h3,.article-heading{"
      "font-family:Georgia,'Times New Roman',serif;"
      "color:" + _p["text"] + ";}"
    "hr{border:none;border-top:1px solid " + _p["border"] + ";margin:1.5rem 0;}"
    "[data-testid='stButton']>button{"
      "background:" + _p["gold"] + ";"
      "color:" + _p["ink"] + ";"
      "border:none;font-weight:600;border-radius:6px;padding:0.5rem 1.25rem;}"
    "[data-testid='stButton']>button:hover{"
      "background:" + _p["gold_dim"] + ";"
      "color:" + _p["text"] + ";}"
    "[data-testid='stTextInput'] input,"
    "[data-testid='stTextArea'] textarea{"
      "background:" + _p["ink_mid"] + " !important;"
      "color:" + _p["text"] + " !important;"
      "border:1px solid " + _p["border"] + " !important;"
      "border-radius:6px;}"
    # Style the sidebar page_links to match the design system
    "[data-testid='stSidebar'] [data-testid='stPageLink']{"
      "padding:0 !important;margin:0 !important;}"
    "[data-testid='stSidebar'] [data-testid='stPageLink'] p{"
      "font-size:0.9rem !important;margin:0 !important;}"
    "</style>"
)

STAGES = [
    {"key": "transcribe", "label": "Transcribe", "icon": "🎙"},
    {"key": "develop",    "label": "Develop",    "icon": "💬"},
    {"key": "plan",       "label": "Plan",        "icon": "📋"},
    {"key": "draft",      "label": "Draft",       "icon": "✍️"},
    {"key": "publish",    "label": "Publish",     "icon": "🚀"},
]

_STAGE_INDEX = {s["key"]: i for i, s in enumerate(STAGES)}

_PAGE_PATHS = {
    "transcribe": "pages/transcribe.py",
    "develop":    "pages/develop.py",
    "plan":       "pages/plan.py",
    "draft":      "pages/draft.py",
    "publish":    "pages/publish.py",
}


def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)


def render_page_header(stage_key: str, title: str, subtitle: str):
    """Render the gold h1 + muted subtitle used on every stage page."""
    gold  = _p["gold"]
    muted = _p["muted"]
    safe_title    = html.escape(title)
    safe_subtitle = html.escape(subtitle)
    st.markdown(
        "<h1 style='font-family:Georgia,serif;color:" + gold + "'>" + safe_title + "</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:" + muted + "'>" + safe_subtitle + "</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")


def render_sidebar(active_stage: str):
    active_idx = _STAGE_INDEX.get(active_stage, 0)
    raw_title = st.session_state.get("working_title", "Untitled piece")
    working_title = html.escape(str(raw_title))

    gold   = _p["gold"]
    muted  = _p["muted"]
    text   = _p["text"]
    done   = _p["done"]
    border = _p["border"]

    with st.sidebar:
        st.markdown(
            "<p style='font-family:Georgia,serif;font-size:1.15rem;color:" + gold + ";"
            "margin-bottom:0.25rem;font-weight:700'>Writing Workflow</p>",
            unsafe_allow_html=True,
        )
        st.markdown("<hr style='margin:0.75rem 0'>", unsafe_allow_html=True)

        for i, stage in enumerate(STAGES):
            if i < active_idx:
                dot_color   = done
                dot         = "✓"
                label_color = text
                fw          = "400"
            elif i == active_idx:
                dot_color   = gold
                dot         = "●"
                label_color = gold
                fw          = "600"
            else:
                dot_color   = muted
                dot         = "○"
                label_color = muted
                fw          = "400"

            # Vertical connector line below the dot (except last item)
            connector = (
                "<div style='width:1px;height:14px;background:" + border + ";margin:1px auto 1px auto'></div>"
                if i < len(STAGES) - 1 else ""
            )

            icon  = stage["icon"]
            label = stage["label"]
            path  = _PAGE_PATHS[stage["key"]]

            # Left column: dot + connector line; right column: page_link
            col_dot, col_label = st.columns([1, 5])
            with col_dot:
                st.markdown(
                    "<div style='display:flex;flex-direction:column;align-items:center;padding-top:4px'>"
                    "<span style='color:" + dot_color + ";font-size:0.75rem;line-height:1'>" + dot + "</span>"
                    + connector +
                    "</div>",
                    unsafe_allow_html=True,
                )
            with col_label:
                st.page_link(
                    path,
                    label=icon + " " + label,
                )

        st.markdown("<hr style='margin:0.75rem 0'>", unsafe_allow_html=True)
        st.markdown(
            "<p style='font-size:0.7rem;color:" + muted + ";margin-bottom:2px'>Current piece</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='font-size:0.85rem;color:" + text + ";font-family:Georgia,serif;margin-top:0'>"
            + working_title + "</p>",
            unsafe_allow_html=True,
        )
