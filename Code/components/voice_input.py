"""
Reusable voice/mic input component.

Usage:
    from components.voice_input import voice_input_widget

    # widget_key must match the key= passed to the associated st.text_area.
    voice_input_widget("develop_response")
    user_text = st.text_area("Response", key="develop_response", ...)

    # On submit, clear the widget key so the text_area resets:
    if st.button("Send"):
        text = st.session_state.get("develop_response", "").strip()
        st.session_state["develop_response"] = ""
        ...
"""

import hashlib
import io
import os

import streamlit as st
from audio_recorder_streamlit import audio_recorder


def voice_input_widget(widget_key: str) -> None:
    """
    Renders a mic button inline. When the user records and stops, audio is
    sent to Whisper and the result is written directly into
    st.session_state[widget_key] — which must match the key= of the
    associated st.text_area so Streamlit picks it up on the next rerun.

    widget_key: the key= value of the paired st.text_area.
    """
    processed_key = "_voice_hash_" + widget_key

    audio_bytes = audio_recorder(
        text="",
        recording_color="#c9a96e",   # gold — matches design system
        neutral_color="#9b9690",     # muted
        icon_name="microphone",
        icon_size="lg",
        pause_threshold=2.0,
        key="recorder_" + widget_key,
    )

    if audio_bytes is not None:
        audio_hash = hashlib.md5(audio_bytes).hexdigest()
        if st.session_state.get(processed_key) != audio_hash:
            # New recording — transcribe once, then mark as processed.
            st.session_state[processed_key] = audio_hash
            _transcribe_and_store(audio_bytes, widget_key)


def _transcribe_and_store(audio_bytes: bytes, draft_key: str) -> None:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    buf = io.BytesIO(audio_bytes)
    buf.name = "recording.wav"
    with st.spinner("Transcribing..."):
        try:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=buf,
                # No language specified — Whisper auto-detects Urdu/English mix
            )
            st.session_state[draft_key] = result.text.strip()
        except Exception as e:
            st.error("Transcription failed: " + str(e))
    st.rerun()
