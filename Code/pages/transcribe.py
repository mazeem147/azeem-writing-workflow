import re
import io
import os
import html as _html
import streamlit as st
from ui import inject_css, render_sidebar, render_page_header, PALETTE

inject_css()
render_sidebar("transcribe")
render_page_header("transcribe", "🎙 Transcribe", "Upload your voice memo to begin a Development Session.")

# Pattern for uncertain words marked by Claude as [word?]
_UNCERTAIN_RE = re.compile(r'\[([^\]]+?)\?\]')


def _transcribe_audio(file_bytes, filename):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    f = io.BytesIO(file_bytes)
    f.name = filename
    result = client.audio.transcriptions.create(model="whisper-1", file=f)
    return result.text


def _clean_transcript(raw):
    import httpx
    key = os.environ["OPENROUTER_API_KEY"]
    system = (
        "You are cleaning a voice memo transcript for an English/Urdu bilingual speaker. "
        "Fix obvious transcription errors and normalise Urdu romanisation where you are confident. "
        "For any word you are NOT confident about — garbled audio, ambiguous pronunciation, "
        "or likely mishearing — wrap it as [word?], keeping your best guess inside the brackets. "
        "Return only the corrected transcript text. No preamble, no explanation."
    )
    resp = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
        },
        json={
            "model": "anthropic/claude-haiku-4-5",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": raw},
            ],
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _apply_corrections(clean_text, corrections):
    """Replace [word?] markers with corrections (or original word if no correction given)."""
    counter = [0]

    def replacer(m):
        word = m.group(1)
        correction = corrections.get(counter[0], "").strip()
        counter[0] += 1
        return correction if correction else word

    return _UNCERTAIN_RE.sub(replacer, clean_text)


def _render_transcript_html(clean_text, corrections):
    # corrections dict must be fully populated before this is called (fix #3)
    gold = PALETTE["gold"]
    ink_mid = PALETTE["ink_mid"]
    border = PALETTE["border"]
    text_color = PALETTE["text"]

    parts = []
    last = 0
    idx = 0

    for m in _UNCERTAIN_RE.finditer(clean_text):
        if m.start() > last:
            # fix #1: escape plain text before embedding in HTML
            chunk = _html.escape(clean_text[last:m.start()]).replace("\n", "<br>")
            parts.append(chunk)

        word = m.group(1)
        correction = corrections.get(idx, "").strip()

        if correction and correction != word:
            parts.append(
                '<span style="color:' + gold + ';font-weight:600">'
                + _html.escape(correction) + "</span>"
            )
        else:
            parts.append(
                '<span style="background:' + ink_mid + ';color:' + gold + ";"
                "border:1px solid " + gold + ";border-radius:3px;"
                'padding:0 3px;font-weight:600" '
                'title="Uncertain — correct in the panel below">'
                "[" + _html.escape(word) + "?]</span>"
            )

        idx += 1
        last = m.end()

    if last < len(clean_text):
        # fix #1: escape trailing plain text too
        parts.append(_html.escape(clean_text[last:]).replace("\n", "<br>"))

    body = "".join(parts)
    return (
        '<div style="font-family:Georgia,serif;font-size:1.05rem;line-height:1.8;'
        "color:" + text_color + ";"
        'white-space:pre-wrap;padding:1rem 0">' + body + "</div>"
    )


# ── Session state defaults ────────────────────────────────────────────────────
for _key in ("transcript_raw", "transcript_clean", "transcript", "last_uploaded_file"):
    if _key not in st.session_state:
        st.session_state[_key] = None
if "corrections" not in st.session_state:
    st.session_state.corrections = {}

# ── File uploader ─────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Upload your voice memo",
    type=["m4a", "mp3", "wav"],
    help="Record on iPhone Voice Memos, email to yourself, then upload here.",
)

if uploaded is not None and uploaded.name != st.session_state.last_uploaded_file:
    st.session_state.last_uploaded_file = uploaded.name
    st.session_state.transcript_raw = None
    st.session_state.transcript_clean = None
    st.session_state.transcript = None
    st.session_state.corrections = {}

    file_bytes = uploaded.read()

    with st.spinner("Transcribing with Whisper..."):
        try:
            raw = _transcribe_audio(file_bytes, uploaded.name)
            st.session_state.transcript_raw = raw
        except Exception as e:
            st.error("Transcription failed: " + str(e))
            st.stop()

    with st.spinner("Cleaning transcript with Claude..."):
        try:
            clean = _clean_transcript(st.session_state.transcript_raw)
            st.session_state.transcript_clean = clean
            words = clean.split()
            st.session_state.working_title = (
                " ".join(words[:6]) + ("..." if len(words) > 6 else "")
            )
        except Exception as e:
            st.error("Cleaning pass failed: " + str(e))
            st.stop()

    st.rerun()

# ── Transcript display ────────────────────────────────────────────────────────
if st.session_state.transcript_clean:
    clean = st.session_state.transcript_clean
    uncertain_matches = list(_UNCERTAIN_RE.finditer(clean))

    # fix #3: build corrections from widget keys BEFORE rendering HTML so the
    # display always reflects the current run's widget values, not the prior run
    corrections = {}
    for i, m in enumerate(uncertain_matches):
        widget_key = "corr_" + str(i)
        if widget_key in st.session_state:
            corrections[i] = str(st.session_state[widget_key])
        else:
            corrections[i] = m.group(1)
    st.session_state.corrections = corrections

    st.markdown("### Transcript")
    st.markdown(
        _render_transcript_html(clean, corrections), unsafe_allow_html=True
    )
    st.markdown("")

    # ── Corrections panel ──────────────────────────────────────────────────────
    if uncertain_matches:
        n = len(uncertain_matches)
        label = "🔶 " + str(n) + " uncertain word" + ("s" if n != 1 else "") + " — correct below"
        with st.expander(label, expanded=True):
            st.markdown(
                "<p style='color:"
                + PALETTE["muted"]
                + ";font-size:0.85rem;margin-bottom:0.75rem'>"
                "These words were flagged by Claude as uncertain. "
                "Edit to correct; leave as-is to keep Claude's best guess.</p>",
                unsafe_allow_html=True,
            )
            for i, m in enumerate(uncertain_matches):
                word = m.group(1)
                col_lbl, col_inp = st.columns([1, 3])
                with col_lbl:
                    st.markdown(
                        "<div style='padding-top:6px;color:"
                        + PALETTE["gold"]
                        + ";font-weight:600'>[" + _html.escape(word) + "?]</div>",
                        unsafe_allow_html=True,
                    )
                with col_inp:
                    # fix #2: no manual rerun — Streamlit reruns naturally on
                    # widget commit (Enter / focus-out); widget key keeps value
                    # in session_state so the render above can read it next run
                    st.text_input(
                        "Correction for " + word,
                        value=corrections.get(i, word),
                        key="corr_" + str(i),
                        label_visibility="collapsed",
                    )
    else:
        st.success("No uncertain words — transcript looks clean.")

    # Always keep the final transcript in sync
    st.session_state.transcript = _apply_corrections(clean, st.session_state.corrections)

    st.markdown("---")

    muted = PALETTE["muted"]
    st.markdown(
        "<p style='color:" + muted + ";font-size:0.85rem'>"
        "Review the transcript above. Correct any amber-highlighted words, "
        "then begin the Development Session.</p>",
        unsafe_allow_html=True,
    )

    if st.button("Begin Development Session →"):
        st.switch_page("pages/develop.py")

else:
    st.markdown(
        "<p style='color:"
        + PALETTE["muted"]
        + "'>"
        "Upload a <code>.m4a</code>, <code>.mp3</code>, or <code>.wav</code> "
        "file above to begin.</p>",
        unsafe_allow_html=True,
    )
