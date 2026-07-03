# Handoff: Azeem's Writing Workflow — ready to build Issue 03

**Session date:** 2026-07-03  
**Next task:** Implement Issue 03 — Develop stage (Seeder Questions + typed conversation)

---

## What was done this session

### Issue 01 (previously complete)
App scaffold, sidebar navigation, design system. See:
- `Code/app.py`
- `Code/ui.py`
- `Code/pages/*.py` (placeholders)

### Issue 02 (completed this session)
Full Transcribe stage: file upload → Whisper transcription → Claude cleaning pass → inline `[word?]` correction UI → "Begin Development Session →" button.

Three code-review bugs were found and fixed before signing off:
1. HTML-injection / XSS in transcript renderer — fixed with `html.escape()` on all plain-text chunks
2. Rerun-per-keystroke in correction inputs — fixed by removing manual `st.rerun()` and relying on widget key sync
3. Stale corrections dict passed to HTML renderer — fixed by rebuilding corrections from widget keys **before** calling `_render_transcript_html`

Key file: `Code/pages/transcribe.py`

---

## Repo layout (no git)

```
Azeem's Writing Workflow/
  CONTEXT.md          ← domain glossary (Trigger, Juice, Capture, Brain Dump, etc.)
  PRD.md              ← full spec, user stories, implementation decisions
  issues/
    01-scaffold.md          ✅ done
    02-transcribe-stage.md  ✅ done
    03-develop-stage.md     ← NEXT
    04-voice-input.md
    05-plan-stage.md
    06-draft-stage.md
    07-repurposed-content.md
    08-publish-stage.md
  Code/
    app.py            ← entry point; load_dotenv() already added
    ui.py             ← PALETTE, inject_css(), render_sidebar(), render_page_header()
    pages/
      transcribe.py   ✅ full implementation
      develop.py      ← placeholder — implement this
      plan.py         ← placeholder
      draft.py        ← placeholder
      publish.py      ← placeholder
    requirements.txt  ← streamlit, openai, httpx, python-dotenv
    .env.example      ← OPENAI_API_KEY, OPENROUTER_API_KEY
    .env              ← real keys (not committed, do not log)
    WORKING_CONTEXT.md ← running build log; update when issue 03 is done
```

---

## Issue 03 spec summary

Full spec: `issues/03-develop-stage.md`

**What to build:**
- Split-panel layout: cleaned transcript (left, read-only) | conversation (right)
- On entry: Claude generates first Seeder Question from the transcript (specific, not templated)
- User types answer → submits with Enter or Send button → Claude asks follow-up
- Repeats for as many rounds as user wants
- "Build the Plan →" button always visible; clicking it stores the full Q&A conversation as `st.session_state.brain_dump` and navigates to `pages/plan.py`
- Loading spinner while Claude is generating
- Full conversation history shown oldest-at-top in the right panel

**Session state consumed:** `st.session_state.transcript` (set by Transcribe stage)  
**Session state produced:** `st.session_state.brain_dump` (list of `{"role": "ai"|"user", "text": str}` dicts, or equivalent structure for Plan stage to consume)

---

## Patterns to follow

### LLM calls (OpenRouter)
All Claude calls go through OpenRouter — see `_clean_transcript()` in `Code/pages/transcribe.py` for the exact pattern:

```python
import httpx, os
resp = httpx.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
             "Content-Type": "application/json"},
    json={"model": "anthropic/claude-sonnet-4-5",
          "messages": [...]},
    timeout=60,
)
resp.raise_for_status()
return resp.json()["choices"][0]["message"]["content"].strip()
```

Use `anthropic/claude-haiku-4-5` for cheap passes; use `anthropic/claude-sonnet-4-5` for Seeder Questions and follow-ups (they need to be good).

### Page structure
Every page starts with:
```python
from ui import inject_css, render_sidebar, render_page_header, PALETTE
inject_css()
render_sidebar("develop")
render_page_header("develop", "💬 Develop", "<subtitle>")
```

### Python 3.9 constraint
No `X | Y` union types, no `list[str]` generics — use `List[str]` from `typing` or skip annotations. No f-strings with backslash expressions.

### HTML safety
Any user-generated text embedded in `st.markdown(..., unsafe_allow_html=True)` must be wrapped in `html.escape()` (import as `_html` to avoid shadowing).

### No rerun on widget change
Do not call `st.rerun()` inside a widget's change handler to refresh display — Streamlit's natural rerun on widget commit handles it. Calling `st.rerun()` per keystroke breaks focus.

---

## Design system

From `Code/ui.py`:

| Token | Value |
|---|---|
| Ink (background) | `#0d0c14` |
| Sidebar | `#1a1826` |
| Mid-ground | `#2a2838` |
| Gold accent | `#c9a96e` |
| Gold dim | `#8a6e42` |
| Text | `#e8e4dc` |
| Muted | `#9b9690` |
| Done (green) | `#4a9e6b` |
| Border | `#2e2c3a` |

Article/transcript text: Georgia serif. Chrome/UI: system-ui.

---

## How to run

Preview server configured in `.claude/launch.json` as `"Writing Workflow"` on port 8502.

```
cd "Azeem's Writing Workflow/Code"
.venv/bin/streamlit run app.py --server.port 8502
```

Or start via the `preview_start` tool with server name `"Writing Workflow"`.

---

## Suggested skills

- **`/claude-api`** — invoke before writing any Claude prompt or choosing a model to confirm current model IDs (names change).
- **`/code-review`** — run at low effort after implementing to catch runtime-correctness bugs. The Issue 02 review caught three real bugs.
- **`/verify`** — use the preview server to confirm the split-panel layout renders and the conversation flow works end-to-end.
