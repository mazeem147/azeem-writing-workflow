import os
import re
import html as _html
import httpx
import streamlit as st
from ui import inject_css, render_sidebar, render_page_header, PALETTE
from components.voice_input import voice_input_widget

inject_css()
render_sidebar("draft")
render_page_header("draft", "✍️ Draft", "Your article, generated section by section in your Voice.")

# ── Voice rules path ──────────────────────────────────────────────────────────
_PAGES_DIR  = os.path.dirname(os.path.abspath(__file__))
_CODE_DIR   = os.path.dirname(_PAGES_DIR)
_WF_DIR     = os.path.dirname(_CODE_DIR)
_WORKSPACE  = os.path.dirname(_WF_DIR)
_SKILL_PATH = os.path.join(_WORKSPACE, "skills", "writing-voice", "SKILL.md")

_VOICE_RULES = ""
try:
    with open(_SKILL_PATH, "r") as _skill_f:
        _VOICE_RULES = _skill_f.read()
except Exception:
    pass

# ── Guard ─────────────────────────────────────────────────────────────────────
if not st.session_state.get("writing_plan"):
    st.markdown(
        "<p style='color:" + PALETTE["muted"] + "'>No Writing Plan found. "
        "Please complete the <strong>Plan</strong> stage first.</p>",
        unsafe_allow_html=True,
    )
    if st.button("← Go to Plan"):
        st.switch_page("pages/plan.py")
    st.stop()


# ── LLM helper ────────────────────────────────────────────────────────────────
def _call_claude(messages, timeout=120):
    key = os.environ["OPENROUTER_API_KEY"]
    resp = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
        },
        json={"model": "anthropic/claude-sonnet-4-5", "messages": messages},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


# ── Voice-rule enforcement ────────────────────────────────────────────────────
# Matches an em dash (U+2014) or horizontal bar (U+2015) plus any surrounding
# whitespace. \s and \u are both interpreted by the re engine.
_EM_DASH_RE = re.compile(r"\s*[—―]\s*")


def _strip_em_dashes(text):
    """The Voice rules forbid em dashes, but the model emits them anyway.
    Replace each em dash (with its surrounding whitespace) with a comma so the
    clause break still reads naturally, then tidy any doubled/space-before commas."""
    text = _EM_DASH_RE.sub(", ", text)
    text = re.sub(r"\s+,", ",", text)         # " ," -> ","
    text = re.sub(r",\s*,", ", ", text)       # ",," / ", ," -> ", "
    text = re.sub(r"[^\S\n]{2,}", " ", text)  # collapse runs of spaces/tabs, keep newlines
    return text


# ── Style Fingerprint extraction ──────────────────────────────────────────────
def _extract_style_fingerprint(style_notes):
    notes_text = ""
    for i, note in enumerate(style_notes):
        notes_text += "Note " + str(i + 1) + ":\n" + note["text"] + "\n\n"

    system = (
        "You are a literary analyst. Extract a Style Fingerprint from the writing samples below "
        "— a precise description of the rhetorical and prose patterns you observe.\n\n"
        "Analyse and describe:\n"
        "1. Sentence rhythm: how does sentence length vary? When do short sentences appear?\n"
        "2. Paragraph openers: how does this writer typically begin a paragraph?\n"
        "3. How doubt or uncertainty is introduced: what phrases signal it?\n"
        "4. Analogy structures: what kinds of comparisons does this writer reach for?\n"
        "5. Any distinctive cadence, code-switching, or voice markers.\n\n"
        "Be specific and concrete. Quote short phrases from the samples as evidence where helpful. "
        "This fingerprint will guide article generation — make it actionable. "
        "Write 200-350 words in flowing prose. No headers or bullet points."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": "Writing samples:\n\n" + notes_text},
    ]
    return _call_claude(messages)


# ── Section generation ────────────────────────────────────────────────────────
def _generate_section(section_idx, feedback=None):
    plan    = st.session_state.writing_plan
    section = plan[section_idx]
    total   = len(plan)

    fingerprint  = st.session_state.get("style_fingerprint") or ""
    bullets_text = "\n".join("- " + b for b in section.get("bullets", []))
    pinned       = section.get("pinned_notes", [])

    if section_idx == 0:
        position_hint = (
            "This is the OPENING section. Do not open with a conclusion or summary. "
            "Start where the thinking begins. No generic scene-setting or preambles."
        )
    elif section_idx == total - 1:
        position_hint = (
            "This is the CLOSING section. End open — not unfinished, but not neatly resolved. "
            "Leave a door ajar: a question, a half-formed thought. Do not summarise what was said."
        )
    else:
        position_hint = (
            "This is section " + str(section_idx + 1) + " of " + str(total) + ". "
            "Maintain forward motion — the argument is mid-journey."
        )

    pinned_block = ""
    if pinned:
        pinned_block = (
            "\n\nContent Notes for this section "
            "(use as raw material — weave them in, do not quote verbatim):\n"
        )
        for note_text in pinned:
            pinned_block += "\n---\n" + note_text + "\n"

    fingerprint_block = ""
    if fingerprint:
        fingerprint_block = (
            "\n\nStyle Fingerprint "
            "(how this writer's prose actually sounds — match it closely):\n"
            + fingerprint
        )

    voice_block = ""
    if _VOICE_RULES:
        voice_block = "\n\nVoice Rules (non-negotiable — follow these exactly):\n" + _VOICE_RULES

    revision_block = ""
    if feedback:
        revision_block = (
            "\n\nRevision feedback from the writer — apply this precisely:\n" + feedback
        )

    system = (
        "You are writing one section of an article in the writer's own voice.\n\n"
        "Section title: " + section["title"] + "\n"
        "Points to cover:\n" + bullets_text + "\n\n"
        + position_hint
        + fingerprint_block
        + voice_block
        + pinned_block
        + revision_block
        + "\n\nWrite 2-4 paragraphs of prose. No section header or title at the start. "
        "No bullet points. No em dashes. "
        "Write in first person where natural. "
        "Do not restate the section title in your first sentence. Just write the section."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": "Write this section now."},
    ]
    return _strip_em_dashes(_call_claude(messages))


# ── Inline revision form ──────────────────────────────────────────────────────
def _render_revision_form(section_idx):
    gold   = PALETTE["gold"]
    muted  = PALETTE["muted"]
    border = PALETTE["border"]
    ink_mid = PALETTE["ink_mid"]

    st.markdown(
        "<div style='margin:0.25rem 0 0.75rem;padding:1rem 1.25rem;"
        "border:1px solid " + gold + ";border-radius:8px;"
        "background:" + ink_mid + "'>"
        "<p style='color:" + gold + ";font-size:0.8rem;font-weight:600;margin:0'>"
        "Revision feedback</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    mic_col, label_col = st.columns([1, 9])
    with label_col:
        st.markdown(
            "<p style='color:" + muted + ";font-size:0.78rem;margin:0 0 2px'>"
            "What to change — type it or use the mic</p>",
            unsafe_allow_html=True,
        )
    with mic_col:
        voice_input_widget("revision_feedback")

    feedback = st.text_area(
        "Feedback",
        placeholder="Describe what to change, or speak it with the mic above…",
        height=90,
        key="revision_feedback",
        label_visibility="collapsed",
    )

    regen_col, cancel_col, _ = st.columns([2, 1, 4])
    with regen_col:
        if st.button("Regenerate →", type="primary", key="regen_" + str(section_idx)):
            feedback_text = feedback.strip() if feedback else None
            new_text = None
            with st.spinner("Regenerating section…"):
                try:
                    new_text = _generate_section(section_idx, feedback=feedback_text)
                except Exception as exc:
                    st.error("Regeneration failed: " + str(exc))

            if new_text is not None:
                st.session_state.draft_sections[section_idx] = new_text
                # Don't reset revision_feedback here: the text_area with this key
                # was already instantiated this run (StreamlitAPIException). Closing
                # the form and reopening it via "Revise ✦" clears the field safely
                # (before the widget is created).
                st.session_state.modal_section_idx = None
                st.rerun()

    with cancel_col:
        if st.button("Cancel", key="cancel_" + str(section_idx)):
            # See note above — the reset is handled on reopen, not here.
            st.session_state.modal_section_idx = None
            st.rerun()

    st.markdown(
        "<div style='margin:0.5rem 0 1.5rem;border-bottom:1px solid "
        + border + "'></div>",
        unsafe_allow_html=True,
    )


# ── Section card renderer ─────────────────────────────────────────────────────
def _render_section(section_idx, section_text):
    plan    = st.session_state.writing_plan
    section = plan[section_idx]

    gold    = PALETTE["gold"]
    text    = PALETTE["text"]
    border  = PALETTE["border"]
    ink_mid = PALETTE["ink_mid"]

    num        = str(section_idx + 1)
    safe_title = _html.escape(section["title"])
    safe_text  = _html.escape(section_text)

    para_style = (
        "margin:0 0 1rem;font-family:Georgia,serif;font-size:1.05rem;"
        "line-height:1.85;color:" + text
    )
    # Convert double newlines to paragraph breaks; single newlines to spaces
    safe_text = safe_text.replace(
        "\n\n",
        "</p><p style='" + para_style + "'>",
    ).replace("\n", " ")

    card_html = (
        "<div style='margin-bottom:0.4rem;padding:1.25rem 1.5rem;"
        "background:" + ink_mid + ";"
        "border:1px solid " + border + ";"
        "border-radius:8px'>"
        "<p style='color:" + gold + ";font-family:system-ui;font-size:0.75rem;"
        "font-weight:600;margin:0 0 0.75rem;letter-spacing:0.06em'>"
        "SECTION " + num + " — " + safe_title + "</p>"
        "<p style='" + para_style + ";margin-top:0'>" + safe_text + "</p>"
        "</div>"
    )
    st.markdown(card_html, unsafe_allow_html=True)

    # Revise button — right-aligned below the card
    is_open   = st.session_state.get("modal_section_idx") == section_idx
    btn_label = "Close ✕" if is_open else "Revise ✦"
    _, btn_col = st.columns([7, 2])
    with btn_col:
        if st.button(btn_label, key="revise_" + str(section_idx)):
            if is_open:
                st.session_state.modal_section_idx = None
                st.session_state.revision_feedback = ""
            else:
                st.session_state.modal_section_idx = section_idx
                st.session_state.revision_feedback = ""
            st.rerun()

    if is_open:
        _render_revision_form(section_idx)


# ── Session state defaults ────────────────────────────────────────────────────
if "style_fingerprint" not in st.session_state:
    st.session_state.style_fingerprint = None
if "draft_sections" not in st.session_state:
    st.session_state.draft_sections = None
if "modal_section_idx" not in st.session_state:
    st.session_state.modal_section_idx = None
if "revision_feedback" not in st.session_state:
    st.session_state.revision_feedback = ""

plan = st.session_state.writing_plan

# ── Step 1: Extract Style Fingerprint ────────────────────────────────────────
if st.session_state.style_fingerprint is None:
    style_notes = st.session_state.get("style_notes") or []
    fp = None
    if style_notes:
        with st.spinner("Extracting Style Fingerprint from your notes…"):
            try:
                fp = _extract_style_fingerprint(style_notes)
            except Exception as exc:
                st.error("Style Fingerprint extraction failed: " + str(exc))
                st.stop()
        if fp is None:
            st.stop()
    else:
        fp = ""  # No style notes available — proceed without a fingerprint
    st.session_state.style_fingerprint = fp
    st.session_state.draft_sections = []
    st.rerun()

# ── Step 2: Progressive section generation ────────────────────────────────────
if st.session_state.draft_sections is None:
    st.session_state.draft_sections = []

drafts = st.session_state.draft_sections

# Trim stale sections if the plan shrank since the last Draft visit
if len(drafts) > len(plan):
    st.session_state.draft_sections = drafts[:len(plan)]
    drafts = st.session_state.draft_sections

# Render all already-completed sections
for i, section_text in enumerate(drafts):
    _render_section(i, section_text)

# Generate next section if the draft is not yet complete
if len(drafts) < len(plan):
    next_idx      = len(drafts)
    section_title = plan[next_idx]["title"]
    quote_open    = '"'
    quote_close   = '"'
    spinner_msg   = (
        "Generating section " + str(next_idx + 1) + " of " + str(len(plan))
        + ": " + quote_open + section_title + quote_close + "…"
    )

    new_text = None
    with st.spinner(spinner_msg):
        try:
            new_text = _generate_section(next_idx)
        except Exception as exc:
            st.error("Section generation failed: " + str(exc))
            st.stop()

    if new_text is None:
        st.stop()

    st.session_state.draft_sections.append(new_text)
    st.rerun()

# ── All sections generated — bottom bar ──────────────────────────────────────
st.markdown("---")

n    = len(plan)
word = "section" if n == 1 else "sections"
hint = str(n) + " " + word + " generated. Click Revise ✦ on any section to refine it."

col_hint, col_btn = st.columns([3, 1])
with col_hint:
    st.markdown(
        "<p style='color:" + PALETTE["muted"] + ";font-size:0.85rem;padding-top:6px'>"
        + hint + "</p>",
        unsafe_allow_html=True,
    )
with col_btn:
    if st.button("Approve Draft →", type="primary"):
        st.session_state.draft_approved = True
        st.switch_page("pages/repurpose.py")
