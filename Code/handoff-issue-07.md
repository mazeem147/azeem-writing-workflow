# Handoff: Azeem's Writing Workflow — ready to build Issue 07

**Session date:** 2026-07-09
**Next task:** Implement Issue 07 — Repurposed Content (Tweet Thread + LinkedIn Post generation from approved Draft)

---

## What was done this session

### Issue 06 (completed this session)
Draft stage fully implemented and code-reviewed.

**Files created/changed:**
- `pages/draft.py` — full implementation: Style Fingerprint extraction from Style Notes, sequential section-by-section Draft generation, section card renderer, inline revision form with mic input, "Approve Draft →" navigation
- `WORKING_CONTEXT.md` — updated with Issue 06 build log

**Key decisions:**
- Style Fingerprint extracted via Claude (sonnet-4-5 via OpenRouter) from `st.session_state.style_notes` before generation begins; stored in `st.session_state.style_fingerprint`; used in every section prompt
- Voice rules read from `skills/writing-voice/SKILL.md` at module load time using `__file__` walk (same path resolution pattern as ChromaDB in plan.py); included verbatim in every section generation prompt
- Section generation is progressive: on each rerun, already-completed sections are rendered, then the next section is generated and appended to `draft_sections`, then `st.rerun()`. User sees sections appear one by one.
- Revision uses an **inline form** (not `@st.dialog`): `voice_input_widget` calls `st.rerun()` internally after transcription, which would close a dialog before the user sees the transcribed text. Inline form persists via `st.session_state.modal_section_idx`.
- `modal_section_idx`: int (section index) or None. "Revise ✦" sets it; "Cancel" or "Regenerate" clears it to None. Only one section's form is open at a time.
- `revision_feedback` key: shared between `voice_input_widget("revision_feedback")` and `st.text_area(key="revision_feedback")` — same pattern as `develop_response` in develop.py.
- "Approve Draft →" navigates to `pages/publish.py` (placeholder until Issue 08).

**Bug caught in code review and fixed:**
- `IndexError` when user navigates back to Plan stage, shrinks the plan, then returns to Draft: `draft_sections` retained stale longer list but `plan` was shorter. Fixed by truncating `draft_sections` to `len(plan)` before the rendering loop.

**Session state produced:**
- `st.session_state.style_fingerprint` — string describing rhetorical patterns (empty string if no style_notes)
- `st.session_state.draft_sections` — `list[str]`, one prose paragraph block per Writing Plan section

**Session state consumed:** `st.session_state.writing_plan`, `st.session_state.style_notes`

---

## Repo layout

```
Azeem's Writing Workflow/
  CONTEXT.md
  PRD.md
  issues/
    01-app-scaffold.md              ✅ done
    02-transcribe-stage.md          ✅ done
    03-develop-stage.md             ✅ done
    04-voice-input.md               ✅ done
    05-plan-stage.md                ✅ done
    06-draft-stage.md               ✅ done (this session)
    07-repurposed-content.md        ← NEXT
    08-publish-stage.md
  Code/
    app.py                          ← entry point
    ui.py                           ← PALETTE, inject_css(), render_sidebar(), render_page_header()
    components/
      __init__.py
      voice_input.py                ✅ reusable mic component
    pages/
      transcribe.py                 ✅ full implementation
      develop.py                    ✅ full implementation + mic
      plan.py                       ✅ full implementation
      draft.py                      ✅ full implementation (this session)
      publish.py                    ← placeholder (Issue 08)
    requirements.txt
    .env.example
    .env                            ← real keys (not committed)
    WORKING_CONTEXT.md              ← full build log of all issues
    handoff-issue-07.md             ← this file
```

GitHub: https://github.com/mazeem147/azeem-writing-workflow

---

## Session state entering Issue 07

The Repurposed Content stage will receive:

- `st.session_state.draft_sections` — `list[str]`, one prose block per Writing Plan section. The full article is `"\n\n".join(st.session_state.draft_sections)`.

- `st.session_state.writing_plan` — `list[dict]` where each dict is:
  ```python
  {"title": str, "bullets": list[str], "pinned_notes": list[str]}
  ```

- `st.session_state.working_title` — the article's working title (set in Transcribe stage from first 6 words of transcript)

---

## Issue 07 spec summary

Full spec: `issues/07-repurposed-content.md` — read this before implementing.

**What to build:**
1. **Tweet Thread generation** — one Claude call from the full Draft. 8-12 tweets written natively for Twitter's attention structure: strong opener (provocation, not article intro), each tweet standalone-readable, closes with a hook to Substack. NOT a compressed version of the article — a rewrite for a different medium.
2. **LinkedIn Post generation** — one Claude call from the full Draft. 3-5 sentences, direct tone, surfaces the core provocation, drives to Substack.
3. **Tabs UI** — Tweet Thread and LinkedIn Post shown in separate tabs so the screen doesn't feel cluttered.
4. **"Continue to Publish →"** — navigates to `pages/publish.py` after user has reviewed both.

**Session state produced:**
- `st.session_state.tweet_thread` — `list[str]`, 8-12 tweet strings each ≤ 280 characters
- `st.session_state.linkedin_post` — `str`, 3-5 sentence LinkedIn post

---

## Patterns to follow

### LLM calls (OpenRouter)
```python
import httpx, os
resp = httpx.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
             "Content-Type": "application/json"},
    json={"model": "anthropic/claude-sonnet-4-5", "messages": [...]},
    timeout=90,
)
resp.raise_for_status()
return resp.json()["choices"][0]["message"]["content"].strip()
```

### Page structure
```python
from ui import inject_css, render_sidebar, render_page_header, PALETTE
inject_css()
render_sidebar("publish")  # no dedicated sidebar stage for repurposed content — use publish
render_page_header("publish", "🔁 Repurposed Content", "subtitle")
```

**Note:** The sidebar currently has 5 stages: Transcribe, Develop, Plan, Draft, Publish. Repurposed Content is not a separate sidebar stage — it's either folded into the Publish stage or treated as a sub-step. Check `issues/07-repurposed-content.md` for guidance. If the issue specifies adding a sidebar stage, update `ui.py`'s `STAGES` list.

### Python 3.9 constraint
No `X | Y` union types, no `list[str]` generics. No f-strings with backslash expressions — pre-extract variables before building HTML strings.

### HTML safety
User-generated text in `st.markdown(..., unsafe_allow_html=True)` must be wrapped in `html.escape()`.

### UnboundLocalError pattern
Always initialize variables to `None` before a `try` block that assigns them, then guard after:
```python
result = None
with st.spinner("..."):
    try:
        result = do_thing()
    except Exception as exc:
        st.error(str(exc))
        st.stop()
if result is None:
    st.stop()
```

---

## Design system tokens

| Token | Value |
|---|---|
| Ink (body bg) | `#0d0c14` |
| Sidebar bg | `#1a1826` (no PALETTE key — use hex directly) |
| Mid-ground | `PALETTE["ink_mid"]` → `#2a2838` |
| Gold accent | `PALETTE["gold"]` → `#c9a96e` |
| Gold dim | `PALETTE["gold_dim"]` → `#8a6e42` |
| Text | `PALETTE["text"]` → `#e8e4dc` |
| Muted | `PALETTE["muted"]` → `#9b9690` |
| Done green | `PALETTE["done"]` → `#4a9e6b` |
| Border | `PALETTE["border"]` → `#2e2c3a` |

---

## How to run

```bash
cd "/Users/mazeem147/Claude Code (Personal)/Azeem's Writing Workflow/Code"
.venv/bin/streamlit run app.py --server.port 8502
```

Or use `preview_start` with server name `"Writing Workflow"` (configured in `Code/.claude/launch.json`).

---

## Suggested skills for next session

- **`/implement Issue 07`** — to trigger this same build pattern; read `issues/07-repurposed-content.md` first
- **`/code-review --effort medium`** — run after implementing to catch UnboundLocalError and JSON-parsing patterns
- **`/verify`** — use preview server to confirm Tweet Thread tab + LinkedIn Post tab render correctly and character counts are enforced
