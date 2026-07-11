"""Regression tests for the Plan stage section operations (pages/plan.py).

Guards the "modify a widget-backed session_state key after the widget was
instantiated" bug class that has bitten this app three times (develop.py,
draft.py, and plan.py's "+ Add"). See WORKING_CONTEXT.md, Issue 05.

The original "+ Add" handler did, inside the button's if-block:

    if st.button("+ Add", key="add_section_btn"):
        _add_section(...)
        st.session_state["new_section_title"] = ""   # <-- after the text_input
        st.rerun()                                    #     widget was created

which raised:

    StreamlitAPIException: st.session_state.new_section_title cannot be modified
    after the widget with key new_section_title is instantiated.

The fix moved the append + clear into an on_click callback (callbacks run
before widgets are instantiated on the resulting rerun).

These tests drive pages/plan.py headlessly via Streamlit's AppTest and assert
on behaviour (no exception, correct state, key-type invariants). Pixel layout
(the second symptom — action buttons overflowing narrow columns) is not
observable via AppTest and is verified visually instead.

Run directly (no pytest needed):
    .venv/bin/python tests/test_plan_section_ops.py
Or under pytest, if installed:
    .venv/bin/python -m pytest tests/test_plan_section_ops.py
"""
import os
import sys

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_CODE_DIR = os.path.dirname(_TESTS_DIR)
if _CODE_DIR not in sys.path:
    sys.path.insert(0, _CODE_DIR)

from streamlit.testing.v1 import AppTest

# The sidebar uses st.page_link, which needs an st.navigation context that
# AppTest does not provide. It is not the code under test, so stub it to a
# no-op. plan.py does `from ui import render_sidebar`, which resolves from this
# already-imported (and now patched) module.
import ui  # noqa: E402
ui.render_sidebar = lambda *a, **k: None

_PLAN_PY = os.path.join(_CODE_DIR, "pages", "plan.py")


def _note(title, text):
    return {"text": text, "meta": {"title": title, "created": "2025-01-02"}}


def _fresh_app():
    """An AppTest for plan.py seeded with a 3-section plan (no LLM / ChromaDB).

    writing_plan is pre-populated so plan.py skips its generate-on-first-entry
    branch, so no network or embedding model is touched.
    """
    at = AppTest.from_file(_PLAN_PY, default_timeout=15)
    at.session_state["brain_dump"] = [
        {"role": "ai", "text": "What triggered this?"},
        {"role": "user", "text": "A tweet."},
    ]
    at.session_state["writing_plan"] = [
        {"title": "The Trigger", "bullets": ["Saw the tweet", "Felt the juice"]},
        {"title": "The Contrarian Take", "bullets": ["Everyone is wrong"]},
        {"title": "Where It Lands", "bullets": ["Open ending"]},
    ]
    at.session_state["content_notes"] = {
        "0": [_note("Note A", "past thinking about triggers")],
        "1": [_note("Note B", "a contrarian note")],
        "2": [],
    }
    at.session_state["pinned_notes"] = {"0": [0], "1": [], "2": []}
    at.session_state["section_expanded"] = {0: True, 1: True, 2: True}
    at.session_state["style_notes"] = []
    at.session_state["working_title"] = "Test piece"
    at.run()
    assert not at.exception, "seeded initial render raised: " + str(at.exception)
    return at


def _assert_key_invariants(at):
    """content_notes / pinned_notes use str keys; section_expanded uses int keys."""
    cn = at.session_state["content_notes"]
    pn = at.session_state["pinned_notes"]
    se = at.session_state["section_expanded"]
    assert all(isinstance(k, str) for k in cn), "content_notes keys must be str, got " + repr(list(cn))
    assert all(isinstance(k, str) for k in pn), "pinned_notes keys must be str, got " + repr(list(pn))
    assert all(isinstance(k, int) for k in se), "section_expanded keys must be int, got " + repr(list(se))


def test_add_section_no_exception_and_appends():
    """The core regression: '+ Add' must not raise and must append + clear input."""
    at = _fresh_app()
    n_before = len(at.session_state["writing_plan"])

    at.text_input(key="new_section_title").set_value("My New Section").run()
    at.button(key="add_section_btn").click().run()

    assert not at.exception, "clicking '+ Add' raised: " + str([e.value for e in at.exception])
    plan = at.session_state["writing_plan"]
    assert len(plan) == n_before + 1, "section was not appended"
    assert plan[-1]["title"] == "My New Section", "wrong title on appended section"
    assert plan[-1]["bullets"] == [], "appended section should start with no bullets"
    # The text input is cleared inside the callback (this is what used to crash).
    assert at.session_state["new_section_title"] == "", "input was not cleared after add"
    # New index must have consistent side-tables.
    idx = str(len(plan) - 1)
    assert at.session_state["content_notes"][idx] == []
    assert at.session_state["pinned_notes"][idx] == []
    assert at.session_state["section_expanded"][len(plan) - 1] is True
    _assert_key_invariants(at)


def test_add_section_blank_title_defaults():
    """Clicking '+ Add' with an empty input falls back to 'New Section'."""
    at = _fresh_app()
    n_before = len(at.session_state["writing_plan"])

    # Leave new_section_title empty.
    at.button(key="add_section_btn").click().run()

    assert not at.exception, "blank '+ Add' raised: " + str([e.value for e in at.exception])
    plan = at.session_state["writing_plan"]
    assert len(plan) == n_before + 1
    assert plan[-1]["title"] == "New Section"


def test_reorder_and_delete_reindex_no_exception():
    """Move a section down then delete one — the re-indexing paths must not raise
    and must keep the str/int key invariants."""
    at = _fresh_app()

    # Move section 0 ("The Trigger") down -> swaps with section 1.
    at.button(key="dn0").click().run()
    assert not at.exception, "reorder (↓) raised: " + str([e.value for e in at.exception])
    titles = [s["title"] for s in at.session_state["writing_plan"]]
    assert titles[:2] == ["The Contrarian Take", "The Trigger"], "reorder did not swap: " + repr(titles)
    _assert_key_invariants(at)

    # Delete section 0 -> re-indexes remaining sections down.
    at.button(key="dl0").click().run()
    assert not at.exception, "delete (✕) raised: " + str([e.value for e in at.exception])
    plan = at.session_state["writing_plan"]
    assert len(plan) == 2, "delete did not remove a section"
    # Side-tables must be re-indexed to a contiguous 0..n-1 range.
    assert set(at.session_state["content_notes"].keys()) == {"0", "1"}
    assert set(at.session_state["pinned_notes"].keys()) == {"0", "1"}
    assert set(at.session_state["section_expanded"].keys()) == {0, 1}
    _assert_key_invariants(at)


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
