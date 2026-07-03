# Handoff: Azeem's Writing Workflow — ready to build Issue 04

**Session date:** 2026-07-03  
**Next task:** Implement Issue 04 — Voice input (reusable mic component across stages)

---

## What was done this session

### Issue 03 (completed this session)
Full Develop stage implemented in `Code/pages/develop.py`:

- Two-column layout: read-only cleaned transcript (left) | conversation panel (right)
- On entry: Claude generates a Seeder Question from the transcript via OpenRouter (`anthropic/claude-sonnet-4-5`)
- Iterative Q&A loop: user types answer → Claude asks targeted follow-up → repeats indefinitely
- "Build the Plan →" button always visible at bottom; saves `st.session_state.brain_dump` (list of `{"role": "ai"|"user", "text": str}`) and navigates to `pages/plan.py`
- Guard at top: if no `st.session_state.transcript`, shows message + back button, calls `st.stop()`
- Loading spinner during Claude generation
- Two code-review bugs caught and fixed before commit:
  1. `ai_text` potentially unbound → initialized to `None` before try block; append guarded with `if ai_text`
  2. Dead `pending_user_msg` session state key removed

Committed and pushed: commit `8c9db69` on `main`.

---

## Repo layout

```
Azeem's Writing Workflow/
  CONTEXT.md                        ← domain glossary
  PRD.md                            ← full spec and user stories
  issues/
    01-app-scaffold.md              ✅ done
    02-transcribe-stage.md          ✅ done
    03-develop-stage.md             ✅ done
    04-voice-input.md               ← NEXT (full spec below)
    05-plan-stage.md
    06-draft-stage.md
    07-repurposed-content.md
    08-publish-stage.md
  Code/
    app.py                          ← entry point
    ui.py                           ← PALETTE, inject_css(), render_sidebar(), render_page_header()
    pages/
      transcribe.py                 ✅ full implementation
      develop.py                    ✅ full implementation (this session)
      plan.py                       ← placeholder
      draft.py                      ← placeholder
      publish.py                    ← placeholder
    requirements.txt
    .env.example                    ← OPENAI_API_KEY, OPENROUTER_API_KEY
    .env                            ← real keys (not committed)
    .claude/launch.json             ← preview server "Writing Workflow" on port 8502
```

GitHub: https://github.com/mazeem147/azeem-writing-workflow

---

## Issue 04 spec summary

Full spec: `issues/04-voice-input.md`

**What to build:**
A reusable mic component droppable next to any text input. Records from the user's mic, sends audio to Whisper (OpenAI API directly), inserts transcription into the associated text field for review before submission.

**Acceptance criteria:**
- Mic button next to conversation input on Develop stage
- Mic button in section revision modal on Draft stage
- Clicking starts recording → button pulses to show active state
- Clicking again stops recording
- Audio sent to Whisper → transcribed text inserted into the associated field
- User can edit transcribed text before sending
- Handles Urdu/English mixed speech (Whisper multilingual)
- Implemented as a reusable function/component — not duplicated per screen

**Blocked by:** Issue 03 ✅ (now done)

**Key constraint:** Browser-based mic recording requires either a Streamlit custom component or a package like `streamlit-webrtc`. Neither ships with Streamlit by default — the implementation approach needs to be decided at the start of the session. Check `requirements.txt` first to see if anything relevant is already installed.

---

## Patterns to follow

### LLM calls (OpenRouter)
See `_call_claude()` in `Code/pages/develop.py` or `_clean_transcript()` in `Code/pages/transcribe.py`:

```python
import httpx, os
resp = httpx.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
             "Content-Type": "application/json"},
    json={"model": "anthropic/claude-sonnet-4-5", "messages": [...]},
    timeout=60,
)
resp.raise_for_status()
return resp.json()["choices"][0]["message"]["content"].strip()
```

Whisper calls go directly to OpenAI (not OpenRouter) — see `_transcribe_audio()` in `transcribe.py`.

### Page structure
Every page starts with:
```python
from ui import inject_css, render_sidebar, render_page_header, PALETTE
inject_css()
render_sidebar("stage_name")
render_page_header("stage_name", "Icon Title", "subtitle")
```

### Python 3.9 constraint
No `X | Y` union types, no `list[str]` generics — use `List[str]` from `typing` or skip annotations. No f-strings with backslash expressions.

### HTML safety
Any user-generated text in `st.markdown(..., unsafe_allow_html=True)` must be wrapped in `html.escape()` (imported as `_html`).

### No rerun on widget change
Do not call `st.rerun()` inside a widget's change handler. Streamlit's natural rerun on widget commit handles it.

---

## Design system (from `Code/ui.py` `PALETTE` dict)

| Token | Value |
|---|---|
| Ink (body bg) | `#0d0c14` |
| Sidebar bg | `#1a1826` (no PALETTE key — use hex directly) |
| Mid-ground | `#2a2838` → `PALETTE["ink_mid"]` |
| Gold accent | `#c9a96e` → `PALETTE["gold"]` |
| Gold dim | `#8a6e42` → `PALETTE["gold_dim"]` |
| Text | `#e8e4dc` → `PALETTE["text"]` |
| Muted | `#9b9690` → `PALETTE["muted"]` |
| Done green | `#4a9e6b` → `PALETTE["done"]` |
| Border | `#2e2c3a` → `PALETTE["border"]` |

Article/transcript text: Georgia serif. Chrome/UI: system-ui.

---

## How to run

```bash
cd "/Users/mazeem147/Claude Code (Personal)/Azeem's Writing Workflow/Code"
.venv/bin/streamlit run app.py --server.port 8502
```

Or use the `preview_start` tool with server name `"Writing Workflow"` (configured in `Code/.claude/launch.json`).

---

## Suggested skills

- **`/claude-api`** — invoke before writing any Claude prompt or choosing a model to confirm current model IDs.
- **`/code-review --effort low`** — run after implementing to catch runtime-correctness bugs (caught real bugs in Issues 02 and 03).
- **`/verify`** — use the preview server to confirm the mic button renders and recording flow works end-to-end.
