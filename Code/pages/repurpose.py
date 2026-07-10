import os
import re
import json
import httpx
import streamlit as st
from ui import inject_css, render_sidebar, render_page_header, PALETTE

inject_css()
render_sidebar("publish")
render_page_header(
    "publish",
    "🔁 Repurposed Content",
    "Tweet Thread + LinkedIn Post, generated from your Draft.",
)

# ── Guard ──────────────────────────────────────────────────────────────────────
_guard_muted = PALETTE["muted"]
if not st.session_state.get("draft_approved"):
    st.markdown(
        "<p style='color:" + _guard_muted + "'>Draft not yet approved. "
        "Please complete the <strong>Draft</strong> stage first.</p>",
        unsafe_allow_html=True,
    )
    if st.button("← Go to Draft"):
        st.switch_page("pages/draft.py")
    st.stop()


# ── LLM helper ────────────────────────────────────────────────────────────────
def _call_claude(messages, timeout=90):
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


# ── Tweet Thread generation ────────────────────────────────────────────────────
def _generate_tweet_thread(full_draft):
    system = (
        "You are a writer who knows how Twitter works. Your job is to turn a long-form article "
        "into a native Tweet Thread — not a summary, not a compressed version, but a rewrite "
        "for Twitter's attention structure.\n\n"
        "Rules:\n"
        "- 8 to 12 tweets total.\n"
        "- First tweet: a provocation that earns attention. Not the article's introduction. "
        "Not a summary of what you're about to say. A claim, a question, or an observation "
        "that makes someone stop scrolling.\n"
        "- Each tweet must be standalone-readable. A reader who sees only tweet 5 of 10 should "
        "get value from it, even without context.\n"
        "- Final tweet: a hook that drives the reader to Substack. Reference that the full "
        "piece is there. Make them want to go.\n"
        "- Every tweet must be under 280 characters.\n"
        "- Do not number the tweets.\n"
        "- Do not use hashtags unless they are essential to the meaning.\n"
        "- Write in the same voice as the article — direct, analytical, personal where relevant.\n\n"
        "Return a JSON array of strings. Each string is one tweet. "
        "Example: [\"Tweet 1 text.\", \"Tweet 2 text.\", ...]"
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": "Article to rewrite as a Tweet Thread:\n\n" + full_draft},
    ]
    raw = _call_claude(messages)
    # Strip code fences
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    try:
        tweets = json.loads(raw)
    except Exception:
        # Fallback: split by newline, treat non-empty lines as tweets
        tweets = [line.strip() for line in raw.splitlines() if line.strip()]
    # Keep only non-empty tweets, strip em dashes, cap at 12
    tweets = [_strip_em_dashes(t) for t in tweets if t][:12]
    return tweets


# ── LinkedIn Post generation ───────────────────────────────────────────────────
def _generate_linkedin_post(full_draft):
    system = (
        "You are writing a LinkedIn post that drives traffic to a Substack article.\n\n"
        "Rules:\n"
        "- 3 to 5 sentences.\n"
        "- Direct tone. Not corporate. Not buzzword-heavy.\n"
        "- Surface the core provocation of the article — the thing that makes it worth reading.\n"
        "- End with a sentence that drives to Substack. Something like 'Full piece on Substack.' "
        "or 'I wrote about this in full — link in bio.' Keep it natural, not salesy.\n"
        "- No emojis unless they are essential.\n"
        "- No hashtag spam.\n"
        "- Write in the same voice as the article.\n\n"
        "Return only the post text. No explanation, no preamble."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": "Article:\n\n" + full_draft},
    ]
    return _strip_em_dashes(_call_claude(messages))


# ── Session state defaults ─────────────────────────────────────────────────────
if "tweet_thread" not in st.session_state:
    st.session_state.tweet_thread = None
if "linkedin_post" not in st.session_state:
    st.session_state.linkedin_post = None

full_draft = "\n\n".join(st.session_state.draft_sections)

# ── Generation phase ───────────────────────────────────────────────────────────
if st.session_state.tweet_thread is None:
    tweets = None
    with st.spinner("Generating Tweet Thread…"):
        try:
            tweets = _generate_tweet_thread(full_draft)
        except Exception as exc:
            st.error("Tweet Thread generation failed: " + str(exc))
            st.stop()
    if tweets is None:
        st.stop()
    if len(tweets) < 8:
        st.warning(
            "Only " + str(len(tweets)) + " tweets generated (expected 8-12). "
            "Use ↺ Regenerate Thread to try again."
        )
    st.session_state.tweet_thread = tweets
    st.rerun()

if st.session_state.linkedin_post is None:
    post = None
    with st.spinner("Generating LinkedIn Post…"):
        try:
            post = _generate_linkedin_post(full_draft)
        except Exception as exc:
            st.error("LinkedIn Post generation failed: " + str(exc))
            st.stop()
    if post is None:
        st.stop()
    st.session_state.linkedin_post = post
    st.rerun()

# ── Display ────────────────────────────────────────────────────────────────────
tweets = st.session_state.tweet_thread
post   = st.session_state.linkedin_post

gold  = PALETTE["gold"]
muted = PALETTE["muted"]

tab_thread, tab_linkedin = st.tabs(["🐦 Tweet Thread", "💼 LinkedIn Post"])

with tab_thread:
    thread_count = str(len(tweets))
    st.markdown(
        "<p style='color:" + muted + ";font-size:0.85rem;margin-bottom:1rem'>"
        + thread_count + " tweets · Each has a copy button in the top-right corner</p>",
        unsafe_allow_html=True,
    )
    for i, tweet in enumerate(tweets):
        tweet_num  = str(i + 1)
        char_count = len(tweet)
        char_str   = str(char_count)
        char_color = gold if char_count <= 280 else PALETTE["error"]

        st.markdown(
            "<p style='color:" + muted + ";font-size:0.75rem;font-weight:600;"
            "letter-spacing:0.05em;margin:0.75rem 0 2px'>"
            "TWEET " + tweet_num
            + " · <span style='color:" + char_color + "'>"
            + char_str + "/280</span></p>",
            unsafe_allow_html=True,
        )
        st.code(tweet, language=None)

    st.markdown("<div style='margin-top:0.5rem'></div>", unsafe_allow_html=True)
    _, regen_col = st.columns([3, 1])
    with regen_col:
        if st.button("↺ Regenerate Thread", key="regen_thread"):
            st.session_state.tweet_thread = None
            st.rerun()

with tab_linkedin:
    st.markdown(
        "<p style='color:" + muted + ";font-size:0.85rem;margin-bottom:1rem'>"
        "Copy the full block below</p>",
        unsafe_allow_html=True,
    )
    st.code(post, language=None)

    st.markdown("<div style='margin-top:0.5rem'></div>", unsafe_allow_html=True)
    _, regen_col = st.columns([3, 1])
    with regen_col:
        if st.button("↺ Regenerate Post", key="regen_linkedin"):
            st.session_state.linkedin_post = None
            st.rerun()

# ── Bottom bar ─────────────────────────────────────────────────────────────────
st.markdown("---")

hint_col, btn_col = st.columns([3, 1])
with hint_col:
    st.markdown(
        "<p style='color:" + muted + ";font-size:0.85rem;padding-top:6px'>"
        "Review both tabs before marking as published.</p>",
        unsafe_allow_html=True,
    )
with btn_col:
    if st.button("Mark as Published →", type="primary"):
        st.switch_page("pages/publish.py")
