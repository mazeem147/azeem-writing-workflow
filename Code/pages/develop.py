import os
import html as _html
import httpx
import streamlit as st
from ui import inject_css, render_sidebar, render_page_header, PALETTE
from components.voice_input import voice_input_widget

inject_css()
render_sidebar("develop")
render_page_header("develop", "💬 Develop", "Expand your Capture into a full position via AI-driven conversation.")

# ── Guard: must have a transcript from stage 1 ────────────────────────────────
if not st.session_state.get("transcript"):
    st.markdown(
        "<p style='color:" + PALETTE["muted"] + "'>"
        "No transcript found. Please complete the "
        "<strong>Transcribe</strong> stage first.</p>",
        unsafe_allow_html=True,
    )
    if st.button("← Go to Transcribe"):
        st.switch_page("pages/transcribe.py")
    st.stop()

# ── Session state defaults ────────────────────────────────────────────────────
if "conversation" not in st.session_state:
    st.session_state.conversation = []   # list of {"role": "ai"|"user", "text": str}
if "seeder_requested" not in st.session_state:
    st.session_state.seeder_requested = False
if "awaiting_ai" not in st.session_state:
    st.session_state.awaiting_ai = False
if "develop_response" not in st.session_state:
    st.session_state.develop_response = ""


# ── LLM helper ────────────────────────────────────────────────────────────────
def _call_claude(messages):
    """Send a messages list to claude-sonnet-4-5 via OpenRouter and return content string."""
    key = os.environ["OPENROUTER_API_KEY"]
    resp = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
        },
        json={
            "model": "anthropic/claude-sonnet-4-5",
            "messages": messages,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _seeder_messages(transcript):
    system = (
        "You are a thinking partner helping the writer deepen and develop their raw idea "
        "into a fully-formed position. Your job is to ask ONE precise, probing question "
        "that stems from a specific statement or gap in their transcript — never a generic "
        "question like 'Tell me more' or 'What do you think about this?'. "
        "Read the transcript carefully. Identify the most interesting claim, tension, "
        "or unexplained assumption. Ask a single question about that. "
        "Return ONLY the question — no preamble, no explanation."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": "Transcript:\n\n" + transcript},
    ]


def _followup_messages(transcript, conversation):
    system = (
        "You are a thinking partner helping the writer deepen their idea. "
        "You have been having a conversation with them about their transcript. "
        "Based on their latest answer and the full conversation so far, ask ONE follow-up question "
        "that probes deeper — targeting a specific claim they made, a gap they revealed, "
        "or an assumption they haven't examined. "
        "Avoid generic prompts. Return ONLY the question."
    )
    history = []
    for turn in conversation:
        role = "assistant" if turn["role"] == "ai" else "user"
        history.append({"role": role, "content": turn["text"]})
    return (
        [{"role": "system", "content": system}]
        + [{"role": "user", "content": "Original transcript:\n\n" + transcript}]
        + history
    )


# ── Trigger seeder question on first entry ────────────────────────────────────
if not st.session_state.seeder_requested:
    st.session_state.seeder_requested = True
    st.session_state.awaiting_ai = True

# ── Generate AI response if flagged ──────────────────────────────────────────
if st.session_state.awaiting_ai:
    transcript = st.session_state.transcript
    conversation = st.session_state.conversation

    ai_text = None
    with st.spinner("Claude is thinking..."):
        try:
            if not conversation:
                ai_text = _call_claude(_seeder_messages(transcript))
            else:
                ai_text = _call_claude(_followup_messages(transcript, conversation))
        except Exception as e:
            st.error("Claude call failed: " + str(e))
            st.session_state.awaiting_ai = False
            st.stop()

    if ai_text:
        st.session_state.conversation.append({"role": "ai", "text": ai_text})
    st.session_state.awaiting_ai = False
    st.rerun()

# ── Layout: two columns ───────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown(
        "<p style='color:" + PALETTE["gold"] + ";font-weight:600;"
        "font-family:Georgia,serif;font-size:1rem;margin-bottom:0.5rem'>"
        "Your Transcript</p>",
        unsafe_allow_html=True,
    )
    transcript_html = (
        '<div style="font-family:Georgia,serif;font-size:0.95rem;line-height:1.8;'
        "color:" + PALETTE["text"] + ";"
        "background:" + PALETTE["ink_mid"] + ";"
        "border:1px solid " + PALETTE["border"] + ";"
        "border-radius:6px;padding:1rem;"
        'overflow-y:auto;max-height:70vh;white-space:pre-wrap">'
        + _html.escape(st.session_state.transcript)
        + "</div>"
    )
    st.markdown(transcript_html, unsafe_allow_html=True)

with col_right:
    st.markdown(
        "<p style='color:" + PALETTE["gold"] + ";font-weight:600;"
        "font-family:Georgia,serif;font-size:1rem;margin-bottom:0.5rem'>"
        "Conversation</p>",
        unsafe_allow_html=True,
    )

    # Render conversation history oldest-first
    conversation = st.session_state.conversation
    if conversation:
        bubbles = []
        for turn in conversation:
            if turn["role"] == "ai":
                bg = PALETTE["ink_mid"]
                label_color = PALETTE["gold"]
                label = "Claude"
            else:
                bg = "#1a1826"
                label_color = PALETTE["muted"]
                label = "You"

            bubble = (
                "<div style='margin-bottom:1rem;padding:0.75rem 1rem;"
                "background:" + bg + ";"
                "border-radius:6px;border:1px solid " + PALETTE["border"] + "'>"
                "<p style='margin:0 0 0.25rem;font-size:0.75rem;color:"
                + label_color + ";font-weight:600;font-family:system-ui'>"
                + label + "</p>"
                "<p style='margin:0;font-family:Georgia,serif;font-size:0.95rem;"
                "line-height:1.7;color:" + PALETTE["text"] + "'>"
                + _html.escape(turn["text"]).replace("\n", "<br>")
                + "</p></div>"
            )
            bubbles.append(bubble)

        st.markdown(
            '<div style="max-height:55vh;overflow-y:auto;padding-right:0.25rem">'
            + "".join(bubbles)
            + "</div>",
            unsafe_allow_html=True,
        )

    # ── User input ────────────────────────────────────────────────────────────
    if conversation:  # only show input once first question is rendered
        # Mic button row — sits above the text area, right-aligned
        mic_row = st.columns([8, 1])
        with mic_row[0]:
            st.markdown(
                "<p style='color:" + PALETTE["muted"] + ";font-size:0.78rem;"
                "margin:0 0 2px'>Your response</p>",
                unsafe_allow_html=True,
            )
        with mic_row[1]:
            voice_input_widget("develop_response")

        # key= matches widget_key passed to voice_input_widget so Whisper
        # output is injected directly into this widget's session state.
        user_text = st.text_area(
            "Your response",
            placeholder="Type your answer, or click the mic to speak...",
            height=100,
            label_visibility="collapsed",
            key="develop_response",
        )

        if st.button("Send →", type="primary"):
            text_to_send = user_text.strip()
            if text_to_send:
                st.session_state.conversation.append(
                    {"role": "user", "text": text_to_send}
                )
                st.session_state.develop_response = ""
                st.session_state.awaiting_ai = True
                st.rerun()

# ── "Build the Plan" button — always visible ──────────────────────────────────
st.markdown("---")

col_hint, col_btn = st.columns([3, 1])
with col_hint:
    st.markdown(
        "<p style='color:" + PALETTE["muted"] + ";font-size:0.85rem;padding-top:6px'>"
        "When you've explored enough, carry the full conversation into the Plan stage.</p>",
        unsafe_allow_html=True,
    )
with col_btn:
    if st.button("Build the Plan →", type="primary"):
        st.session_state.brain_dump = list(st.session_state.conversation)
        st.switch_page("pages/plan.py")
