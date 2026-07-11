"""Tests for the Repurposed Content stage (pages/repurpose.py), Issue 10.

Covers the swap from the single Substack-teaser "LinkedIn Post" (Issue 07) to
two LinkedIn-native outputs: LinkedIn Article (600-900 words, full argument)
and LinkedIn Feed Post (150-200 words, hooks to the Article). Tweet Thread is
retained, but its closing-hook system prompt now points at the LinkedIn
Article instead of Substack.

These tests drive pages/repurpose.py headlessly via Streamlit's AppTest, with
httpx.post monkeypatched to a fake OpenRouter endpoint so no network or API
key is required. The fake inspects each outgoing system prompt for a marker
phrase unique to one of the three generation calls (Tweet Thread / LinkedIn
Article / LinkedIn Feed Post) and returns a canned, word-count-controlled
response for it — this lets tests assert on both the generated artifacts
*and* the prompts actually sent (e.g. "Substack" must never appear).

Run directly (no pytest needed):
    .venv/bin/python tests/test_repurpose_content.py
Or under pytest, if installed:
    .venv/bin/python -m pytest tests/test_repurpose_content.py
"""
import json
import os
import sys

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_CODE_DIR = os.path.dirname(_TESTS_DIR)
if _CODE_DIR not in sys.path:
    sys.path.insert(0, _CODE_DIR)

import httpx  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

# The sidebar uses st.page_link, which needs an st.navigation context that
# AppTest does not provide. Stub it to a no-op, same idiom as
# test_plan_section_ops.py.
import ui  # noqa: E402
ui.render_sidebar = lambda *a, **k: None

os.environ.setdefault("OPENROUTER_API_KEY", "test-key")

_REPURPOSE_PY = os.path.join(_CODE_DIR, "pages", "repurpose.py")

# Marker phrases unique to each generation call's system prompt.
_TWEET_MARKER   = "Twitter's attention structure"
_ARTICLE_MARKER = "LinkedIn's native article editor"
_FEED_MARKER    = "earn comments in the first hour"


def _lorem(n_words):
    return " ".join(["word"] * n_words)


def _tweets_json(n=10, closing_mentions_article=True):
    tweets = ["Tweet number " + str(i) + " with a real claim in it." for i in range(1, n)]
    closing = "Full argument's in the LinkedIn Article now, go read it."
    if not closing_mentions_article:
        closing = "That's the thread."
    tweets.append(closing)
    return json.dumps(tweets)


class _FakeResponse:
    def __init__(self, content):
        self._content = content

    def raise_for_status(self):
        pass

    def json(self):
        return {"choices": [{"message": {"content": self._content}}]}


def _make_fake_post(calls, responses):
    """responses: dict of marker -> content (or list of contents, popped in order)."""
    remaining = {k: (list(v) if isinstance(v, list) else [v]) for k, v in responses.items()}

    def fake_post(url, headers=None, json=None, timeout=None):  # noqa: A002 - matches httpx.post signature
        calls.append(json)
        system = json["messages"][0]["content"]
        for marker, queue in remaining.items():
            if marker in system:
                if not queue:
                    raise AssertionError("No more canned responses queued for marker: " + marker)
                return _FakeResponse(queue.pop(0))
        raise AssertionError("Unrecognized request, no marker matched: " + system[:120])

    return fake_post


def _fresh_app():
    at = AppTest.from_file(_REPURPOSE_PY, default_timeout=15)
    at.session_state["draft_approved"] = True
    at.session_state["draft_sections"] = [
        "Section one of the draft, making the opening claim.",
        "Section two, developing the argument further.",
        "Section three, the closing thought.",
    ]
    return at


def _default_responses():
    return {
        _TWEET_MARKER: _tweets_json(),
        _ARTICLE_MARKER: _lorem(750),
        _FEED_MARKER: _lorem(180),
    }


def test_full_generation_produces_three_outputs_and_no_substack():
    calls = []
    real_post = httpx.post
    httpx.post = _make_fake_post(calls, _default_responses())
    try:
        at = _fresh_app()
        at.run()
    finally:
        httpx.post = real_post

    assert not at.exception, "generation flow raised: " + str([e.value for e in at.exception])

    tweets = at.session_state["tweet_thread"]
    assert isinstance(tweets, list) and 8 <= len(tweets) <= 12

    article = at.session_state["linkedin_article"]
    article_words = len(article.split())
    assert 600 <= article_words <= 900, "article word count out of range: " + str(article_words)

    feed_post = at.session_state["linkedin_feed_post"]
    feed_words = len(feed_post.split())
    assert 150 <= feed_words <= 200, "feed post word count out of range: " + str(feed_words)

    assert "linkedin_post" not in at.session_state, "old Substack-teaser key must be gone"

    # In-range outputs must leave no validation warning behind.
    warnings_by_key = at.session_state["gen_warnings"]
    assert all(v is None for v in warnings_by_key.values()), (
        "in-range outputs should not warn: " + repr(warnings_by_key)
    )
    assert not at.warning, "no warnings should render for in-range outputs"

    # No request or generated artifact should ever mention Substack.
    assert len(calls) == 3, "expected exactly 3 generation calls, got " + str(len(calls))
    for call in calls:
        system = call["messages"][0]["content"]
        assert "Substack" not in system, "system prompt still mentions Substack: " + system[:200]
    assert "Substack" not in article
    assert "Substack" not in feed_post


def test_tweet_thread_prompt_hooks_to_linkedin_article_not_substack():
    calls = []
    real_post = httpx.post
    httpx.post = _make_fake_post(calls, _default_responses())
    try:
        at = _fresh_app()
        at.run()
    finally:
        httpx.post = real_post

    assert not at.exception
    tweet_system = next(
        c["messages"][0]["content"] for c in calls if _TWEET_MARKER in c["messages"][0]["content"]
    )
    assert "LinkedIn Article" in tweet_system
    assert "Substack" not in tweet_system


def test_tabs_labeled_correctly_and_teaser_ui_removed():
    calls = []
    real_post = httpx.post
    httpx.post = _make_fake_post(calls, _default_responses())
    try:
        at = _fresh_app()
        at.run()
    finally:
        httpx.post = real_post

    assert not at.exception
    tab_labels = [t.label for t in at.tabs]
    assert tab_labels == ["🐦 Tweet Thread", "📰 LinkedIn Article", "💼 LinkedIn Feed Post"]

    button_labels = [b.label for b in at.button]
    assert "↺ Regenerate Article" in button_labels
    assert "↺ Regenerate Feed Post" in button_labels
    assert "↺ Regenerate Post" not in button_labels, "old teaser regenerate button must be gone"
    assert "Mark as Published →" in button_labels

    header_markdowns = " ".join(m.value for m in at.markdown)
    assert "Substack" not in header_markdowns
    assert "LinkedIn Article" in header_markdowns
    assert "LinkedIn Feed Post" in header_markdowns


def test_regenerate_article_only_replaces_article():
    calls = []
    responses = _default_responses()
    # Queue a second, distinct article for the regenerate click.
    responses[_ARTICLE_MARKER] = [_lorem(750), _lorem(820)]
    real_post = httpx.post
    httpx.post = _make_fake_post(calls, responses)
    try:
        at = _fresh_app()
        at.run()
        tweets_before = at.session_state["tweet_thread"]
        feed_before = at.session_state["linkedin_feed_post"]
        article_before = at.session_state["linkedin_article"]

        at.button(key="regen_article").click().run()
    finally:
        httpx.post = real_post

    assert not at.exception, "regenerate raised: " + str([e.value for e in at.exception])
    assert at.session_state["linkedin_article"] != article_before
    assert len(at.session_state["linkedin_article"].split()) == 820
    assert at.session_state["tweet_thread"] == tweets_before, "regenerating article touched tweet thread"
    assert at.session_state["linkedin_feed_post"] == feed_before, "regenerating article touched feed post"


def test_out_of_range_word_counts_surface_persistent_warnings():
    """Out-of-range word counts must warn the user. The warning is persisted into
    gen_warnings during generation and rendered in the display phase, so it survives
    the st.rerun() that ends generation (a bare st.warning() in the generation phase
    would flash and vanish before the user sees it)."""
    calls = []
    responses = {
        _TWEET_MARKER: _tweets_json(),
        _ARTICLE_MARKER: _lorem(400),   # too short: expected 600-900
        _FEED_MARKER: _lorem(250),      # too long: expected 150-200
    }
    real_post = httpx.post
    httpx.post = _make_fake_post(calls, responses)
    try:
        at = _fresh_app()
        at.run()
    finally:
        httpx.post = real_post

    assert not at.exception, "out-of-range branch raised: " + str([e.value for e in at.exception])
    # State is still populated despite being out of range.
    assert len(at.session_state["linkedin_article"].split()) == 400
    assert len(at.session_state["linkedin_feed_post"].split()) == 250
    # The warnings are persisted, not flashed away by the rerun.
    assert at.session_state["gen_warnings"]["linkedin_article"] is not None
    assert at.session_state["gen_warnings"]["linkedin_feed_post"] is not None
    # And they actually render in the final tree.
    warnings = " ".join(w.value for w in at.warning)
    assert "600-900" in warnings, "article out-of-range warning not surfaced: " + warnings
    assert "150-200" in warnings, "feed post out-of-range warning not surfaced: " + warnings


def test_short_tweet_thread_surfaces_persistent_warning():
    """The Tweet Thread under-8 warning uses the same persist-across-rerun path as the
    new outputs, so it now surfaces too (it previously flashed and vanished). The Tweet
    Thread output itself is unchanged."""
    calls = []
    responses = {
        _TWEET_MARKER: _tweets_json(n=5),   # 5 tweets: under the expected 8-12
        _ARTICLE_MARKER: _lorem(750),
        _FEED_MARKER: _lorem(180),
    }
    real_post = httpx.post
    httpx.post = _make_fake_post(calls, responses)
    try:
        at = _fresh_app()
        at.run()
    finally:
        httpx.post = real_post

    assert not at.exception
    assert len(at.session_state["tweet_thread"]) == 5
    assert at.session_state["gen_warnings"]["tweet_thread"] is not None
    warnings = " ".join(w.value for w in at.warning)
    assert "expected 8-12" in warnings, "short-thread warning not surfaced: " + warnings


def test_markdown_bold_and_headers_stripped_from_article_and_feed_post():
    """The model is told not to use markdown (LinkedIn renders ** and # literally),
    but doesn't always comply. _strip_markdown is a defensive post-process, same
    idiom as _strip_em_dashes for the Voice rules."""
    calls = []
    responses = {
        _TWEET_MARKER: _tweets_json(),
        _ARTICLE_MARKER: "# A Bold Headline\n\nThis has **bold text** in it. " + _lorem(740),
        _FEED_MARKER: "**Provocative Opener**\n\nRest of the post. " + _lorem(190),
    }
    real_post = httpx.post
    httpx.post = _make_fake_post(calls, responses)
    try:
        at = _fresh_app()
        at.run()
    finally:
        httpx.post = real_post

    assert not at.exception
    article = at.session_state["linkedin_article"]
    feed_post = at.session_state["linkedin_feed_post"]
    assert "**" not in article and "**" not in feed_post
    assert not article.lstrip().startswith("#")
    assert not feed_post.lstrip().startswith("#")
    assert "A Bold Headline" in article, "header text should survive, only the markers stripped"
    assert "bold text" in article
    assert "Provocative Opener" in feed_post


def _main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failures = 0
    for t in tests:
        try:
            t()
            print("PASS  " + t.__name__)
        except AssertionError as exc:
            failures += 1
            print("FAIL  " + t.__name__ + "\n      " + str(exc))
        except Exception as exc:  # noqa: BLE001 - surface unexpected errors too
            failures += 1
            print("ERROR " + t.__name__ + "\n      " + type(exc).__name__ + ": " + str(exc))
    print("\n" + str(len(tests) - failures) + "/" + str(len(tests)) + " passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_main())
