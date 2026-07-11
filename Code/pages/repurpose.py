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
    "Tweet Thread, LinkedIn Article, and LinkedIn Feed Post, generated from your Draft.",
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


_MD_BOLD_RE   = re.compile(r"\*\*(.+?)\*\*")
_MD_HEADER_RE = re.compile(r"^#{1,6}\s*", flags=re.MULTILINE)


def _strip_markdown(text):
    """LinkedIn's article editor and feed compose box render markdown syntax as
    literal characters, not formatting. The prompt says not to use it, but the
    model emits it anyway, so strip **bold** and # headers here."""
    text = _MD_BOLD_RE.sub(r"\1", text)
    text = _MD_HEADER_RE.sub("", text)
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
        "- Final tweet: a hook that drives the reader to the LinkedIn Article. Reference that "
        "the full piece is there. Make them want to go.\n"
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


# ── LinkedIn Article generation ────────────────────────────────────────────────
def _generate_linkedin_article(full_draft):
    system = (
        "You are adapting a long-form Draft into a LinkedIn Article — the piece's primary "
        "publishable form, posted via LinkedIn's native article editor, where it becomes a "
        "permanent, Google-indexed portfolio artifact on the profile.\n\n"
        "Rules:\n"
        "- 600 to 900 words.\n"
        "- Deliver the complete argument in full. This is not a summary or a teaser, it is "
        "the whole piece adapted for LinkedIn's article format.\n"
        "- Preserve every claim and the structure of the Draft; tighten or expand as needed "
        "to land in the word range without dropping any part of the argument.\n"
        "- Write in the same voice as the Draft: analytical and personal in the same sentence, "
        "thinks out loud, ends open.\n"
        "- Use short paragraphs (2-4 sentences). No markdown headers, no bullet-point lists, "
        "no bold/italic syntax — LinkedIn's article editor does not render markdown.\n"
        "- Do not reference any other publishing destination. This LinkedIn Article is the "
        "whole piece; it lives here and nowhere else.\n\n"
        "Return only the article text. No explanation, no preamble, no title line."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": "Draft to adapt into a LinkedIn Article:\n\n" + full_draft},
    ]
    return _strip_markdown(_strip_em_dashes(_call_claude(messages)))


# ── LinkedIn Feed Post generation ──────────────────────────────────────────────
def _generate_linkedin_feed_post(full_draft):
    system = (
        "You are writing a LinkedIn Feed Post to accompany a companion LinkedIn Article that "
        "carries the full argument. The Feed Post's only job is to earn comments in the first "
        "hour after posting — algorithmic amplification depends on early engagement.\n\n"
        "Rules:\n"
        "- 150 to 200 words.\n"
        "- Open with a direct hook in the first line. No throat-clearing, no restating the "
        "article's introduction, no title or headline line above the hook.\n"
        "- Surface the core provocation — the single claim most likely to make someone stop "
        "scrolling.\n"
        "- No markdown syntax anywhere (no **bold**, no # headers) — the LinkedIn feed renders "
        "asterisks and hashes as literal characters, not formatting.\n"
        "- End on a question or a strong opinion designed to invite replies. Not a bare "
        "'thoughts?' — actually provoke a response.\n"
        "- Reference that the full argument lives in the LinkedIn Article (e.g. 'I go deeper "
        "in the article below' or similar). The Feed Post is a hook toward it, not a "
        "replacement for it.\n"
        "- Direct tone. Not corporate. Not buzzword-heavy.\n"
        "- No emojis unless they are essential.\n"
        "- No hashtag spam.\n"
        "- Write in the same voice as the article.\n\n"
        "Return only the post text. No explanation, no preamble."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": "Draft the companion LinkedIn Article is based on:\n\n" + full_draft},
    ]
    return _strip_markdown(_strip_em_dashes(_call_claude(messages)))


def _word_count(text):
    return len(text.split())


# ── Generation orchestration ────────────────────────────────────────────────
def _validate_tweet_count(tweets):
    """Warning string if the thread is under the expected 8-12 range, else None."""
    if len(tweets) < 8:
        return (
            "Only " + str(len(tweets)) + " tweets generated (expected 8-12). "
            "Use ↺ Regenerate Thread to try again."
        )
    return None


def _word_range_validator(label, regen_label, lo, hi):
    """Build a validator that returns a warning if a text output falls outside
    [lo, hi] words, else None."""
    def validate(text):
        wc = _word_count(text)
        if wc < lo or wc > hi:
            return (
                label + " is " + str(wc) + " words (expected "
                + str(lo) + "-" + str(hi) + "). Use ↺ " + regen_label + " to try again."
            )
        return None
    return validate


def _generate_output(full_draft, state_key, label, generate_fn, validate):
    """Generate one output into st.session_state[state_key] if it is absent.

    generate_fn(full_draft) -> result; validate(result) -> warning str or None.
    A validation warning is persisted into st.session_state.gen_warnings rather
    than shown with st.warning() here, because this phase ends in st.rerun(): a
    warning emitted now would flash and vanish before the user sees it. The
    display phase (which does not rerun) renders the persisted warning.

    A no-op once the output is present, so the three calls each generate one
    output per rerun and preserve the sequential "output appears" UX."""
    if st.session_state[state_key] is not None:
        return
    result = None
    with st.spinner("Generating " + label + "…"):
        try:
            result = generate_fn(full_draft)
        except Exception as exc:
            st.error(label + " generation failed: " + str(exc))
            st.stop()
    if result is None:
        st.stop()
    st.session_state.gen_warnings[state_key] = validate(result)
    st.session_state[state_key] = result
    st.rerun()


# ── Session state defaults ─────────────────────────────────────────────────────
for _key in ("tweet_thread", "linkedin_article", "linkedin_feed_post"):
    if _key not in st.session_state:
        st.session_state[_key] = None
if "gen_warnings" not in st.session_state:
    st.session_state.gen_warnings = {}

full_draft = "\n\n".join(st.session_state.draft_sections)

# ── Generation phase ───────────────────────────────────────────────────────────
# One session-state-gated phase per output; each generates then reruns, so the
# outputs appear sequentially. See _generate_output for the warning handling.
_generate_output(
    full_draft, "tweet_thread", "Tweet Thread",
    _generate_tweet_thread, _validate_tweet_count,
)
_generate_output(
    full_draft, "linkedin_article", "LinkedIn Article",
    _generate_linkedin_article,
    _word_range_validator("LinkedIn Article", "Regenerate Article", 600, 900),
)
_generate_output(
    full_draft, "linkedin_feed_post", "LinkedIn Feed Post",
    _generate_linkedin_feed_post,
    _word_range_validator("LinkedIn Feed Post", "Regenerate Feed Post", 150, 200),
)

# ── Single-block text output renderer (LinkedIn Article / Feed Post) ─────────
def _render_text_output(state_key, text, regen_label, regen_key):
    """Render any persisted validation warning, a word count, the copyable text
    block, and a regenerate button that clears only this output's state."""
    muted = PALETTE["muted"]
    warning = st.session_state.gen_warnings.get(state_key)
    if warning:
        st.warning(warning)
    st.markdown(
        "<p style='color:" + muted + ";font-size:0.85rem;margin-bottom:1rem'>"
        + str(_word_count(text)) + " words · Copy the full block below</p>",
        unsafe_allow_html=True,
    )
    st.code(text, language=None)
    st.markdown("<div style='margin-top:0.5rem'></div>", unsafe_allow_html=True)
    _, regen_col = st.columns([3, 1])
    with regen_col:
        if st.button("↺ " + regen_label, key=regen_key):
            st.session_state[state_key] = None
            st.session_state.gen_warnings.pop(state_key, None)
            st.rerun()


# ── Display ────────────────────────────────────────────────────────────────────
tweets    = st.session_state.tweet_thread
article   = st.session_state.linkedin_article
feed_post = st.session_state.linkedin_feed_post

gold  = PALETTE["gold"]
muted = PALETTE["muted"]

tab_thread, tab_article, tab_feed = st.tabs(
    ["🐦 Tweet Thread", "📰 LinkedIn Article", "💼 LinkedIn Feed Post"]
)

with tab_thread:
    thread_warning = st.session_state.gen_warnings.get("tweet_thread")
    if thread_warning:
        st.warning(thread_warning)
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
            st.session_state.gen_warnings.pop("tweet_thread", None)
            st.rerun()

with tab_article:
    _render_text_output("linkedin_article", article, "Regenerate Article", "regen_article")

with tab_feed:
    _render_text_output("linkedin_feed_post", feed_post, "Regenerate Feed Post", "regen_feed_post")

# ── Bottom bar ─────────────────────────────────────────────────────────────────
st.markdown("---")

hint_col, btn_col = st.columns([3, 1])
with hint_col:
    st.markdown(
        "<p style='color:" + muted + ";font-size:0.85rem;padding-top:6px'>"
        "Review all three tabs before marking as published.</p>",
        unsafe_allow_html=True,
    )
with btn_col:
    if st.button("Mark as Published →", type="primary"):
        st.switch_page("pages/publish.py")
